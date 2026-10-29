# SupportPearlz AI — LangChain RAG Customer Support Agent

A Streamlit interface over a LangChain retrieval-augmented generation (RAG) pipeline. The app asks for an API key before showing the console, validates it, and keeps it in Streamlit session memory only (not in `.env`, logs, or files).

## Features
- API-key gate with validation before console access.
- Animated dark glass dashboard, responsive sidebar, gradient accents and chat UI.
- PDF, DOCX, Markdown, TXT and CSV ingestion with per-file error handling.
- Persistent Chroma vector index; build/rebuild is separate from query-time retrieval.
- Metadata on each chunk, relevance gate, grounded answer prompt, structured Pydantic response.
- Source cards with document/location and a preview of retrieved evidence.
- Session chat history, follow-up query condensation, reset-chat control.
- Admin controls for chunk size, overlap, top-k and score threshold.
- Upload documents, rebuild index, view ingestion report and logs.
- Evaluation starter set with 20 cases and JSON results output support.

## Quick start (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```
Python 3.10–3.12 is recommended. If `py -3.11` is unavailable, install Python 3.11 first.

## Using the app
1. Open the Streamlit URL in your browser.
2. Enter an OpenAI API key. The app validates it before revealing the console.
3. Add your own policy/manual documents in **Knowledge Base** or place them in `data/knowledge_base/`.
4. Click **Build / Rebuild index**. This is the offline ingestion path; questions do not re-embed the corpus.
5. Ask questions and inspect source citations. Unknown answers should be refused rather than guessed.

The knowledge base is a fictional, internally consistent training corpus with Markdown, CSV, PDF and DOCX files, deliberate cross-document seams, and documented answer gaps. `data/knowledge_base/DATASET_NOTES.md` lists the seams and gaps. The assessment manual PDF is not indexed as customer knowledge. The approximate Markdown/text/CSV corpus count is around 10,000 words; the PDF and DOCX files add further content.

## Security notes
- The API key is held in Streamlit session state only and is not written to disk or logged. Session memory is not a secure vault; use a private device and clear the session when finished.
- Never commit `.env`, API keys, customer PII, or vector-store data.
- Set provider spending limits before indexing a large corpus.
- For production use, add authentication, secret management, rate limiting, access controls, PII redaction, and human review for refunds, safety issues and commercial commitments.

## CLI / pipeline commands
```powershell
python -m src.ingestion.build_index
python -m src.ingestion.build_index --rebuild
python -m src.app_cli
python -m evaluation.run_eval
```

## Project structure
```text
app.py
src/
  config.py
  ingestion/loaders.py
  ingestion/chunking.py
  ingestion/build_index.py
  retrieval/vector_store.py
  retrieval/retriever.py
  chains/prompts.py
  chains/schemas.py
  chains/memory.py
  chains/rag_chain.py
  utils/logging_setup.py
data/knowledge_base/
evaluation/test_questions.json
evaluation/run_eval.py
tests/
```

## Assignment experiments and deliverables

The project now includes runnable experiment scripts and a draft technical report. API-dependent results are intentionally not pre-filled; run them against your own API key and index before submission.

```powershell
# Build/rebuild the vector index (requires OPENAI_API_KEY in the environment)
python -m src.ingestion.build_index --rebuild

# Run measured experiments after indexing
python -m evaluation.experiment_chunking
python -m evaluation.embedding_diagnostic
python -m evaluation.experiment_retrieval
python -m evaluation.run_eval
```

- `evaluation/experiment_chunking.py`: six chunk-size/overlap configurations and measured top-4 answer-chunk hit rate.
- `evaluation/embedding_diagnostic.py`: actual embedding dimension and pairwise cosine similarities.
- `evaluation/experiment_retrieval.py`: similarity k=3, similarity k=8 and MMR k=5 comparisons.
- `evaluation/prompt_injection_test.json`: adversarial test prompts to run and inspect.
- `docs/technical_report.pdf` and `.md`: analytical report draft with explicit pending-measurement notes.
- `docs/architecture.mmd`: architecture diagram source.
- `docs/demo_script.md`: 5–8 minute recording plan and six screenshot checklist.
- `evaluation/run_eval.py`: 20-case live run, JSON/Markdown output and manual scoring worksheet.

Before submission, run the experiments, review actual outputs and citations, complete manual scores/failure analysis, capture six real screenshots, and record the demo. Do not claim that live API experiments passed unless the generated evidence shows it.
