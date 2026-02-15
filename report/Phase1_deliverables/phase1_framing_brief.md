# Research Proposal: Automated Evaluation of RAG Systems

**Student Names:** Gaurav Pandey & Shantanu Shastri
**Course:** 95-864 A3
**Date:** Spring 2026

---

## 1. Research Domain
**Domain:** Automated Evaluation of Retrieval-Augmented Generation (RAG) Systems

This project focuses on the **"Evaluation Gap"** in RAG pipelines. While RAG systems are widely deployed, measuring their reliability remains an unsolved problem. Traditional NLP metrics (like BLEU or ROUGE) fail to capture "groundedness," and human evaluation is too expensive for continuous integration. This domain explores **reference-free evaluation metrics** that use LLMs as judges to score retrieval quality and generation faithfulness.

## 2. Main Research Question
**Primary Question:**
> "How can we reliably distinguish between 'Retrieval Errors' (missing context) and 'Generation Errors' (hallucination) in automated RAG evaluation pipelines?"

This question addresses the **"Blame Game"** in RAG: when an answer is wrong, is it because the retriever failed to find the document, or because the LLM ignored the document it found?

## 3. Sub-Questions (Decomposition)
To answer the main question, we will investigate the following retrievable sub-questions:

* **Metric Definitions:** How do leading frameworks (e.g., Ragas, Self-RAG, ARES) mathematically define "Faithfulness" vs. "Context Recall"?
* **Correlation:** To what extent do automated "LLM-as-a-Judge" scores correlate with human expert judgments on technical domains?
* **Failure Modes:** What are the known limitations of reference-free evaluation (e.g., does the "Judge" LLM hallucinate the score)?
* **Optimization:** Which retrieval parameters (chunk size, top-k) have the highest impact on "Context Precision"?

## 4. Scope (Inclusions & Exclusions)

### Inclusions (What we will build/test)
* **Source Material:** Peer-reviewed papers and technical reports from 2023–2026 focusing on RAG evaluation (e.g., Ragas, Self-RAG, Corrective RAG, TruLens).
* **Methodology:** We will focus on **"Reference-Free" metrics** (where no gold-standard answer exists) because this represents the real-world production constraint.
* **Tasks:** We are testing the system's ability to:
    * **Triage Papers:** Extract formal definitions of metrics (Contribution, Method, Limitations).
    * **Verify Claims:** Extract exact quotes that support specific claims about metric performance.

### Exclusions (What we will NOT cover)
* **General LLM Benchmarks:** We will exclude general reasoning benchmarks (like MMLU or GSM8K) that do not involve retrieval.
* **Multimodal RAG:** We will strictly focus on text-based retrieval, excluding image/video RAG evaluation to keep the scope manageable.
* **Fine-Tuning:** We are evaluating the retrieval pipeline and prompting strategies, not fine-tuning the underlying embedding models or LLMs.

## 5. Phase 1 Experiment Design

| Component | Selection |
| :--- | :--- |
| **Tasks** | 1. **Paper Triage** (Structured Summarization of Methods/Limitations)<br>2. **Claim-Evidence Extraction** (Verifying Groundedness) |
| **Test Cases** | **Case A:** *Ragas: Automated Evaluation of Retrieval Augmented Generation* (Es et al.)<br>**Case B:** *Self-RAG: Learning to Retrieve, Generate, and Critique* (Asai et al.) |
| **Models** | **Model 1:** GPT-4o (OpenAI) – representing high-reasoning proprietary models.<br>**Model 2:** Gemini 1.5 Pro / Claude 3.5 Sonnet – representing long-context capability. |
| **Evaluation** | We will manually score **16 outputs** (2 Tasks × 2 Cases × 2 Prompts × 2 Models) on a 1–4 scale for Groundedness and Citation Correctness. |