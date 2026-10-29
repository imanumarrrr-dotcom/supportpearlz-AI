from langchain_chroma import Chroma

def retrieve(store: Chroma, query: str, k: int = 5, doc_type: str | None = None):
    search_filter = {"doc_type": doc_type} if doc_type and doc_type != "All types" else None
    return store.similarity_search_with_relevance_scores(query, k=k, filter=search_filter)
