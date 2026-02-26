# Synthesis Memo: Common Failure Modes of RAG Evaluation

The primary failure modes of Retrieval-Augmented Generation (RAG) systems revolve around two core stages: the retrieval of incorrect or insufficient context, and the generative limitations of the Large Language Model interpreting that context.

## 1. Retrieval Failures (Precision and Recall)

Retrieval failures are among the most common sources of errors. These can manifest during query processing, document matching, or result ranking phases (Source: 2601.05264v1, Chunk: 2601.05264v1_chunk_98). When the system fails to retrieve the correct context, the generation stage is starved of factual information, leading directly to hallucinations. Additionally, other failure modes such as query decomposition errors can occur when the initial user question is not broken down into effective, specific sub-queries (Source: 2510.22344v1, Chunk: 2510.22344v1_chunk_156).

If the chunk size is excessively large, or if pure dense retrieval misses high-overlap keyword targets, the result ranking will push the necessary context out of the top-k window, creating a "missing content" failure mode (Source: 2601.05264v1, Chunk: 2601.05264v1_chunk_98).

## 2. Context Truncation and Over-saturation

Context truncation failures can occur as a result of insufficient or misleading context. When the retrieved information exceeds the model's context window, it results in incomplete or distorted responses, as critical evidence is cut off (Source: 2601.05264v1, Chunk: 2601.05264v1_chunk_191). Conversely, feeding too many weakly-related chunks into the context can dilute the LLM's attention, causing it to infer incorrect relationships.

## 3. Evaluation Limitations

Evaluating these failure modes is traditionally difficult without human intervention. Automated reference-free evaluation frameworks, such as RAGAS, have been proposed to evaluate RAG systems end-to-end to catch these specific errors (Source: 2601.05264v1, Chunk: 2601.05264v1_chunk_73). While these frameworks have shown promising results—with some metrics like "faithfulness" being highly accurate—evaluating "context relevance" remains a distinct challenge for models like ChatGPT (Source: 2309.15217v2, Chunk: 2309.15217v2_chunk_26).

---

### References

- **Source: 2601.05264v1**: "Retrieval-Augmented Generation Evaluation Frameworks"
- **Source: 2510.22344v1**: "Query Decomposition Strategies in RAG"
- **Source: 2309.15217v2**: "Evaluating LLM Generation Groundedness"
