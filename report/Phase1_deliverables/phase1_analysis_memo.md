# Analysis Memo: Task 1 (Paper Triage)

### Overview
In Task 1, we evaluated the ability of two models (**ChatGPT GPT-5.2 Auto** and **Gemini 3 Pro**) to extract structured research summaries (Triage) from technical papers. The experiment compared a **Baseline Prompt (Prompt A)** against an **Advanced "Systems Architect" Prompt (Prompt B)** designed to force JSON formatting and specific citation evidence.

### 1. Pattern: Format Compliance & Operational Readiness
A critical "Operational" failure mode was observed in the Baseline prompt runs.
* **Gemini 3 Pro (Run 7):** Provided excellent technical depth but failed to produce the machine-readable output required for Phase 2, returning unstructured text instead of JSON.
* **ChatGPT (Run 1):** Surprisingly produced JSON even with the Baseline prompt, but the content lacked specific detail.

> **Takeaway:** Reliability is model-dependent. We cannot rely on model "intelligence" alone for formatting; **Prompt B is strictly necessary** to guarantee the valid JSON schema required for the Phase 2 ingestion pipeline, ensuring we don't need manual data entry.

### 2. Failure Mode: The "Citation Gap" in ChatGPT
The most distinct differentiator between the models was their adherence to the Citation Constraint in Prompt B.

| Model | Performance | Analysis |
| :--- | :--- | :--- |
| **ChatGPT** | **Failure** (Runs 2 & 6) | Followed JSON structure but struggled to rigorously apply the citation constraint. Failed to attach specific quotes, resulting in a score of 3.5. |
| **Gemini 3 Pro** | **Success** (Runs 4 & 8) | Demonstrated perfect adherence, correctly appending bracketed citations and direct quotes. |

> **Implication:** For Phase 2, **Gemini 3 Pro** appears to be the superior "Extractor" agent when strict evidence traceability is required. If we use ChatGPT, we will need to implement a "Retry/Correction" loop to force citations.

### 3. Pattern: Technical Nuance vs. Generalization
We observed a "Depth vs. Breadth" trade-off.
* **ChatGPT:** Tended to summarize findings into general high-level statements (e.g., Run 5 omitted "beam search").
* **Gemini 3 Pro:** Particularly with Prompt B, successfully extracted specific technical nuances (e.g., "FactScore" comparisons in Run 8 and "Inference Beam Search" in Run 7).

> **Design Choice:** The Advanced Prompt successfully mitigated "Hallucination by Omission" by forcing the model to look for specific quantitative evidence (Scores, Datasets) rather than qualitative summaries.

### Phase 2 Design Decision
Based on these results, we will utilize **Prompt B exclusively** for the ingestion pipeline.
* We will likely prioritize **Gemini 3 Pro** as the primary "Triage Agent" due to its superior performance in handling negative constraints and citation formatting.
* These capabilities are critical for the **"Groundedness" metric** of our final portal.

---

# Analysis Memo: Task 2 (Claim & Metric Extraction)

### Overview
Task 2 evaluated the models' ability to move beyond general triage and into Technical Specification Extraction. We tested the extraction of core claims (Prompt A) and the mapping of technical evaluation pipelines (Prompt B) using a Systems Architect persona. The primary challenge was the **Negative Constraint** regarding mathematical formulas and the Classification of RAG inputs.

### 1. Pattern: The "Formatting vs. Content" Trade-off
A significant technical failure was observed in Gemini 3 Pro regarding the Markdown table.
* **Gemini Failure (Runs 12 & 16):** Attempted to be "too helpful" by rendering complex formulas. This triggered a recurring formatting/cut-off error, rendering the "Logic" column difficult to read.
* **ChatGPT Success (Run 14):** Recognized the operational intent of the "Yes/No" column. It confirmed the existence of a formula without attempting to render LaTeX within a dense table, maintaining a clean structure.

> **Takeaway:** For high-density technical tables, **ChatGPT** shows higher "format awareness," whereas Gemini prioritizes "content depth" at the expense of UI/UX stability.

### 2. Failure Mode: Negative Constraint Adherence
The "Negative Constraint" (write "FORMULA MISSING" if no math is present) was a stress test for hallucination.

* **ChatGPT:** Managed this perfectly (Run 10), correctly identifying that many RAG metrics are described conceptually (LLM-as-a-judge) without formal algebraic definitions.
* **Gemini:** Suffered from "Missing Values" (Run 12). Instead of explicitly writing the requested string, it occasionally left fields blank or failed to bridge the gap between technical description and formal equation.

> **Implication:** **ChatGPT** is currently the more reliable model for logic-gate instructions (If X, then Y) in a technical context.

### 3. Pattern: Qualitative Grounding (Claims vs. Definitions)
Both models performed exceptionally well on Prompt A (Baseline), successfully moving beyond definitions to identify strategic claims (e.g., the trade-off between retrieval and generation quality).

* **Gemini Strength:** Inclusion of "Bonus Summary Tables" (Run 15) added significant value for a human reader—synthesis that wasn't explicitly asked for but was highly relevant.
* **Evidence Traceability:** Both models maintained **100% accuracy** in claim-quote pairing.

> **Observation:** For high-level "Claim-Evidence" tasks, model choice is less critical than for structured "Metric-Mapping" tasks.

### Phase 2 Design Decision
For the Evaluation Pipeline mapping:

1.  **Metric Logic Extraction:** We will adopt **ChatGPT's approach** for the "Metric Table" to ensure the formatting does not break and that negative constraints (`FORMULA MISSING`) are strictly followed.
2.  **Claim Verification:** We can use either model, but **Gemini 3 Pro** is preferred for "Synthesis/Summary" due to its ability to provide helpful technical context beyond basic requirements.
3.  **Refinement:** We will update the Prompt B schema to **explicitly forbid LaTeX rendering in tables** to prevent the "cut-off" issue observed in Gemini's runs.