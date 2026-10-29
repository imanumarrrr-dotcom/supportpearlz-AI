from pathlib import Path
from typing import Iterable
import hashlib
import logging
import re
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader

SUPPORTED = {".pdf", ".docx", ".md", ".txt", ".csv"}
logger = logging.getLogger("supportpearlz")

def _normalise(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def load_documents(folder: str) -> tuple[list[Document], list[dict]]:
    base = Path(folder)
    base.mkdir(parents=True, exist_ok=True)
    docs, report, seen = [], [], set()
    paths = sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED and "assignment_manual" not in p.name.lower() and "langchain_rag_assignment_manual" not in p.name.lower())
    for path in paths:
        try:
            ext = path.suffix.lower()
            if ext == ".pdf":
                loaded = PyPDFLoader(str(path)).load()
            elif ext == ".docx":
                loaded = Docx2txtLoader(str(path)).load()
            elif ext == ".csv":
                loaded = CSVLoader(str(path), encoding="utf-8").load()
            else:
                loaded = TextLoader(str(path), encoding="utf-8", autodetect_encoding=True).load()
            added = 0
            for i, doc in enumerate(loaded):
                text = _normalise(doc.page_content)
                if not text:
                    continue
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if digest in seen:
                    continue
                seen.add(digest)
                metadata = dict(doc.metadata)
                version_match = re.search(r"(?im)^version\s*:\s*([^|\n]+)", text)
                updated_match = re.search(r"(?im)^last updated\s*:\s*([^|\n]+)", text)
                product_line = "general"
                for candidate in ("AquaPearl 500 Pro", "AquaPearl 300", "AeroPearl Mini", "AquaPearl 200"):
                    if candidate.lower() in (path.stem + " " + text[:500]).lower():
                        product_line = candidate
                        break
                page_num = int(metadata.get("page", i)) + 1 if ext == ".pdf" else None
                metadata.update({
                    "source": path.name,
                    "doc_type": _doc_type(path),
                    "product_line": metadata.get("product_line", product_line),
                    "version": metadata.get("version", version_match.group(1).strip() if version_match else "unspecified"),
                    "last_updated": updated_match.group(1).strip() if updated_match else "unspecified",
                    "location": f"page {page_num}" if ext == ".pdf" else (f"row {i + 1}" if ext == ".csv" else f"section {i + 1}"),
                    "content_hash": digest,
                })
                docs.append(Document(page_content=text, metadata=metadata))
                added += 1
            report.append({"file": path.name, "type": ext, "characters": sum(len(d.page_content) for d in loaded),
                           "pages_or_records": len(loaded), "loaded_units": added, "status": "loaded" if added else "empty/duplicate"})
        except Exception as exc:
            logger.warning("Skipping unreadable file %s: %s", path.name, exc)
            report.append({"file": path.name, "type": path.suffix.lower(), "status": "skipped", "reason": str(exc)})
    return docs, report

def _doc_type(path: Path) -> str:
    name = path.stem.lower()
    if "warranty" in name or "refund" in name or "shipping" in name or "privacy" in name:
        return "policy"
    if "faq" in name:
        return "faq"
    if "order_account" in name:
        return "guide"
    if "price" in name:
        return "pricing"
    if "troubleshoot" in name or "install" in name or "maintenance" in name:
        return "guide"
    if "manual" in name or "product_changelog" in name:
        return "manual"
    return "general"
