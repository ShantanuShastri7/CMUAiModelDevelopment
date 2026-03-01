# Personal Research Portal (PRP)

## Phase 1: Prompting → RAG Framing

_Completed._ See `report/` for artifacts.

## Quickstart (Phase 3 Product)

Run this from the project root (`Phase 3`) for a reliable local setup.

### 1) Create and activate Python 3.12 environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

Use one of the following:

- `requirements.txt` for normal development install.
- `requirements.lock` for reproducible, pinned installs.

```bash
pip install -r requirements.txt
# or (reproducible)
# pip install -r requirements.lock
```

### 3) Configure environment

Create a `.env` file in project root:

```bash
GROQ_API_KEY=gsk_...
```

### 4) Populate corpus (if needed)

If `data/raw/` and `data/chroma_db/` are not already populated:

```bash
python3 src/main.py fetch
python3 src/main.py ingest
```

### 5) Launch the portal

```bash
python3 src/main.py ui
```

The app will run at `http://localhost:8501`.

## Phase 2: Research-Grade RAG

### Setup

1. Create a `.env` file with your **GROQ_API_KEY**:
   ```bash
   GROQ_API_KEY=gsk_...
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

**1. Fetch Papers (Arxiv):**
Downloads ~20 papers on "RAG evaluation" to `data/raw/` and updates manifest.

```bash
python3 src/main.py fetch
```

**2. Ingest Papers:**
Parses PDFs, chunks them, computes embeddings (using local HuggingFace model), and stores them in ChromaDB.

```bash
python3 src/main.py ingest
```

**3. Ask a Question:**
Retrieves context and answers using Llama3-70b (via Groq).

```bash
python3 src/main.py ask "What are the limitations of Ragas?"
```

**4. Run Evaluation:**
Runs a set of 20 test queries and generates a report in `outputs/eval/`.

```bash
python3 src/main.py eval
```

## Phase 3: Personal Research Portal UI

Launch the Streamlit web application to access the full Personal Research Portal product:

```bash
python3 src/main.py ui
```

This will open a web interface where you can:

- Explore your research queries and retrieve contexts with citations.
- View old chat threads and execution history.
- Generate specialized **Synthesis Memos** as artifacts.
- Explore retrieved evidence via interactive **Knowledge Graph** network visualizations.
- Analyze query answers for missing evidence and suggested search actions using the **Gap Finder**.
- Export your generated artifacts and answers.
- View Evaluation Reports natively in the sidebar.

## Key Technical implementations (Addressing Phase 2 Feedback)

- **Chunking Strategy**: Uses `RecursiveCharacterTextSplitter` with 1000 character chunks and 200 character overlap to preserve semantic context without fragmentation.
- **Reranker Ablation**: Baseline dense retrieval Context Precision was ~0.65. Adding the `ms-marco-MiniLM-L-12-v2` cross-encoder reranker boosted precision to ~0.82.
- **Groundedness Tracking**: Strict prompting mandates inline `(Source, Chunk)` citations, resulting in high Ragas Faithfulness metric scores.
- **API Reliability**: Custom exponential backoff and explicit rate limiting wraps all external API calls (Arxiv fetches and Groq LLM generations) to prevent `429 Too Many Requests` errors.

## Folder Structure

- `data/`: Raw PDFs and ChromaDB storage.
- `src/`: Source code.
  - `ingest/`: Fetching and Ingestion logic.
  - `rag/`: RAG engine (Retriever + Generator).
  - `eval/`: Evaluation scripts.
- `outputs/`: Evaluation reports.
- `report/AI_usage_disclosure.md`: Required AI usage log for submission.
