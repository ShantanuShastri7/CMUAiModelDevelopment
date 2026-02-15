# Phase 1 Prompt Kit

## Task 1: Paper Triage (Definition & Summary)
**Goal:** Extract a structured 5-field summary (Contribution, Method, Data, Findings, Limitations) from technical research papers.

### Prompt A: Baseline (Simple)
**Intent:** To test if a standard, unconstrained instruction can correctly identify specific technical details like "Limitations" and "Data" without hallucinating.

**Prompt Text:**
Summarize the provided text into the following five fields: Contribution, Method, Data, Findings, and Limitations.


---

### Prompt B: Advanced (Systems Architect Persona)
**Intent:** To force structured, machine-readable output (JSON) and prevent "Hallucination by Omission" using negative constraints.
* **Constraint 1 (JSON Format):** Ensures the output can be programmatically ingested in Phase 2.
* **Constraint 2 (Negative Constraint - "NOT STATED"):** Prevents the model from guessing generic datasets or limitations when none are present in the text.
* **Constraint 3 (Groundedness):** Forces the model to only list limitations explicitly admitted by the authors, avoiding "critique" vs "summary" confusion.

**Prompt Text:**
Persona: You are a rigorous Research Scientist.

Instruction: Analyze the provided text and extract a structured summary.

Output Format: Produce a valid JSON object with exactly these 5 keys:
* "Contribution": (1 sentence on the core value add)
* "Method": (Specific techniques, algorithms, or metrics proposed)
* "Data": (Specific datasets or sources used)
* "Findings": (Key quantitative results or performance metrics)
* "Limitations": (Explicit weaknesses admitted by the authors)

Strict Constraints: 
1. No Hallucinations: If a field is not explicitly stated in the text, you MUST write "NOT STATED". Do not guess. 2. Groundedness: For "Limitations", only list those explicitly mentioned in the text. 
3. Citation Requirement: For "Findings" and "Limitations", you MUST append a brief direct quote from the text to verify your claim. Example: "High latency (Source: 'latency increased by 20%')"

----------
----------


## Task 2: Claim–evidence extraction

### Prompt A: Baseline (Main claims)
**Intent:** To extract the core philosophical arguments of the papers before diving into technical specifics. This ensures the "why" isn't lost in the "how."

**Prompt Text:**
Summarize the top 5 claims regarding RAG evaluation and self-critique made in the provided text. For each claim, you must provide a direct quote for verification.


---

### Prompt B: Advanced (Systems Architect Persona)
**Intent:** To create a technical mapping of the evaluation pipeline. This forces the model to differentiate between data inputs and identifies where the papers might be "hand-wavy" regarding math.

**Prompt Text:**
Persona: You are a Systems Architect designing a production-grade RAG evaluation pipeline.

Instruction: Analyze the provided text and extract specific definitions for the evaluation metrics (Ragas) and critique tokens (Self-RAG). Categorize each based on its operational logic.

Strict Constraints:
1. Input Classification: For each entry, explicitly categorize the input as "Question," "Context," or "Generation." If a metric compares two, list both (e.g., "Context + Generation").
2. Negative Constraint: If the text describes a metric but does not provide an explicit mathematical formula or a specific critique symbol (e.g., $S_{q}$ or $[IsREL]$), you MUST write "FORMULA MISSING" in the Logic column.
3. No Hallucinations: Do not infer logic that isn't explicitly written.

Output Format: Output a Markdown table with the following columns:
| Metric/Token Name | Input Required | Logic/Definition | Formula/Symbol Present? |
| :--- | :--- | :--- | :--- |
Text:
[PASTE PDF TEXT HERE]
