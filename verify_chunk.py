from src.ingest.ingestor import Ingestor

ingestor = Ingestor()
# Fetch the specific chunk to verify content
results = ingestor.vector_store.get(ids=["2309.15217v2_chunk_24"])
print(f"Chunk 2309.15217v2_chunk_24 Content:\n{results['documents'][0]}")
