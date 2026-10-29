import argparse, json
from pathlib import Path
from src.config import settings
from src.ingestion.loaders import load_documents
from src.ingestion.chunking import split_documents
from src.retrieval.vector_store import build_vector_store, load_vector_store
from src.config import settings as default_settings


def build_index(api_key: str, chunk_size: int | None = None, chunk_overlap: int | None = None):
    size = chunk_size or default_settings.chunk_size
    overlap = default_settings.chunk_overlap if chunk_overlap is None else chunk_overlap
    docs, report = load_documents(default_settings.knowledge_base_path)
    chunks = split_documents(docs, size, overlap)
    store = build_vector_store(chunks, api_key, default_settings.vector_store_path, default_settings.embedding_model)
    info = {"documents": len(docs), "chunks": len(chunks), "chunk_size": size, "chunk_overlap": overlap}
    Path(default_settings.vector_store_path, "manifest.json").write_text(json.dumps({"embedding_model": default_settings.embedding_model, **info}, indent=2), encoding="utf-8")
    return store, report, info

def sync_index(api_key: str):
    from src.retrieval.vector_store import index_exists
    if index_exists(default_settings.vector_store_path):
        store = load_vector_store(api_key, default_settings.vector_store_path, default_settings.embedding_model)
        return store, [], {"status": "loaded existing index"}
    return build_index(api_key)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Force a fresh index build")
    parser.add_argument("--api-key", default=None, help="Optional API key; prefer using the Streamlit UI")
    args = parser.parse_args()
    import os
    key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("Missing API key. Use the Streamlit UI or set OPENAI_API_KEY for CLI indexing.")
    docs, report = load_documents(settings.knowledge_base_path)
    chunks = split_documents(docs, settings.chunk_size, settings.chunk_overlap)
    build_vector_store(chunks, key, settings.vector_store_path, settings.embedding_model)
    Path(settings.vector_store_path, "manifest.json").write_text(json.dumps({"embedding_model": settings.embedding_model, "documents": len(docs), "chunks": len(chunks), "chunk_size": settings.chunk_size, "chunk_overlap": settings.chunk_overlap}, indent=2), encoding="utf-8")
    Path("evaluation/results").mkdir(parents=True, exist_ok=True)
    Path("evaluation/results/ingestion_report.json").write_text(json.dumps({"files": report, "documents": len(docs), "chunks": len(chunks)}, indent=2), encoding="utf-8")
    print(f"Index built: {len(docs)} document units -> {len(chunks)} chunks")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
