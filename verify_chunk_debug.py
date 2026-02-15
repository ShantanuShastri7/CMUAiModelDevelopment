from src.ingest.ingestor import Ingestor

ingestor = Ingestor()
print(f"Collection count: {ingestor.vector_store._collection.count()}")
# Get first few IDs to check format
ids = ingestor.vector_store._collection.get()['ids'][:5]
print(f"Sample IDs: {ids}")

# Try fetching specific ID again
target_id = "2309.15217v2_chunk_24"
if target_id in ids or True: # Force try
    results = ingestor.vector_store.get(ids=[target_id])
    if results['documents']:
        print(f"\nChunk {target_id} Content:\n{results['documents'][0][:200]}...") # Print first 200 chars
    else:
        print(f"\nChunk {target_id} NOT FOUND.")
