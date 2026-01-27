# CMU AI Model Development - Personal Research Portal (PRP)

This repository contains the Personal Research Portal project, divided into three phases:

- **Phase 1**: Prompting → RAG Framing
- **Phase 2**: RAG Implementation
- **Phase 3**: Research Portal Product

## Folder Structure

- `data/`
  - `raw/`: Store raw PDFs, HTML snapshots, and notes here.
  - `processed/`: Store parsed text, chunks, and intermediate files.
  - `data_manifest.csv`: Metadata registry for all sources.
- `src/`
  - `app/`: Phase 3 UI (Streamlit/Gradio).
  - `ingest/`: Scripts for parsing and chunking.
  - `rag/`: Retrieval and generation logic.
  - `eval/`: Evaluation scripts and query sets.
- `outputs/`: Generated artifacts (evidence tables, memos) and exports.
- `logs/`: Run logs (machine-readable).
- `report/`: Deliverable documents.
  - `phase1_framing_brief.md`: Frame the research domain and questions.
  - `phase1_prompt_kit.md`: Document prompts and guardrails.
  - `phase1_evaluation_sheet.md`: Log and score Phase 1 test runs.
  - `phase1_analysis_memo.md`: Analyze failure modes and plan for Phase 2.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your API keys (e.g., in `.env` or environment variables).

## Phase 1 Checklist

- [ ] Complete `report/phase1_framing_brief.md`
- [ ] Add raw documents to `data/raw/` and update `data/data_manifest.csv`
- [ ] Design prompts in `report/phase1_prompt_kit.md`
- [ ] Run evaluation and record in `report/phase1_evaluation_sheet.md`
- [ ] Write analysis in `report/phase1_analysis_memo.md`
