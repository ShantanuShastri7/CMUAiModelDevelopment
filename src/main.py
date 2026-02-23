import argparse
import sys
import os

# Ensure the root directory is in the Python path so 'src' can be resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ingest.ingestor import Ingestor
from src.ingest.arxiv_fetcher import ArxivFetcher
from dotenv import load_dotenv
load_dotenv()

try:
    from src.rag.rag_engine import ResearchRAG
    from src.eval.evaluator import Evaluator
except ImportError:
    # Handle cases where dependencies (like Groq) might miss API keys initially
    pass

def main():
    parser = argparse.ArgumentParser(description="Personal Research Portal (PRP) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Fetch Command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch papers from Arxiv")
    fetch_parser.add_argument("--query", type=str, default="RAG evaluation", help="Search query")
    fetch_parser.add_argument("--max", type=int, default=20, help="Max results")

    # Ingest Command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest papers into Vector Store")

    # Ask Command
    ask_parser = subparsers.add_parser("ask", help="Ask a question to the RAG system")
    ask_parser.add_argument("query", type=str, help="The question to ask")
    ask_parser.add_argument("--no-rerank", action="store_true", help="Disable reranker")

    # Eval Command
    eval_parser = subparsers.add_parser("eval", help="Run evaluation suite")
    eval_parser.add_argument("--no-rerank", action="store_true", help="Disable reranker")

    # UI Command
    ui_parser = subparsers.add_parser("ui", help="Launch the Personal Research Portal frontend UI")

    args = parser.parse_args()

    if args.command == "fetch":
        fetcher = ArxivFetcher()
        fetcher.search_and_download(query=args.query, max_results=args.max)
    
    elif args.command == "ingest":
        ingestor = Ingestor()
        ingestor.run()
        
    elif args.command == "ask":
        try:
            rag = ResearchRAG(use_reranking=not args.no_rerank)
            response = rag.answer(args.query)
            print(f"\nAnswer:\n{response}\n")
        except Exception as e:
            print(f"Error: {e}")
            
    elif args.command == "eval":
        try:
            evaluator = Evaluator(use_reranking=not args.no_rerank)
            evaluator.run_evaluation()
        except Exception as e:
            print(f"Error: {e}")
            
    elif args.command == "ui":
        import os
        print("Launching Personal Research Portal...")
        os.system("streamlit run src/app/app.py")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
