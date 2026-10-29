import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.chains.prompts import SYSTEM_PROMPT_V1
from src.chains.schemas import SupportAnswer
from src.chains.memory import condense_question
from src.retrieval.retriever import retrieve

def answer_question(question: str, history: list[dict], store, api_key: str, model: str,
                    temperature: float = 0.1, k: int = 5, threshold: float = 0.35,
                    doc_type: str | None = None) -> dict:
    started = time.perf_counter()
    rewritten = condense_question(question, history, api_key, model)
    hits = retrieve(store, rewritten, k=k, doc_type=doc_type)
    hits = [(d, float(s)) for d, s in hits if s >= threshold]
    sources, context_blocks = {}, []
    for i, (doc, score) in enumerate(hits, start=1):
        label = f"S{i}"
        meta = doc.metadata
        source = f"{meta.get('source', 'unknown')} — {meta.get('location', 'location unavailable')}"
        sources[label] = {"source": source, "score": round(score, 4), "snippet": doc.page_content[:700], "metadata": meta}
        context_blocks.append(f"[{label}] source={source}; doc_type={meta.get('doc_type')}\n{doc.page_content[:3500]}")
    if not context_blocks:
        result = SupportAnswer(answer="I couldn't find reliable supporting information for this question in the current knowledge base. Please contact the support team for confirmation.", sources=[], confidence="none", answered=False)
    else:
        llm = ChatOpenAI(api_key=api_key, model=model, temperature=temperature, max_retries=1, timeout=45)
        structured = llm.with_structured_output(SupportAnswer)
        prompt = f"{SYSTEM_PROMPT_V1}\n\nRETRIEVED CONTEXT:\n" + "\n\n".join(context_blocks) + f"\n\nCustomer question: {question}\nStandalone retrieval query: {rewritten}"
        try:
            result = structured.invoke([SystemMessage(content=SYSTEM_PROMPT_V1), HumanMessage(content=prompt)])
            valid_labels = {f"[{key}]" for key in sources}
            result.sources = [s for s in result.sources if s in valid_labels]
            if not result.answered:
                result.confidence = "none"
            elif result.confidence == "high" and not result.sources:
                result.confidence = "partial"
        except Exception:
            result = SupportAnswer(answer="I couldn't safely validate a response. Please contact the support team and try again later.", sources=[], confidence="none", answered=False)
    return {"answer": result.answer, "sources": result.sources, "confidence": result.confidence,
            "answered": result.answered, "retrieved": sources, "rewritten_query": rewritten,
            "latency_ms": round((time.perf_counter()-started)*1000), "refused": not result.answered}
