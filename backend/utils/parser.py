import csv
import io
import json
import re
from typing import Any

# from typing import Any, List, Dict, Optional

KV_RE = re.compile(r"(\w+)=([^\s]+)")


def clean_csv(raw_text: str) -> str:
    if "```csv" in raw_text:
        raw_text = raw_text.split("```csv")[1].split("```")[0]
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0]

    lines = raw_text.strip().split('\n')

    if not lines:
        return ""
    header = lines[0]

    if "," not in header:
        data_lines = lines[1:]
    else:
        data_lines = [line for line in lines[1:] if "," in line]

    return '\n'.join([header] + data_lines)


def parse_csv(text: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(clean_csv(text)))
    return [dict(row) for row in reader]


def _parse_json(text: str) -> list[dict[str, Any]]:
    obj = json.loads(text)
    return obj if isinstance(obj, list) else [obj]


def _parse_jsonl(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _parse_kv_log(text: str) -> list[dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        pairs = KV_RE.findall(line.strip())
        rows.append({k: v for k, v in pairs} if pairs else {"message": line})
    return rows


def parse_bytes(raw: bytes, filename: str = None) -> list[dict[str, Any]]:
    text = raw.decode("utf-8", errors="ignore")
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    else:
        ext = ""

    if ext == "csv":
        return parse_csv(text)
    if ext == "json":
        return _parse_json(text)
    if ext in ("jsonl", "ndjson"):
        return _parse_jsonl(text)

    return _parse_kv_log(text)


def parse_dicts(fields: list) -> list:
    return [f.model_dump() if hasattr(f, 'model_dump') else f for f in fields]
