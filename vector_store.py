from pathlib import Path
import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

class IndexNotFoundError(FileNotFoundError): pass
class IndexMismatchError(RuntimeError): pass

def read_manifest(path="data/vector_store"):
    f = Path(path) / "manifest.json"
    try: return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError): return None

def index_exists(path="data/vector_store") -> bool:
    root = Path(path)
    # A placeholder .gitkeep is not a usable index. Require both Chroma data and a manifest.
    return (root / "manifest.json").is_file() and (root / "chroma.sqlite3").is_file()

def make_embeddings(api_key: str, model: str = "text-embedding-3-small") -> OpenAIEmbeddings:
    return OpenAIEmbeddings(api_key=api_key, model=model, max_retries=2)

def build_vector_store(chunks: list[Document], api_key: str, path: str, embedding_model: str) -> Chroma:
    if not chunks:
        raise ValueError("No readable documents found. Add documents to data/knowledge_base first.")
    Path(path).mkdir(parents=True, exist_ok=True)
    # Clear the prior collection to avoid duplicate/stale chunks on a forced rebuild.
    import shutil
    if Path(path).exists():
        shutil.rmtree(path, ignore_errors=True)
        Path(path).mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks, embedding=make_embeddings(api_key, embedding_model),
        persist_directory=path, collection_name="supportpearlz"
    )

def load_vector_store(api_key: str, path: str, embedding_model: str) -> Chroma:
    if not index_exists(path):
        raise IndexNotFoundError("No valid persisted index found. Build or rebuild the knowledge-base index first.")
    return Chroma(
        persist_directory=path, embedding_function=make_embeddings(api_key, embedding_model),
        collection_name="supportpearlz"
    )
