#!/usr/bin/env python3
# korean_db_build_v1 — 수능 국어 PDF·자료 → 국어 DB 구축
import json
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "korean_db_build.json"
DEFAULT_SOURCE_MANIFEST = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/manifest.json"
DEFAULT_OUTPUT = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/국어"


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf 필요: python3 -m pip install pypdf") from exc
    return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)


def normalize(text: str) -> str:
    text = text.replace("\u00a0", " ")
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


def split_questions(text: str) -> list[dict]:
    matches = list(re.finditer(r"(?m)^\s*(\d{1,2})\s*[.)]\s+", text))
    if not matches:
        return [{"question_id": "document", "text": text}]
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append({"question_id": m.group(1), "text": text[m.start():end].strip()})
    return out


def guess_area(text: str) -> str:
    t = text[:800]
    if re.search(r"화법|발표|토론|면담|대화|강연", t):
        return "화법"
    if re.search(r"작문|글쓰기|서술|논술|요약", t):
        return "작문"
    if re.search(r"문법|음운|형태|통사|표기|어법", t):
        return "언어"
    if re.search(r"시의|운율|화자|시어|운|소설|인물|서사|수필|문학", t):
        return "문학"
    return "독서"


def is_korean_pdf(path: Path) -> bool:
    name = path.name
    return "국어" in name and path.suffix.lower() == ".pdf"


def main() -> int:
    cfg = load_config()
    source_manifest = Path(cfg.get("SOURCE_MANIFEST") or DEFAULT_SOURCE_MANIFEST)
    out_dir = Path(cfg.get("OUTPUT_DIR") or DEFAULT_OUTPUT)
    pdf_dir = out_dir / "pdfs"
    md_dir = out_dir / "markdown"
    dataset_dir = out_dir / "datasets"
    for d in (pdf_dir, md_dir, dataset_dir):
        d.mkdir(parents=True, exist_ok=True)

    items = []
    if source_manifest.exists():
        items = json.loads(source_manifest.read_text(encoding="utf-8")).get("items", [])

    korean_items = []
    for item in items:
        p = Path(item.get("local_path", ""))
        if p.exists() and is_korean_pdf(p):
            korean_items.append(item)

    # 로컬 pdfs 폴더 직접 스캔
    parent_db = out_dir.parent
    for p in sorted(parent_db.glob("*국어*.pdf")):
        if any(Path(i.get("local_path", "")) == p for i in korean_items):
            continue
        korean_items.append({"local_path": str(p), "source_url": "", "title": p.name})

    manifest_items = []
    question_rows = []
    print(f"📖 한설 — 국어 DB 구축 → {out_dir}")

    for item in korean_items:
        src = Path(item["local_path"])
        dest = pdf_dir / src.name
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
        raw = read_pdf(dest)
        text = normalize(raw)
        year_m = re.search(r"(20\d{2})", src.name)
        year = year_m.group(1) if year_m else ""
        kind = "정답표" if "정답" in src.name else "문제지"
        md_path = md_dir / f"{dest.stem}.md"
        md_path.write_text(
            f"# {dest.stem}\n\n- year: {year}\n- kind: {kind}\n- source: {item.get('source_url', '')}\n\n## Text\n\n{text}\n",
            encoding="utf-8",
        )
        manifest_items.append(
            {
                "file": str(dest),
                "markdown": str(md_path),
                "year": year,
                "kind": kind,
                "bytes": dest.stat().st_size,
                "sha256": item.get("sha256", ""),
            }
        )
        for q in split_questions(text):
            area = guess_area(q["text"])
            question_rows.append(
                {
                    "source_file": dest.name,
                    "year": year,
                    "question_id": q["question_id"],
                    "area": area,
                    "text_preview": re.sub(r"\s+", " ", q["text"])[:500],
                    "concepts": [],
                    "study_priority": "",
                    "review_status": "needs_analysis",
                }
            )
        print(f"  INDEXED {dest.name} ({len(text)} chars, {len(split_questions(text))} blocks)")

    areas = {
        "화법": "듣기·말하기, 발표·토론, 대화·강연 자료 분석",
        "작문": "글쓰기 과정, 서술·논술, 요약·개요",
        "언어": "문법, 음운·형태·통사, 표기·어법",
        "문학": "시·소설·수필, 화자·서사·표현",
        "독서": "비문학 독해, 논리·추론, 요지·관계",
    }
    (out_dir / "areas.json").write_text(json.dumps(areas, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "manifest.json").write_text(
        json.dumps({"subject": "국어", "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "items": manifest_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    jsonl_path = dataset_dir / "questions.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in question_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"✅ PDF {len(manifest_items)}건, 문항 블록 {len(question_rows)}건")
    print(f"📄 {out_dir / 'manifest.json'}")
    print(f"📄 {jsonl_path}")
    return 0 if manifest_items else 1


if __name__ == "__main__":
    raise SystemExit(main())
