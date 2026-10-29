from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

def condense_question(question: str, history: list[dict], api_key: str, model: str) -> str:
    if not history:
        return question
    recent = history[-8:]
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
    llm = ChatOpenAI(api_key=api_key, model=model, temperature=0)
    prompt = ("Rewrite the latest customer question as a standalone retrieval query using relevant recent context. "
              "If the latest question clearly changes topic, do not carry old entities forward. Return only the query.")
    result = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=f"History:\n{transcript}\nLatest question: {question}")])
    return str(result.content).strip() or question
