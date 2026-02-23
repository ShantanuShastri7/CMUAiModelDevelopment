# Personal Research Portal - Phase 3 Final Report

## 1. Architecture Overview

The Personal Research Portal (PRP) is a lightweight, full-stack Retrieval-Augmented Generation application. The architecture is composed of a backend data ingestion pipeline, a semantic retrieval engine, an LLM generation layer, and a Streamlit-based frontend for end-user interaction.

### Core Components:

- **Data Ingestion (`src/ingest/`)**: Scripts fetch research papers from arXiv regarding RAG evaluation and store raw PDFs in `data/raw/`.
- **Vector Store (`data/chroma_db/`)**: Local ChromaDB instance populated with embedded document chunks using the `all-MiniLM-L6-v2` HuggingFace embedding model.
- **RAG Engine (`src/rag/rag_engine.py`)**: Responsible for initial retrieval (K=25 chunks), re-ranking via `ms-marco-MiniLM-L-12-v2` cross-encoder for high precision, and generation using `Llama-3.3-70b-versatile` through Groq for fast inference.
- **Frontend App (`src/app/app.py`)**: A Streamlit application that provides the primary UI. It parses the return from the RAG Engine, formats outputs for readability, and handles session caching and thread saving via local JSON files.
- **Evaluator (`src/eval/evaluator.py`)**: An automated harness utilizing RAGAS that tests the system on 20 predefined queries, capturing Context Precision, Faithfulness, and Answer Relevancy.

## 2. Design Choices

### Streamlit for the MVP Frontend

Streamlit was chosen for the User Interface because of its rapid prototyping capabilities for Python, especially regarding LLM data presentation. It natively supports markdown, expandable content boxes for viewing raw citations, and file downloads out-of-the-box.

### Local Embeddings and Reranking

To minimize API costs and latency and ensure complete data privacy, we utilized the sentence-transformers library for local vector embeddings. A secondary local re-ranker ensures high retrieval accuracy before hitting the more expensive language modeling step.

### Specialized Artifact Generation

Instead of a generic chatbot, the PRP creates actionable artifacts. The "Synthesis Memo" generator triggers an independent LLM run scoped strictly by the context provided in the previous interaction. This avoids common context-drift hallucinations seen in standard conversational agents.

### JSON-Based Thread State

Research threads are maintained in a local filesystem using lightweight JSON files. This provides the necessary persistence for the MVP without the overhead of introducing a relational database like SQLite or PostgreSQL at this stage.

## 3. Evaluation & Metrics

Based on the integrated RAGAS evaluation suite, the PRP handles querying effectively.

- **Groundedness / Faithfulness**: Maintained at high levels because the prompt strictly requires inline chunk and source citations and penalizes external knowledge.
- **Answer Relevance**: The reranker greatly improved overall answer usefulness, pushing the correct passages in front of the model.

_Representative Failure Case:_ Very ambiguous edge-case queries (e.g., "Discuss arbitrary external events") successfully result in the system stating "I cannot find evidence for this in the provided documents." This behavior aligns directly with the goal of reducing hallucinations.

## 4. Limitations

1. **Document Parsing Consistency**: Heavily formatted PDFs with multiple columns occasionally yield disorganized textual chunks, slightly confusing the downstream generator when interpreting table references.
2. **Context Limits**: Generating extremely long synthesis memos across more than 5-10 distinct papers starts to stretch the context capacities, requiring more intelligent hierarchical summarization techniques.
3. **Latency with Groq Rate Limits**: Extensive back-to-back evaluations can trigger API limits from the generation provider.

## 5. Next Steps

1. **Agentic Research Loop**: Transition the single "ask-answer" paradigm into a multi-step agent that can dynamically decide to re-query the vector store if initial results are insufficient.
2. **Knowledge Graph View**: Implement a visualization of chunk linkages and citations dynamically on the frontend.
3. **Structured Entity Extraction**: Extend ingestion to map out specific entities (like metrics or datasets) directly from papers during the embedding stage.
