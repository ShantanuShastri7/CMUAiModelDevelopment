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

| Metric          | Result        | Description                                                       |
| :-------------- | :------------ | :---------------------------------------------------------------- |
| Total Queries   | 20            | Mixed set of Direct, Synthesis, and Edge Cases.                   |
| Success Rate    | 65% (13/20)   | Queries with generated answers based on context.                  |
| Refusal Rate    | 35% (7/20)    | Queries where the system correctly stated "Cannot find evidence." |
| Avg. Latency    | 4.64s         | Average time to retrieve and generate.                            |
| Min/Max Latency | 1.95s / 7.91s | Fastest (Q8) vs. Slowest (Q12).                                   |

## Detailed Query Evaluation Log

| ID  | Query                                                      | Status  | Latency | G   | F   | R   | Citations / Notes                                          |
| :-- | :--------------------------------------------------------- | :------ | :------ | :-- | :-- | :-- | :--------------------------------------------------------- |
| 0   | What is 'Context Precision' in RAG evaluation?             | Success | 6.79s   | 5   | 5   | 5   | Cited 2601.05264v1 (RAGAS framework).                      |
| 1   | How does Ragas measure faithfulness?                       | Success | 3.99s   | 5   | 5   | 5   | Cited 2309.15217v2; grounded in context.                   |
| 2   | What are the limitations of LLM-as-a-judge?                | Success | 3.50s   | 4   | 5   | 5   | Inferred limitations (Bias, Math) from 2407.12036v2.       |
| 3   | Define 'Groundness' in the context of RAG.                 | Success | 3.15s   | 5   | 5   | 5   | Cited TruLens/RAGAS definitions (2601.05264v1).            |
| 4   | What is 'Self-RAG' and how does it work?                   | Success | 3.19s   | 5   | 5   | 5   | Detailed 3-step process cited (2310.11511v1).              |
| 5   | How does 'Corrective RAG' improve retrieval?               | Refusal | 3.36s   | N/A | 5   | 5   | Correct Refusal: Concept not in corpus.                    |
| 6   | What metrics are used to evaluate retrieval quality?       | Success | 3.16s   | 5   | 5   | 5   | Listed Precision@k, NDCG, etc. (2601.05264v1).             |
| 7   | Explain the concept of 'Hit Rate'.                         | Refusal | 4.31s   | N/A | 4   | 5   | Refused: Term likely missing from chunks.                  |
| 8   | What is the difference between sparse and dense retrieval? | Success | 1.95s   | 5   | 5   | 5   | Comparison of storage/speed (2404.07220v2).                |
| 9   | How does chunk size affect RAG performance?                | Success | 5.91s   | 4   | 5   | 5   | Inferred: Smaller passage = better context (2507.23334v2). |
| 10  | Compare Ragas and TruLens evaluation frameworks.           | Success | 6.10s   | 5   | 5   | 5   | Comparison of focus/automation (2601.05264v1).             |
| 11  | What are the common failure modes of RAG systems?          | Success | 6.40s   | 5   | 5   | 5   | Cited "Retrieval failures" & "Truncation" (2601.05264v1).  |
| 12  | How can we mitigate hallucinations in RAG?                 | Success | 7.91s   | 5   | 5   | 5   | Proposed "Knowledge Base" injection (2409.11353v3).        |
| 13  | Discuss the trade-offs between latency and accuracy.       | Refusal | 2.65s   | N/A | 3   | 5   | Refusal: Unexpected given Q8 context.                      |
| 14  | Summarize state-of-the-art in reference-free evaluation.   | Success | 3.09s   | 5   | 5   | 5   | Cited "RAG,Reward" framework (2601.05264v1).               |
| 15  | Does the corpus mention 'Quantum RAG'?                     | Refusal | 3.97s   | N/A | 5   | 5   | Correct Refusal: Hallucination trap avoided.               |
| 16  | Who won the 2024 US Election?                              | Refusal | 5.92s   | N/A | 5   | 5   | Correct Refusal: Out of Domain (Robustness).               |
| 17  | What is the capital of France?                             | Success | 5.57s   | 5   | 5   | 5   | Simple retrieval success (2409.11353v3).                   |
| 18  | Explain 'Model Collapse' in RAG.                           | Refusal | 5.72s   | N/A | 4   | 5   | Refused: Definition missing in chunks.                     |
| 19  | Is there evidence for using GraphRAG for evaluation?       | Refusal | 6.81s   | N/A | 5   | 5   | Correctly identified lack of "Evaluation" evidence.        |

## Failure Analysis & Enhancement Impact

| Query ID | Category     | Outcome | Analysis / Root Cause                                                                                                                |
| :------- | :----------- | :------ | :----------------------------------------------------------------------------------------------------------------------------------- |
| Q4       | Synthesis    | Success | Multi-hop reasoning: Successfully combined chunk 2601.05264v1 (definition) and 2310.11511v1 (process steps) to explain Self-RAG.     |
| Q5       | Missing Info | Refusal | Knowledge Gap: "Corrective RAG" (CRAG) paper is not in the corpus. System correctly refused rather than hallucinating.               |
| Q16      | Robustness   | Refusal | Out-of-Domain: System correctly filtered out irrelevant chunks (e.g., Arabic NLP papers) and refused to answer a political question. |
| Q10      | Comparison   | Success | Structured Retrieval: Successfully pulled attributes (Focus, Automation Level) from different sections to compare Ragas and TruLens. |
| Q13      | Trade-offs   | Failure | Retrieval Miss: System failed to connect "Sparse vs Dense" evidence (Q8) to the broader "Latency vs Accuracy" query.                 |

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
