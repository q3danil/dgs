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


def parse_csv(text: str, expected_columns: list) -> list[dict[str, Any]]:
    cleaned_text = clean_csv(text)
    if not cleaned_text:
        return []

    lines = cleaned_text.strip().split('\n')
    if not lines:
        return []

    first_line = lines[0].lower()
    has_header = not ('"1"' in first_line or '1,' in first_line)

    f = io.StringIO(cleaned_text)
    reader = csv.reader(f, quotechar='"', delimiter=',', skipinitialspace=True)

    if has_header:
        try:
            raw_headers = next(reader)
            headers = [str(h).strip().strip('"').lower() for h in raw_headers]
        except StopIteration:
            headers = [c.lower() for c in expected_columns]
    else:
        headers = [c.lower() for c in expected_columns]

    data = []
    for row in reader:
        if not row: continue
        clean_row = {}
        for i, h_name in enumerate(headers):
            if i < len(row):
                clean_row[h_name] = row[i]
        ordered_row = {}
        for col in expected_columns:
            col_target = col.lower().strip()
            val = clean_row.get(col_target)
            if val is None:
                try:
                    idx = [c.lower() for c in expected_columns].index(col_target)
                    if idx < len(row):
                        val = row[idx]
                except ValueError:
                    pass

            if val is not None:
                val = str(val).strip().strip('"')
                if val.lower() == "null": val = ""
            ordered_row[col] = val if val is not None else ""
        data.append(ordered_row)
    return data


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
