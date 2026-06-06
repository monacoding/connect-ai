# 코다리 — 수능 데이터베이스·PDF 파이프라인 스킬

## 역할 분담

| 담당 | 작업 |
|------|------|
| **원영 (crawler)** | `kice_pdf_fetch`로 기출 PDF 다운로드 |
| **코다리 (developer)** | 폴더 구조, manifest 검증, DB 스크립트·파이프라인 |
| **suneung / 한설** | PDF 분석·커리큘럼·학습 가이드 |

## PDF 다운로드 — 코다리가 하지 않는 것

- `kice.re.kr/sub/info.do` 직접 fetch ❌
- `page_fetcher` / `web_search`로 PDF 받기 ❌
- 서드파티 사이트(호랭이, 티스토리) 링크 수집 ❌

→ 사용자가 "수능 PDF 받아줘" 하면 **원영에게 `kice_pdf_fetch` 실행 요청**.

## 데이터베이스 구조

```
데이터베이스/
├── manifest.json          # 원영 kice_pdf_fetch 출력
├── 2025_수학_...pdf
├── 2026_국어_...pdf
└── 국어/                  # 한설 파이프라인
    ├── pdfs/
    ├── markdown/
    ├── datasets/questions.jsonl
    └── study_guides/latest.md
```

## 코다리가 할 수 있는 것

1. `데이터베이스/` 폴더·하위 디렉터리 생성 (`mkdir -p`)
2. `manifest.json` 존재·항목 수 검증 (`python3 -c "import json; ..."`)
3. `kice_pdf_fetch.py` 버그 수정 (게시판 파싱, exit code, 페이지네이션)
4. suneung `source_ingest` / 한설 `korean_db_build` 파이프라인 연동

## kice_pdf_fetch 실행 (원영 도구, 코다리 디버깅용)

```bash
cd _agents/crawler/tools
python3 kice_pdf_fetch.py --year 2025 --subject 수학
python3 kice_pdf_fetch.py --year 2024   # 12페이지 자동 탐색
```

- `SKIP duplicate` / `INFO 이미 수집됨` = **성공** (이미 받은 파일)
- `WARN 0건` + exit 1 = 진짜 실패

## 검증 체크리스트

- [ ] `데이터베이스/manifest.json` items ≥ 1
- [ ] PDF 파일 크기 > 10KB (빈 파일 아님)
- [ ] 연도·영역 필터와 manifest 항목 일치

## 원영 실패 시 코다리 복구 절차 (필수)

1. **원인 1 — `--year` 누락** (가장 흔함)
   - 증상: 2024~2026만 SKIP, 요청 연도(예: 2023) 안 받음
   - 해결: `python3 kice_pdf_fetch.py --year 2023`

2. **원인 2 — exit 1인데 이미 있음**
   - 증상: `SKIP duplicate` + exit 1
   - 해결: 도구 v3+ 업데이트 (이미 수집됨 = 성공)

3. **원인 3 — 과거 연도 0건**
   - 증상: `WARN 2024학년도 PDF 0건`
   - 해결: `--year 2024` (12페이지 자동 탐색, 1페이지만 보면 실패)

4. **원인 4 — web_search로 PDF 시도**
   - 해결: `kice_pdf_fetch`만 사용

### 복구 도구

```bash
cd _agents/developer/tools
# kice_pdf_repair.json 에 SUNEUNG_YEAR 설정 후
python3 kice_pdf_repair.py
```

### 코다리 자동 에스컬레이션

원영 PDF 실패 → 시스템이 코다리 `kice_pdf_repair` 자동 실행 → 성공 시 파일 목록만 보고.
