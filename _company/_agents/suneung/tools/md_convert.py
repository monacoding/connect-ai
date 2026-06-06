#!/usr/bin/env python3
# md_convert_v1
import json
import re
import sys
from pathlib import Path


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("PDF 추출에는 pypdf가 필요합니다: python3 -m pip install pypdf") from exc
    return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_questions(text: str):
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\s*[.)]\s+", text))
    if not matches:
        return [{"question_id": "document", "text": text}]
    return [{"question_id": m.group(1), "text": text[m.start():(matches[i + 1].start() if i + 1 < len(matches) else len(text))].strip()} for i, m in enumerate(matches)]


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "md_convert.json"
    cfg = load_config(config_path)
    manifest = json.loads(Path(cfg.get("INPUT_MANIFEST") or "_company/suneung/sources/manifest.json").read_text(encoding="utf-8"))
    output_dir = Path(cfg.get("OUTPUT_DIR") or "_company/suneung")
    md_dir = output_dir / "markdown"
    dataset_dir = output_dir / "datasets"
    md_dir.mkdir(parents=True, exist_ok=True)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    include_raw = str(cfg.get("INCLUDE_RAW_TEXT_IN_JSONL", "false")).lower() == "true"
    rows = []

    for item in manifest.get("items", []):
        path = Path(item["local_path"])
        raw = read_pdf(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8", errors="ignore")
        text = normalize(raw)
        (md_dir / f"{path.stem}.md").write_text(f"# {path.stem}\n\n- source_url: {item.get('source_url', '')}\n- sha256: {item.get('sha256', '')}\n- rights: 원문 저작권을 확인하고 허가 범위 내에서만 사용\n\n## Extracted Text\n\n{text}\n", encoding="utf-8")
        for q in split_questions(text):
            compact = re.sub(r"\s+", " ", q["text"]).strip()
            row = {"source_path": str(path), "source_url": item.get("source_url", ""), "source_sha256": item.get("sha256", ""), "question_id": q["question_id"], "text_summary": compact[:700], "curriculum_units": [], "concept_tags": [], "difficulty": "", "answer": "", "rationale": "", "review_status": "needs_human_review"}
            if include_raw:
                row["raw_text"] = q["text"]
            rows.append(row)

    jsonl_path = dataset_dir / "suneung_learning.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"WROTE {jsonl_path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
