import os
import pandas as pd
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import uuid

class Ingestor:
    def __init__(self, manifest_path="data/data_manifest.csv", persist_directory="./data/chroma_db"):
        self.manifest_path = manifest_path
        self.persist_directory = persist_directory
        # using local embeddings to avoid API key dependency for ingestion
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="rag_evaluation_corpus"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True
        )

    def load_manifest(self):
        """Loads the data manifest CSV."""
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
        return pd.read_csv(self.manifest_path)

    def process_document(self, row):
        """Loads, chunks, and embeds a single document from the manifest row."""
        file_path = row['raw_path']
        source_id = row['source_id']
        title = row['title']
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}. Skipping.")
            return []

        # Load PDF
        try:
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

        # Add metadata to each page BEFORE split
        for doc in docs:
            doc.metadata.update({
                "source_id": str(source_id),
                "title": title,
                "year": int(row['year']) if pd.notna(row['year']) else 0,
                "authors": row['authors'] if pd.notna(row['authors']) else "Unknown"
            })

        # Split
        chunks = self.text_splitter.split_documents(docs)

        # Add unique chunk IDs
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_id}_chunk_{i}"
            chunk.metadata['chunk_id'] = chunk_id
            chunk.metadata['doc_id'] = str(uuid.uuid4())

        return chunks

    def run(self):
        """Main ingestion loop."""
        df = self.load_manifest()
        all_chunks = []
        
        print(f"Found {len(df)} documents in manifest.")
        
        for _, row in df.iterrows():
            print(f"Processing: {row['title']} ({row['source_id']})")
            chunks = self.process_document(row)
            all_chunks.extend(chunks)
            
        if all_chunks:
            print(f"Ingesting {len(all_chunks)} chunks to ChromaDB...")
            batch_size = 100 # Chroma limit
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i+batch_size]
                self.vector_store.add_documents(documents=batch)
                print(f"Added batch {i//batch_size + 1}/{(len(all_chunks)+batch_size-1)//batch_size}")
            
            print("Ingestion complete.")
        else:
            print("No chunks to ingest.")

if __name__ == "__main__":
    # Ensure environment variables are loaded if necessary
    # from dotenv import load_dotenv
    # load_dotenv()
    
    ingestor = Ingestor()
    ingestor.run()
