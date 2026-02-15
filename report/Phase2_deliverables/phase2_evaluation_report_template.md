# Phase 2 Evaluation Report: Ground the Domain

**Student Name:** [Your Name]
**Date:** [Date]

## 1. Query Set Design

_Describe how you chose your 20 queries._

- **Direct Questions (10):** tested basic retrieval...
- **Synthesis Questions (5):** tested multi-hop reasoning...
- **Edge Cases (5):** tested refusal and robustness...

## 2. Evaluation Metrics & Results

_Summarize the results from `outputs/eval/`._

| Metric           | Score (1-4) | Notes                                     |
| :--------------- | :---------- | :---------------------------------------- |
| **Groundedness** | [Score]     | How well answers are supported by chunks. |
| **Faithfulness** | [Score]     | Did the system refuse when appropriate?   |
| **Relevance**    | [Score]     | Precision of retrieval.                   |

### Quantitative Summary

- **Average Latency:** [X] seconds
- **Success Rate:** [X/20] queries answered

## 3. Enhancement Analysis: Reranking

## 3. Enhancement Analysis: Reranking (FlashRank)

I conducted an A/B test comparing the Baseline (Top-5 Vector Search and No Reranking) vs. the Enhanced Pipeline (Top-25 Search + FlashRank Reranking).

### Impact Summary

- **Precision Improvement:** The reranker successfully surfaced relevant chunks for synthesis queries where the baseline failed.
- **Latency Trade-off:** Reranking added ~1.5s to the average latency (Baseline: ~0.5s vs. Enhanced: ~2.0s), but significantly improved answer quality.

### Specific Examples of Improvement

1.  **Query 14: "Summarize the state-of-the-art in reference-free RAG evaluation."**
    - **Baseline:** Failed to find evidence ("I cannot find evidence for this...").
    - **Enhanced:** Successfully retrieved details about "RAG,Reward" and "RAGAS" frameworks (Source: 2601.05264v1), providing a comprehensive summary.
2.  **Query 11: "What are the common failure modes of RAG systems?"**
    - **Baseline:** Provided a vague answer, stating the context "does not provide a comprehensive list."
    - **Enhanced:** Correctly identified specific failure modes: "retrieval failures," "context truncation," and "missing content" (Source: 2601.05264v1).

**Conclusion:** The FlashRank reranker is critical for "Synthesis" type questions where the answer is distributed across the document or phrased differently than the query.

## 4. Failure Modes

### Case 1: Missing Concept (Knowledge Gap)

- **Query:** "How does 'Corrective RAG' improve retrieval?"
- **Answer:** "I cannot find evidence for this..."
- **Analysis:** Correct behavior (Refusal). The concept "Corrective RAG" (CRAG) is from a paper (2401.15884) that is NOT in our current corpus (only RAGAS and Self-RAG are).
- **Fix:** Fetch and ingest the CRAG paper: `python3 src/main.py fetch --query "Corrective RAG"`.

### Case 2: Out of Domain (Robustness)

- **Query:** "Who won the 2024 US Election?"
- **Answer:** "I cannot find evidence for this..."
- **Analysis:** Correct behavior. The system correctly refused to answer a question irrelevant to RAG evaluation.
- **Fix:** None needed. This is desired behavior.

### Case 3: Specific Definition (Granularity)

- **Query:** "Explain 'Model Collapse' in RAG."
- **Answer:** "I cannot find evidence for this..."
- **Analysis:** Potential Retrieval failure. "Model Collapse" might be mentioned in passing, but retrieved chunks didn't contain the definition.
- **Fix:** Improve chunking strategy or add dense retrieval.

## 5. Conclusion

_Final thoughts on the system's readiness for Phase 3._
