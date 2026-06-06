# kice_pdf_fetch

원영 전용 — KICE·수능 기출 PDF 수집. **수능 PDF 요청 시 이 도구만 사용.**

## 실행 (권장)

```bash
python3 kice_pdf_fetch.py --year 2025
python3 kice_pdf_fetch.py --year 2025 --subject 수학
```

## CLI 옵션

| 옵션 | 설명 |
|------|------|
| `--year` | 학년도 (예: 2025, 2026) |
| `--subject` | 영역 (예: 수학, 국어) — 비우면 해당 연도 전체 |
| `--output-dir` | 저장 폴더 (기본: 데이터베이스/) |

## 저장 위치

`/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/`

## 주의

- `kice.re.kr/sub/info.do` 에 PDF 없음
- `page_fetcher`로는 fileSeq 링크 추출 불가
