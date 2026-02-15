import os
import pandas as pd
from src.rag.rag_engine import ResearchRAG
import time
import json
from datetime import datetime

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
                answer = self.rag.answer(query)
                latency = time.time() - start_time
                
                results.append({
                    "query_id": i,
                    "query": query,
                    "answer": answer,
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
        
        # Simple Report
        self.generate_report(results, timestamp)

    def generate_report(self, results, timestamp):
        report_path = os.path.join(self.output_dir, f"eval_report_{timestamp}.md")
        with open(report_path, 'w') as f:
            f.write(f"# Evaluation Report - {timestamp}\n\n")
            f.write(f"**Total Queries:** {len(results)}\n\n")
            f.write("## Results\n\n")
            for res in results:
                f.write(f"### Query {res['query_id']}: {res['query']}\n")
                f.write(f"**Latency:** {res['latency_seconds']}s\n")
                f.write(f"**Answer:**\n{res['answer']}\n\n")
                f.write("---\n")
        print(f"Report generated at {report_path}")

if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.run_evaluation()
