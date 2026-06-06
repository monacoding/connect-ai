#!/usr/bin/env python3
# korean_analyze_v1 — 국어 문항·영역 분석
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "korean_analyze.json"
DEFAULT_DB = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/국어"

CONCEPT_MAP = {
    "화법": ["화법", "발표", "토론", "대화", "강연", "면담", "인터뷰"],
    "작문": ["작문", "서술", "요약", "개요", "글쓰기", "논술"],
    "언어": ["문법", "음운", "형태", "통사", "표기", "어법", "단어", "문장"],
    "문학": ["화자", "시어", "운율", "서사", "인물", "소설", "시", "수필", "표현"],
    "독서": ["주장", "근거", "추론", "요지", "관계", "비문학", "도표", "통계"],
}


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def tag_concepts(text: str, area: str) -> list[str]:
    found = []
    for concept in CONCEPT_MAP.get(area, []):
        if concept in text:
            found.append(concept)
    return found[:5]


def main() -> int:
    cfg = load_config()
    db_dir = Path(cfg.get("DB_DIR") or DEFAULT_DB)
    jsonl_path = db_dir / "datasets" / "questions.jsonl"
    if not jsonl_path.exists():
        print(f"❌ {jsonl_path} 없음 — korean_db_build 먼저 실행")
        return 1

    rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    area_counter = Counter()
    year_counter = Counter()
    analyzed = []

    for row in rows:
        area = row.get("area") or "독서"
        text = row.get("text_preview", "")
        concepts = tag_concepts(text, area)
        row["concepts"] = concepts
        row["study_priority"] = "high" if len(concepts) >= 2 else "medium"
        analyzed.append(row)
        area_counter[area] += 1
        if row.get("year"):
            year_counter[row["year"]] += 1

    analysis = {
        "subject": "국어",
        "total_blocks": len(analyzed),
        "by_area": dict(area_counter),
        "by_year": dict(year_counter),
        "top_concepts": {},
        "study_focus": [],
    }
    for area, keywords in CONCEPT_MAP.items():
        hits = Counter()
        for row in analyzed:
            if row.get("area") == area:
                for c in row.get("concepts", []):
                    hits[c] += 1
        if hits:
            analysis["top_concepts"][area] = hits.most_common(5)

    focus = []
    for area, count in area_counter.most_common():
        focus.append(f"{area} ({count}문항 블록) — {CONCEPT_MAP.get(area, [''])[0]} 등 개념 복습")
    analysis["study_focus"] = focus

    out_path = db_dir / "analysis.json"
    out_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in analyzed:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("📖 한설 — 국어 분석 완료")
    print(f"  영역별: {dict(area_counter)}")
    print(f"  학년도: {dict(year_counter)}")
    print(f"📄 {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
