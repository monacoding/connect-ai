# 한설 — 수능 국어 전문 스킬

## 5개 영역

| 영역 | 선택과목 | 핵심 |
|------|----------|------|
| 화법 | 화법과 작문 | 발표·토론·대화·강연 담화 분석 |
| 작문 | 화법과 작문 | 서술·요약·글쓰기 과정 |
| 언어 | 언어와 매체 | 문법·표기·음운·통사 |
| 문학 | 공통+선택 | 시·소설·수필, 화자·서사·표현 |
| 독서 | 공통(비문학) | 주장·근거·추론·도표 |

## DB 위치

`/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/국어/`

## 파이프라인 (순서)

1. `korean_db_build` — 기출 PDF → markdown + questions.jsonl
2. `korean_resource_collect` — 웹 학습 자료 → resources.jsonl
3. `korean_analyze` — 영역·개념 분석 → analysis.json
4. `korean_study_guide` — 학습 가이드 → study_guides/latest.md

## PDF 없을 때

원영에게 `kice_pdf_fetch --year 2025 --subject 국어` 요청 후 1번 재실행.

## 산출물

- `study_guides/latest.md` — 사장님께 보고할 학습 정리
- `analysis.json` — 영역별 통계·개념 빈도
