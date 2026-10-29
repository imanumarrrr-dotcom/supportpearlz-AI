import logging
import os
from pathlib import Path

def configure_logging(level: str = "INFO") -> logging.Logger:
    Path("logs").mkdir(exist_ok=True)
    logger = logging.getLogger("supportpearlz")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        file_handler = logging.FileHandler("logs/supportpearlz.log", encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(console)
        logger.addHandler(file_handler)
    return logger

import json

def get_logger():
    return configure_logging(os.getenv("LOG_LEVEL", "INFO"))

def append_jsonl(path, record):
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

def read_jsonl(path):
    target = Path(path)
    if not target.exists(): return []
    rows = []
    for line in target.read_text(encoding="utf-8").splitlines():
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: continue
    return rows
