import arxiv
import pandas as pd
import os
from datetime import datetime

class ArxivFetcher:
    def __init__(self, data_dir="data/raw", manifest_path="data/data_manifest.csv"):
        self.data_dir = data_dir
        self.manifest_path = manifest_path
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def search_and_download(self, query="RAG evaluation", max_results=20):
        print(f"Searching Arxiv for: {query}")
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        new_entries = []
        
        # Load existing manifest to avoid duplicates
        if os.path.exists(self.manifest_path):
            existing_df = pd.read_csv(self.manifest_path)
            existing_ids = set(existing_df['source_id'].astype(str))
        else:
            existing_ids = set()

        for result in client.results(search):
            source_id = result.entry_id.split('/')[-1]
            title = result.title.replace('\n', ' ')
            
            if source_id in existing_ids:
                print(f"Skipping existing: {title}")
                continue

            filename = f"{source_id}.pdf"
            filepath = os.path.join(self.data_dir, filename)
            
            print(f"Downloading: {title}")
            try:
                result.download_pdf(dirpath=self.data_dir, filename=filename)
                
                new_entries.append({
                    "source_id": source_id,
                    "title": title,
                    "authors": ", ".join([a.name for a in result.authors]),
                    "year": result.published.year,
                    "source_type": "Paper",
                    "venue": "Arxiv",
                    "url_or_doi": result.entry_id,
                    "raw_path": filepath,
                    "processed_path": "",
                    "tags": "RAG, Evaluation, Automated",
                    "relevance_note": "Fetched from Arxiv based on query."
                })
            except Exception as e:
                print(f"Failed to download {title}: {e}")

        if new_entries:
            new_df = pd.DataFrame(new_entries)
            if os.path.exists(self.manifest_path):
                # Append without writing header
                new_df.to_csv(self.manifest_path, mode='a', header=False, index=False)
            else:
                new_df.to_csv(self.manifest_path, index=False)
            print(f"Added {len(new_entries)} new papers to manifest.")
        else:
            print("No new papers downloaded.")

if __name__ == "__main__":
    fetcher = ArxivFetcher()
    fetcher.search_and_download()
