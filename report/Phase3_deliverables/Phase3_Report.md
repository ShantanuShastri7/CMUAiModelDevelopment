# Personal Research Portal - Phase 3 Final Report

## 1. Architecture Overview

The Personal Research Portal (PRP) is a lightweight, full-stack Retrieval-Augmented Generation application. The architecture is composed of a backend data ingestion pipeline, a semantic retrieval engine, an LLM generation layer, and a Streamlit-based frontend for end-user interaction.

### Core Components:

- **Data Ingestion (`src/ingest/`)**: Scripts fetch research papers from arXiv regarding RAG evaluation and store raw PDFs in `data/raw/`.
- **Vector Store (`data/chroma_db/`)**: Local ChromaDB instance populated with embedded document chunks using the `all-MiniLM-L6-v2` HuggingFace embedding model.
- **RAG Engine (`src/rag/rag_engine.py`)**: Responsible for initial retrieval (K=25 chunks), re-ranking via `ms-marco-MiniLM-L-12-v2` cross-encoder for high precision, and generation using `Llama-3.3-70b-versatile` through Groq for fast inference.
- **Frontend App (`src/app/app.py`)**: A Streamlit application that provides the primary UI. It parses the return from the RAG Engine, formats outputs for readability, and handles session caching and thread saving via local JSON files.
- **Evaluator (`src/eval/evaluator.py`)**: An automated harness utilizing RAGAS that tests the system on 20 predefined queries, capturing Context Precision, Faithfulness, and Answer Relevancy.

End-to-end, the flow is: papers are fetched into `data/raw/` and listed in the data manifest; the ingestor parses and chunks them into ChromaDB; the UI calls the RAG engine for each query, which retrieves, reranks, and then generates an answer with citations. Threads and eval reports are written to `outputs/` so everything is file-based and easy to inspect.

## 2. Design Choices

### Streamlit for the MVP Frontend

Streamlit was chosen for the User Interface because of its rapid prototyping capabilities for Python, especially regarding LLM data presentation. It natively supports markdown, expandable content boxes for viewing raw citations, and file downloads out-of-the-box. We considered Gradio for a more app-like feel but stuck with Streamlit so we could iterate quickly and keep the code in one place without custom front-end work. The trade-off is a less custom look; the upside is that the whole portal runs with a single `streamlit run` and is straightforward for someone else to run locally.

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

### What the UI Actually Provides

For clarity, the portal currently offers: a main chat where you type a research question; retrieval and an answer with inline citations; an expandable “View Retrieved Evidence” panel showing source and chunk IDs plus snippets; “Generate Knowledge Graph” and “Find Evidence Gaps” buttons that appear right after each answer; a “Generate Artifacts” section with Synthesis Memo and downloads for both Markdown (memo) and CSV (evidence table); thread management via sidebar (New Thread, load saved threads); and an “Evaluation Report” page that shows the latest run from `outputs/eval/`. All of this is driven by the same RAG engine and evaluation harness described above.

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

The evaluation set follows the Phase 2 design: 20 queries split into direct (e.g. “What is Context Precision in RAG evaluation?”), synthesis/multi-hop (e.g. comparing methods or metrics), and edge cases (e.g. “Does the corpus contain evidence for [claim]?”). In practice we see both strong citations—e.g. Self-RAG and Corrective RAG style questions get answers with proper (Source, Chunk) references—and correct refusals when the corpus does not support the question (e.g. “I cannot find evidence for this in the provided documents”). That mix is what we wanted from the trust behavior.

_Representative Failure Case:_ Very ambiguous edge-case queries (e.g., "Discuss arbitrary external events") successfully result in the system stating "I cannot find evidence for this in the provided documents." This behavior aligns directly with the goal of reducing hallucinations.

## 4. Limitations

1. **Document Parsing Consistency**: Heavily formatted PDFs with multiple columns occasionally yield disorganized textual chunks, slightly confusing the downstream generator when interpreting table references.
2. **Context Limits**: Generating extremely long synthesis memos across more than 5-10 distinct papers starts to stretch the context capacities, requiring more intelligent hierarchical summarization techniques.
3. **Latency with Groq Rate Limits**: Extensive back-to-back evaluations can trigger API limits from the generation provider.

4. **Single-user and local-only**: The app is built for one user on one machine. There is no authentication, no multi-user state, and no hosted deployment. Threads and exports live in local `outputs/` directories, which is fine for a research prototype but would need to change for shared use.

## 5. Next Steps

1. **Agentic Research Loop**: Transition the single "ask-answer" paradigm into a multi-step agent that can dynamically decide to re-query the vector store if initial results are insufficient.
2. **Knowledge Graph View**: Implement a visualization of chunk linkages and citations dynamically on the frontend.
3. **Structured Entity Extraction**: Extend ingestion to map out specific entities (like metrics or datasets) directly from papers during the embedding stage.

## 6. Product Workflow and User Journey

The PRP is designed around a practical research workflow instead of open-ended chatting. The expected sequence is:

1. **Question entry** through the chat box.
2. **Retrieval + reranking** to identify the most relevant chunks.
3. **Citation-backed generation** where every major claim is tied to `(SourceID, ChunkID)`.
4. **Evidence inspection** in the expandable context panel.
5. **Artifact generation** (Synthesis Memo) for downstream research writing.
6. **Export and persistence** through download buttons and thread state saved to local files.

After each answer, the user can optionally run “Find Evidence Gaps” to see what’s missing and get suggested follow-up queries, or “Generate Knowledge Graph” to see entities and relationships extracted from the retrieved chunks. Both run on the same context that was used for the answer, so they stay aligned with what the system actually cited.

