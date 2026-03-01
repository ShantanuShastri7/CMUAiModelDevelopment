# AI Usage Disclosure (Required)

## Project
Personal Research Portal (PRP) - Phases 1, 2, and 3

## Student Responsibility Statement
AI tools were used for acceleration and drafting support only. I verified outputs, corrected issues, and made manual decisions about architecture, retrieval behavior, citations, and final deliverables. I am responsible for correctness, citation traceability, and assignment compliance.

## Tool Log

| Tool | What it was used for | What was changed manually afterward |
|---|---|---|
| Cursor AI Assistant / Agent | Code navigation, debugging support, and implementation assistance for Streamlit UI, RAG flow, and exports. | Manually reviewed generated code paths, validated run commands locally, and corrected environment setup details (Python 3.12 venv path and execution flow). |
| LLM chat assistance (prompting support) | Refining wording for report sections and prompt formatting ideas. | Rewrote final report text to match actual implementation details and removed unsupported claims where needed. |
| AI coding suggestions inside editor | Fast drafting of helper functions and boilerplate for parsing, retrieval display, and evaluation plumbing. | Manually tested each affected feature (ask flow, citations display, thread save/load, eval page) and adjusted logic based on observed runtime behavior. |

## Areas Where AI Was Used

1. **Documentation drafting support**
   - Initial outlines for README structure and report phrasing.
   - Final README and report sections were manually aligned with the actual commands and files in this repository.

2. **Implementation acceleration**
   - Drafting utility code and UI scaffolding in the Streamlit app.
   - Manual review ensured exports, citation display, and thread persistence matched project requirements.

3. **Debugging and environment triage**
   - Identifying compatibility issues and suggesting remediation steps.
   - Manual reproduction and validation were done in local terminal before accepting fixes.

## Manual Validation Performed

- Ran project commands locally from project root:
  - `python3 src/main.py fetch`
  - `python3 src/main.py ingest`
  - `python3 src/main.py ui`
  - `python3 src/main.py eval`
- Verified that:
  - answers include inline citations tied to retrieved chunks,
  - history files are written under `outputs/history/`,
  - evaluation outputs are generated under `outputs/eval/`,
  - artifact output is generated and exportable.

## Integrity Notes

- AI suggestions were treated as drafts, not final truth.
- Any misleading or unverifiable AI-generated statements were revised or removed during manual review.
- Final submission artifacts reflect the implemented system behavior in this repository.
