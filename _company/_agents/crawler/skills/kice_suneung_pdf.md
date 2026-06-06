# 원영 — KICE·수능 기출 PDF 수집 스킬 (검증됨)

## 🛑 절대 하지 말 것
- `page_fetcher`·`web_search`로 PDF 다운로드 시도 ❌
- `kice.re.kr/sub/info.do` URL을 직접 PDF로 받기 ❌
- JSON 설정 수정 없이 "다운로드 완료"라고만 말하기 ❌

## ✅ 반드시 할 것
수능·기출·PDF·KICE 요청 → **`kice_pdf_fetch` 도구 실행**

```bash
python3 kice_pdf_fetch.py --year 2025
python3 kice_pdf_fetch.py --year 2025 --subject 수학
```

## 작동 원리

1. 게시판 HTML → `fn_fileDown('fileSeq')` 파싱
2. `fileDown.do?fileSeq=` + 브라우저 UA + Referer → PDF 저장

게시판: `https://www.suneung.re.kr/boardCnts/list.do?boardID=1500234&m=0403&s=suneung`

## 저장 위치

`/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/`

- `{학년도}_{영역}_{파일명}.pdf`
- `manifest.json` — 수집 목록

## 학년도 매핑

| 사용자 표현 | SUNEUNG_YEAR |
|------------|--------------|
| 2025학년도 수능 | `2025` |
| 2024학년도 수능 | `2024` (게시판 **2페이지** — 1페이지만 보면 0건) |
| 2026 수능 | `2026` |

`--year` 지정 시 **최대 12페이지 자동 탐색** (v3+). 1페이지에는 2025·2026만 있음.

## exit code 해석 (중요)

- `DOWNLOADED` → 신규 다운로드 성공
- `SKIP duplicate` + `INFO 이미 수집됨` → **이미 받아둔 파일** (성공으로 보고)
- `WARN ... 0건` + exit 1 → 진짜 실패 (연도·영역·게시판 확인)

**절대** "0건 추가"만 보고 실패라고 하지 말 것 — `EXISTS`/`SKIP duplicate`면 manifest 경로 보고.

## 성공 사례

**2025학년도** (홀/짝 분리):
- `2025_수학_수학영역_문제지_홀수형.pdf`
- `2025_수학_수학영역_문제지_짝수형.pdf`
- `2025_수학_수학영역_정답표.pdf`

**2026학년도**:
- `2026_수학_수학영역_문제지.pdf`

## 실패 시 — 코다리에게 넘기기

원영이 2회 실패하면 **코다리(developer)** 가 `kice_pdf_repair`로 복구.
코다리에게 전달: 요청 연도, 원영 stdout, manifest 경로.

## 역할 분담

- **원영**: PDF 다운로드 (`kice_pdf_fetch` + `--year` 필수)
- **코다리**: 실패 진단·복구 (`kice_pdf_repair`)
- **suneung**: PDF 분석·커리큘럼 (`md_convert`)