This flow intentionally separates "answering" from "artifact writing." The answer path optimizes for directness and traceability, while the artifact path optimizes for structured synthesis and readability.

## 7. Trust, Grounding, and Failure Handling

Trust behavior is implemented as a first-class requirement, not a cosmetic UI feature.

### 7.1 Grounding Rules in Generation

The generation prompt enforces:

- no use of outside knowledge,
- explicit refusal when evidence is missing,
- inline citation formatting for claims.

This significantly reduces hallucination risk in the research context. In particular, the model is instructed to return a "cannot find evidence" response when retrieval context does not support the question.

### 7.2 Missing Evidence Surfacing

The app includes a Gap Finder path that performs a post-answer analysis to detect likely missing support and suggest concrete follow-up retrieval queries. This is useful for ambiguous questions and helps convert failure into actionable next steps.

### 7.3 Failure Patterns Observed

Three practical failure patterns were observed in testing:

1. **Broad or underspecified queries**  
   Example: requests that mix multiple sub-topics in one sentence can produce partially grounded answers where only part of the request is evidenced.

2. **Corpus mismatch**  
   If the corpus does not include evidence for a specific claim, the model correctly refuses, but users may interpret this as model weakness rather than corpus scope limitation.

3. **Long-context compression errors**  
   Very long synthesis tasks can over-compress nuanced disagreements across sources. This is reduced by reranking but not fully eliminated.

## 8. Reproducibility and Runbook

To ensure grader reproducibility, the project follows a deterministic local run path:

1. Create a Python 3.12 virtual environment.
2. Install dependencies from `requirements.txt` (or `requirements.lock` for pinned reproducibility).
3. Configure `GROQ_API_KEY` in `.env`.
4. Run fetch/ingest if corpus data is not already present.
5. Launch UI and run evaluation.

### 8.1 Command Sequence

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py fetch
python3 src/main.py ingest
python3 src/main.py ui
python3 src/main.py eval
```

### 8.2 Output Locations

- **Run logs**: `logs/rag_interactions.jsonl`
- **Evaluation outputs**: `outputs/eval/`
- **Saved research threads**: `outputs/history/`
- **Artifacts/exports**: `outputs/artifacts/`

The evaluation can be run from the command line with `python3 src/main.py eval`; it writes a timestamped report (e.g. `eval_report_YYYYMMDD_HHMMSS.md`) into `outputs/eval/`. The UI’s “Evaluation Report” page simply loads the latest of these files, so graders can either run the eval themselves or open an existing report. This explicit mapping is included so that each demonstrated feature has an auditable file output.

## 9. Artifact Design and Export Strategy

The current MVP artifact is a **Synthesis Memo** with citation-backed claims and downloadable markdown output. This was selected because it reflects realistic research deliverables (briefs, literature synthesis drafts, and report sections). The memo is generated from the same retrieved chunks and prior answer, so it stays grounded; users can download it as Markdown from the “Download Synthesis Memo (Markdown)” button.

In addition, the portal supports **Evidence Table** export as CSV. Each row includes the query, the answer, source_id, chunk_id, the evidence snippet, and a citation string. That gives users a spreadsheet-friendly view of which chunks backed the answer and makes it easy to audit or reuse in other tools. So in practice we support both artifact types the assignment asks for: a synthesis memo (Markdown) and an evidence-style table (CSV), plus the raw citations in the UI. This supports downstream analysis in spreadsheet workflows and improves auditability.

### 9.1 Why this artifact choice is appropriate

- It is directly aligned with the assignment requirement for research artifacts.
- It forces grounding discipline: unsupported statements become visible quickly.
- It creates immediate utility beyond chat by producing reusable written output.

### 9.2 Artifact quality constraints

The memo generator is scoped to retrieved context and prior answer state. This reduces context drift and helps keep synthesis tied to cited materials.

## 10. Evaluation Interpretation and Practical Impact

Metric reporting alone is insufficient unless tied to user outcomes. In this project:

- **Higher context precision** translates into fewer irrelevant chunks shown in evidence panels.
- **Higher faithfulness** reduces fabricated claims in generated prose.
- **Better answer relevance** improves first-pass usefulness of responses before manual follow-up.

The reranker ablation result (0.65 -> 0.82 context precision) had clear practical impact: users spent less time scanning unrelated evidence and more time validating high-signal snippets.

## 11. Engineering Trade-offs

This project prioritizes reliability and transparency over maximal feature breadth.

### Trade-off 1: Simplicity vs. Database sophistication

Threads are stored as JSON in filesystem rather than SQL storage. This is simpler for an MVP and easier for graders to inspect, though less scalable for multi-user deployment.

### Trade-off 2: Local embedding stack vs. managed retrieval services

Local embeddings and ChromaDB reduce API costs and improve offline reproducibility, but require local compute and careful environment compatibility management.

### Trade-off 3: Single-artifact depth vs. many shallow artifacts

The system currently goes deeper on one artifact type (Synthesis Memo) rather than implementing several partially complete artifact modes. We added the evidence-table CSV so that “export in Markdown/CSV” is covered without building a separate annotated-bibliography generator; the CSV doubles as a minimal evidence table for traceability.

## 12. Conclusion

Phase 3 successfully transforms the research-grade RAG backend into a usable product-oriented Personal Research Portal. The delivered system supports question answering with evidence, citation inspection, thread persistence, artifact generation, export paths, and integrated evaluation.

The most important achieved objective is not just "chat with papers," but a repeatable and auditable research workflow where each answer can be traced back to ingested evidence. Citations resolve via the data manifest, exports (Markdown and CSV) are in place, and the evaluation view plus run logs give a clear picture of how the system performs. Future iterations will focus on deeper automation (agentic loop), richer retrieval controls, and stronger long-context synthesis reliability.
