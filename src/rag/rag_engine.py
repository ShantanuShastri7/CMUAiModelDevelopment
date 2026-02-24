import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from flashrank import Ranker, RerankRequest
import json
from datetime import datetime
import time
from functools import wraps

def retry_with_backoff(retries=5, backoff_in_seconds=2):
    """
    Decorator to retry an API call with exponential backoff.
    Useful for handling API rate limits (e.g., HTTP 429) and transient errors.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        print(f"Failed after {retries} retries.")
                        raise e
                    sleep_time = backoff_in_seconds * (2 ** x)
                    print(f"API Error: {e}. Retrying in {sleep_time} seconds (Attempt {x+1}/{retries})...")
                    time.sleep(sleep_time)
                    x += 1
        return wrapper
    return decorator

class ResearchRAG:
    def __init__(self, persist_directory="./data/chroma_db", use_reranking=True):
        self.use_reranking = use_reranking 
        # Initialize Embeddings (Local)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="rag_evaluation_corpus"
        )
        # Retrieve more candidates for reranking
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 25} 
        )

        # Initialize Reranker (Local)
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./data/models")

        # Initialize LLM (Groq)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
            
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile", # High quality model
            api_key=api_key
        )

        # Define Prompt
        self.template = """You are a research assistant. Use the following pieces of retrieved context to answer the question.
        
        Rules:
        1. If the answer is not in the context, say "I cannot find evidence for this in the provided documents."
        2. Cite your sources using the format (SourceID, ChunkID) at the end of every claim.
        3. Do not use outside knowledge.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
        
        self.prompt = ChatPromptTemplate.from_template(self.template)

    def _format_docs(self, docs):
        formatted = []
        for doc in docs:
            source = f"(Source: {doc.metadata.get('source_id', 'Unknown')}, Chunk: {doc.metadata.get('chunk_id', 'Unknown')})"
            content = doc.page_content.replace('\n', ' ')
            formatted.append(f"{content} {source}")
        return "\n\n".join(formatted)

    def search(self, query, k=5):
        """Returns raw retrieved documents after reranking."""
        # 1. Initial Retrieval
        initial_docs = self.vector_store.similarity_search(query, k=25)
        
        # 2. Reranking
        passages = [
            {"id": d.metadata.get("chunk_id"), "text": d.page_content, "meta": d.metadata}
            for d in initial_docs
        ]
        
        rerank_request = RerankRequest(query=query, passages=passages)
        
        if self.use_reranking:
            results = self.ranker.rerank(rerank_request)
        else:
            # Fake rerank results (pass-through)
            results = []
            for i, p in enumerate(passages):
                results.append({"text": p["text"], "meta": p["meta"], "score": 0.0}) # Dummy score
        
        # 3. Format back to Documents
        reranked_docs = []
        for res in results[:k]:
            meta = res['meta']
            meta['rerank_score'] = res['score']
            doc = Document(page_content=res['text'], metadata=meta)
            reranked_docs.append(doc)
            
        return reranked_docs

    @retry_with_backoff(retries=5, backoff_in_seconds=2)
    def answer(self, query, return_docs=False):
        """Generates an answer using the RAG pipeline."""
        start_timestamp = datetime.now().isoformat()
        
        # Retrieve and Rerank
        docs = self.search(query, k=5)
        
        # Generate
        formatted_context = self._format_docs(docs)
        chain = self.prompt | self.llm | StrOutputParser()
        
        answer = chain.invoke({"context": formatted_context, "question": query})
        
        # Log interaction
        self._log_interaction(query, docs, answer, start_timestamp)
        
        if return_docs:
            return answer, docs
        return answer

    @retry_with_backoff(retries=3, backoff_in_seconds=3)
    def generate_synthesis_memo(self, query, answer, docs):
        """Generates a Synthesis Memo artifact based on the query, answer, and retrieved documents."""
        memo_template = """You are a research assistant tasked with writing a Synthesis Memo.
        
        Write an 800-1200 word Synthesis Memo addressing the following research query based on the provided context.
        Use inline citations in the format (SourceID, ChunkID).
        Include a 'References' section at the end listing the unique sources used.
        If the evidence is conflicting or insufficient, explicitly state so.
        Format the output in clear Markdown.
        
        Query: {query}
        Previous Brief Answer: {answer}
        
        Context evidence:
        {context}
        
        Synthesis Memo Output:"""
        
        memo_prompt = ChatPromptTemplate.from_template(memo_template)
        formatted_context = self._format_docs(docs)
        
        chain = memo_prompt | self.llm | StrOutputParser()
        memo = chain.invoke({
            "query": query,
            "answer": answer,
            "context": formatted_context
        })
        return memo

    @retry_with_backoff(retries=3, backoff_in_seconds=3)
    def extract_knowledge_graph(self, query, docs):
        """Extracts entities and relationships for a knowledge graph based on retrieved documents."""
        prompt_template = """You are an advanced text analysis system tasked with building a knowledge graph.
        
        Analyze the following retrieved context documents against the user query. Extract key concepts/entities and the relationships between them.
        Ensure you include the 'SourceID' in the extraction when an entity is derived from a specific document.
        
        Output your findings STRICTLY as a JSON object with two lists: 'nodes' and 'edges'.
        - 'nodes' should have objects with 'id' (name of concept), 'label' (name of concept), and 'group' (e.g., 'Concept', 'Source', 'Metric').
        - 'edges' should have objects with 'source' (node id), 'target' (node id), and 'label' (describing the relationship).
        
        Do not include any other text except the JSON object.
        
        Query: {query}
        
        Context:
        {context}
        """
        
        formatted_context = self._format_docs(docs)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # We enforce JSON output strictly
        chain = prompt | self.llm | StrOutputParser()
        raw_output = chain.invoke({"query": query, "context": formatted_context})
        
        try:
            # Clean up potential markdown formatting from LLM
            if "```json" in raw_output:
                raw_output = raw_output.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_output:
                raw_output = raw_output.split("```")[1].strip()
            return json.loads(raw_output)
        except Exception as e:
            print(f"Failed to parse Knowledge Graph JSON: {e}")
            return {"nodes": [], "edges": []}

    @retry_with_backoff(retries=3, backoff_in_seconds=3)
    def find_evidence_gaps(self, query, answer, docs):
        """Identifies missing information from the answer and suggests new search queries."""
        prompt_template = """You are a critical research assistant evaluating a provided answer against its source evidence.
        
        Read the User Query, the final Answer, and the Provided Context. 
        Identify what crucial aspects of the query remain unanswered or lack sufficient evidence in the context.
        Then, suggest 2 or 3 highly specific, distinct follow-up search queries that could help retrieve the missing evidence.
        
        Output your findings STRICTLY as a JSON object with two keys:
        - 'missing_evidence': A short string summarizing what is missing or weak.
        - 'next_queries': A list of strings containing exactly 2 or 3 suggested search queries.
        
        Do not include any other text except the JSON object.
        
        Query: {query}
        Answer: {answer}
        
        Context:
        {context}
        """
        
        formatted_context = self._format_docs(docs)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        chain = prompt | self.llm | StrOutputParser()
        raw_output = chain.invoke({"query": query, "answer": answer, "context": formatted_context})
        
        try:
             # Clean up potential markdown formatting from LLM
            if "```json" in raw_output:
                raw_output = raw_output.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_output:
                raw_output = raw_output.split("```")[1].strip()
            return json.loads(raw_output)
        except Exception as e:
            print(f"Failed to parse Gap Finder JSON: {e}")
            return {"missing_evidence": "Failed to extract missing evidence.", "next_queries": []}

    def _log_interaction(self, query, docs, answer, timestamp):
        log_entry = {
            "timestamp": timestamp,
            "query": query,
            "retrieved_chunks": [d.metadata.get("chunk_id") for d in docs],
            "answer": answer,
            "model": self.llm.model_name
        }
        
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, "rag_interactions.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    # Test run
    # from dotenv import load_dotenv
    # load_dotenv()
    try:
        rag = ResearchRAG()
        response = rag.answer("What are the main failure modes of RAG evaluation?")
        print(response)
    except Exception as e:
        print(f"Error: {e}")
