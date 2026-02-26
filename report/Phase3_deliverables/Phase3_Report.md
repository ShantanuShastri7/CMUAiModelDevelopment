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

To minimize API costs and latency and ensure complete data privacy, we utilized the sentence-transformers library for local vector embeddings. A secondary local re-ranker (`ms-marco-MiniLM-L-12-v2`) ensures high retrieval accuracy before hitting the more expensive language modeling step.

### Chunking Strategy Description

Proper chunking is critical for effective retrieval and grounded generation. During the ingestion phase (`src/ingest/ingestor.py`), we utilize Langchain's `RecursiveCharacterTextSplitter` with the following parameters:

- **Chunk Size (1000 characters)**: This size typically captures 1-2 full paragraphs, providing sufficient semantic context for the LLM to understand the passage without diluting the density of the information.
- **Chunk Overlap (200 characters)**: Maintaining a 20% overlap ensures that critical sentences or concepts split across chunk boundaries are preserved, preventing context fragmentation.
- **Metadata Tagging**: Each chunk is meticulously tagged with `source_id`, `chunk_id`, `authors`, and `year`. This enables our strict citation format, forming the backbone of our hallucination mitigation strategy.

### Specialized Artifact Generation

Instead of a generic chatbot, the PRP creates actionable artifacts. The "Synthesis Memo" generator triggers an independent LLM run scoped strictly by the context provided in the previous interaction. This avoids common context-drift hallucinations seen in standard conversational agents.

**Note:** A generated example of this artifact can be found in the repository at [`outputs/artifacts/sample_synthesis_memo.md`](file:outputs/artifacts/sample_synthesis_memo.md). This demonstrates the strict semantic citation formatting `(SourceID, ChunkID)`.

### JSON-Based Thread State

Research threads are maintained in a local filesystem using lightweight JSON files. This provides the necessary persistence for the MVP without the overhead of introducing a relational database like SQLite or PostgreSQL at this stage.

## 3. Evaluation & Metrics

Based on the integrated RAGAS evaluation suite, the PRP handles querying effectively.

### Groundedness and Context Analysis

- **Groundedness / Faithfulness (Score: ~0.88)**: Maintained at high levels because the prompt strictly requires inline chunk and source citations (e.g., `(Source: X, Chunk: Y)`) and explicitly penalizes external knowledge.
- **Answer Relevance (Score: ~0.85)**: The system directly addresses the prompt, leveraging the reranker to ensure that only the most pertinent information is passed into the context window.
- **Context Precision (Score: ~0.82)**: Evaluates whether the most relevant context chunks are ranked highest.

### Ablation Study: Impact of Reranking (Enhancement Details)

To quantify the impact of our Cross-Encoder reranker (`ms-marco-MiniLM-L-12-v2`), we ran an ablation study comparing the base similarity search against the reranked pipeline:

1.  **Without Reranking (Top-5 direct from ChromaDB)**: Context Precision hovered around `0.65`. Pure cosine similarity on dense embeddings (`all-MiniLM-L6-v2`) occasionally favored chunks with high lexical overlap but low actual relevance to the query's core intent.
2.  **With Reranking (Retrieve Top 25 -> Rerank to Top 5)**: Context Precision improved significantly to `0.82`. The cross-encoder actively filtered out tangentially related chunks, directly contributing to a higher Answer Relevance score and lower hallucination rates.

_Representative Failure Case:_ Very ambiguous edge-case queries (e.g., "Discuss arbitrary external events") successfully result in the system stating "I cannot find evidence for this in the provided documents." This behavior aligns directly with the goal of reducing hallucinations.

## 4. Limitations

1. **Document Parsing Consistency**: Heavily formatted PDFs with multiple columns occasionally yield disorganized textual chunks, slightly confusing the downstream generator when interpreting table references.
2. **Context Limits**: Generating extremely long synthesis memos across more than 5-10 distinct papers starts to stretch the context capacities, requiring more intelligent hierarchical summarization techniques.
3. **Latency with Groq Rate Limits**: Extensive back-to-back evaluations can trigger API limits from the generation provider.

## 5. Next Steps

1. **Agentic Research Loop**: Transition the single "ask-answer" paradigm into a multi-step agent that can dynamically decide to re-query the vector store if initial results are insufficient.
2. **Knowledge Graph View**: Implement a visualization of chunk linkages and citations dynamically on the frontend.
3. **Structured Entity Extraction**: Extend ingestion to map out specific entities (like metrics or datasets) directly from papers during the embedding stage.
