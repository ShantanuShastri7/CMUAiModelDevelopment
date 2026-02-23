# Personal Research Portal (PRP)

## Phase 1: Prompting → RAG Framing

_Completed._ See `report/` for artifacts.

## Phase 2: Research-Grade RAG (Current)

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
- Export your generated artifacts and answers.
- View Evaluation Reports natively in the sidebar.

## Folder Structure

- `data/`: Raw PDFs and ChromaDB storage.
- `src/`: Source code.
  - `ingest/`: Fetching and Ingestion logic.
  - `rag/`: RAG engine (Retriever + Generator).
  - `eval/`: Evaluation scripts.
- `outputs/`: Evaluation reports.
