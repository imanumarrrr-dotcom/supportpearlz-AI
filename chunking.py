from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(documents: list[Document], chunk_size: int = 800, chunk_overlap: int = 120) -> list[Document]:
    if chunk_size < 100:
        raise ValueError("chunk_size must be at least 100 characters")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        add_start_index=True
    )
    chunks = splitter.split_documents(documents)
    source_docs = {}
    for original in documents:
        source_docs.setdefault(original.metadata.get("source", "unknown"), []).append(original)
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk-{idx:06d}"
        source = chunk.metadata.get("source", "unknown")
        # For text documents, attach the nearest heading to each chunk so citations are more useful.
        if chunk.metadata.get("page") is None and source.lower().endswith((".md", ".txt", ".docx")):
            originals = source_docs.get(source, [])
            start = int(chunk.metadata.get("start_index", 0) or 0)
            original_text = originals[0].page_content if originals else ""
            headings = [(m.start(), m.group(1).strip()) for m in __import__("re").finditer(r"(?m)^#{1,6}\s+(.+)$", original_text)]
            preceding = [h for pos, h in headings if pos <= start]
            if preceding:
                chunk.metadata["location"] = "section: " + preceding[-1]
        elif source.lower().endswith(".csv"):
            chunk.metadata["location"] = "CSV row/record"

    return chunks
