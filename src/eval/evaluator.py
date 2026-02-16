import os
import pandas as pd
from src.rag.rag_engine import ResearchRAG
import time
import json
from datetime import datetime
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
)

class Evaluator:
    def __init__(self, output_dir="outputs/eval", use_reranking=True):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.rag = ResearchRAG(use_reranking=use_reranking)

        # Define 20 Test Queries (MVP)
        self.test_queries = [
            # Direct Questions
            "What is 'Context Precision' in RAG evaluation?",
            "How does Ragas measure faithfulness?",
            "What are the limitations of LLM-as-a-judge?",
            "Define 'Groundness' in the context of RAG.",
            "What is 'Self-RAG' and how does it work?",
            "How does 'Corrective RAG' improve retrieval?",
            "What metrics are used to evaluate retrieval quality?",
            "Explain the concept of 'Hit Rate'.",
            "What is the difference between sparse and dense retrieval?",
            "How does chunk size affect RAG performance?",
            
            # Synthesis Questions
            "Compare Ragas and TruLens evaluation frameworks.",
            "What are the common failure modes of RAG systems according to recent research?",
            "How can we mitigate hallucinations in RAG?",
            "Discuss the trade-offs between latency and accuracy in RAG.",
            "Summarize the state-of-the-art in reference-free RAG evaluation.",

            # Edge Cases / Ambiguous
            "Does the corpus mention 'Quantum RAG'?", # Likely no
            "Who won the 2024 US Election?", # Out of domain
            "What is the capital of France?", # Out of domain
            "Explain 'Model Collapse' in RAG.", # Maybe mentioned?
            "Is there evidence for using GraphRAG for evaluation?"
        ]

    def run_evaluation(self):
        results = []
        print(f"Starting evaluation on {len(self.test_queries)} queries...")
        
        for i, query in enumerate(self.test_queries):
            print(f"[{i+1}/{len(self.test_queries)}] Query: {query}")
            start_time = time.time()
            try:
                # We need to update rag.answer to return context! 
                # Or we call search() then _format() then generate.
                # Let's assume we modify rag.answer to return (answer, context_docs)
                # But rag.answer currently returns string. 
                # Let's modify rag.answer first.
                
                # Temporary fix: re-retrieve to get context for Ragas
                docs = self.rag.search(query, k=5)
                context_text = [d.page_content for d in docs]
                
                answer = self.rag.answer(query)
                latency = time.time() - start_time
                
                results.append({
                    "query_id": i,
                    "query": query,
                    "answer": answer,
                    "contexts": context_text, # Added for Ragas
                    "latency_seconds": round(latency, 2),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error processing query '{query}': {e}")
                results.append({
                    "query_id": i,
                    "query": query,
                    "answer": f"ERROR: {str(e)}",
                    "latency_seconds": 0,
                    "timestamp": datetime.now().isoformat()
                })

        # Save Results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_run_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"Evaluation complete. Results saved to {filepath}")

        # Run RAGAS Evaluation
        print("Running RAGAS evaluation (this may take a while)...")
        ragas_results = self.evaluate_with_ragas(results)
        
        # Save RAGAS Results
        ragas_filename = f"eval_run_ragas_{timestamp}.json"
        ragas_filepath = os.path.join(self.output_dir, ragas_filename)
        with open(ragas_filepath, 'w') as f:
            json.dump(ragas_results, f, indent=4)
        print(f"RAGAS evaluation complete. Results saved to {ragas_filepath}")
        
        # Simple Report
        self.generate_report(results, ragas_results, timestamp)

    def evaluate_with_ragas(self, results):
        """
        Runs RAGAS metrics on the evaluation results.
        """
        # Prepare data for RAGAS
        data = {
            "question": [],
            "answer": [],
            "contexts": [],
            "ground_truth": [] # Optional, leaving empty for now
        }
        
        for res in results:
            data["question"].append(res["query"])
            data["answer"].append(res["answer"])
            # Extract contexts from the rag engine logs if available, 
            # or we need to modify answer() to return context.
            # For now, we'll assume we haven't stored context in results.
            # EDIT: We need context! Let's update run_evaluation to capture it.
            data["contexts"].append(res.get("contexts", [])) 
            data["ground_truth"].append("N/A")

        dataset = Dataset.from_dict(data)
        
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
        ]
        
        # We need to ensure the LLM/Embeddings are passed to Ragas if not using OpenAI default
        # Ragas uses OpenAI by default. 
        # For this implementation, we will rely on the environment variable OPENAI_API_KEY being set
        # OR we need to wrap our Groq/Local embeddings for Ragas.
        # Since Ragas supports LangChain embeddings/LLMs, we can reuse ours?
        # Actually Ragas v0.1+ handles this differently.
        # For simplicity in this MVP, we will try to run it. 
        # Note: If no OpenAI key, this might fail. We should wrap in try-except.
        
        try:
            # Wrap LangChain LLM and Embeddings for Ragas
            # Configure RunConfig to avoid Rate Limits (Groq has tight limits)
            from ragas.run_config import RunConfig
            
            run_config = RunConfig(
                max_workers=1, # Sequential execution to avoid 429
                timeout=60,
                max_retries=10,
                max_wait=60
            )
            
            # Need to disable parallelism in Ragas for Groq
            results = evaluate(
                dataset=dataset, 
                metrics=metrics,
                llm=self.rag.llm,
                embeddings=self.rag.embeddings,
                run_config=run_config
            )
            return results
        except Exception as e:
            print(f"RAGAS Evaluation failed: {e}")
            return {}

    def generate_report(self, results, ragas_results, timestamp):
        report_path = os.path.join(self.output_dir, f"eval_report_{timestamp}.md")
        with open(report_path, 'w') as f:
            f.write(f"# Evaluation Report - {timestamp}\n\n")
            f.write(f"**Total Queries:** {len(results)}\n")
            if ragas_results:
                f.write(f"**RAGAS Scores:** {ragas_results}\n\n")
            else:
                f.write("\n")
            f.write("## Results\n\n")
            for res in results:
                f.write(f"### Query {res['query_id']}: {res['query']}\n")
                f.write(f"**Latency:** {res['latency_seconds']}s\n")
                f.write(f"**Answer:**\n{res['answer']}\n")
                f.write(f"**Contexts Retrieved:** {len(res.get('contexts', []))}\n\n")
                f.write("---\n")
        print(f"Report generated at {report_path}")

if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.run_evaluation()
