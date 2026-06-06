#!/usr/bin/env python3
# korean_study_guide_v1 — 국어 학습 가이드 생성
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "korean_study_guide.json"
DEFAULT_DB = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/국어"

STUDY_TEMPLATE = """# 수능 국어 학습 가이드

생성: {date}
데이터: `{db}`

## 1. 영역별 현황

{area_summary}

## 2. 우선 공부할 것 (기출 기반)

{study_focus}

## 3. 영역별 핵심 개념

{concept_blocks}

## 4. 추천 학습 순서

1. **언어** — 문법·표기 기본 (틀리면 전 영역 감점)
2. **독서** — 비문학 지문 구조·추론 (시간 관리 핵심)
3. **문학** — 화자·서사·표현 장치 암기+적용
4. **화법** — 담화 유형·맥락 파악
5. **작문** — 서술·요약 실전 연습

## 5. 참고 자료 (DB)

- 기출 PDF: `pdfs/`
- 웹 자료: `resources.jsonl` (공식 도메인 우선)
- 문항 데이터: `datasets/questions.jsonl`

## 6. 다음 액션

- [ ] 부족한 영역 기출 추가 수집 (원영 → kice_pdf_fetch --year --subject 국어)
- [ ] korean_analyze 재실행으로 개념 태그 보강
- [ ] 오답 노트를 `study_notes/`에 누적
"""


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def main() -> int:
    cfg = load_config()
    db_dir = Path(cfg.get("DB_DIR") or DEFAULT_DB)
    analysis_path = db_dir / "analysis.json"
    areas_path = db_dir / "areas.json"
    if not analysis_path.exists():
        print("❌ analysis.json 없음 — korean_analyze 먼저 실행")
        return 1

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    areas = json.loads(areas_path.read_text(encoding="utf-8")) if areas_path.exists() else {}

    area_lines = []
    for area, count in (analysis.get("by_area") or {}).items():
        desc = areas.get(area, "")
        area_lines.append(f"- **{area}**: {count}블록 — {desc}")

    focus_lines = [f"- {s}" for s in analysis.get("study_focus", [])]

    concept_blocks = []
    for area, concepts in (analysis.get("top_concepts") or {}).items():
        if not concepts:
            continue
        items = ", ".join(f"{c}({n})" for c, n in concepts)
        concept_blocks.append(f"### {area}\n{items}\n")

    guide_dir = db_dir / "study_guides"
    guide_dir.mkdir(parents=True, exist_ok=True)
    guide_path = guide_dir / f"guide_{time.strftime('%Y%m%d')}.md"
    body = STUDY_TEMPLATE.format(
        date=time.strftime("%Y-%m-%d %H:%M"),
        db=str(db_dir),
        area_summary="\n".join(area_lines) or "_(데이터 없음)_",
        study_focus="\n".join(focus_lines) or "_(분석 후 생성)_",
        concept_blocks="\n".join(concept_blocks) or "_(개념 태그 후 생성)_",
    )
    guide_path.write_text(body, encoding="utf-8")
    latest = guide_dir / "latest.md"
    latest.write_text(body, encoding="utf-8")

    print(f"📖 한설 — 학습 가이드 생성")
    print(f"📄 {guide_path}")
    print(f"📄 {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
