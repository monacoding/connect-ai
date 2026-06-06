# 🕸️ 원영 (Web Data Crawling Specialist) 개인 메모리

_원영 에이전트만 읽고 쓰는 개인 노트. 학습·교훈·자주 쓰는 패턴이 누적됩니다._

## 학습 기록

- [2026-06-06] 2025년 수리영역 수능 문제를 PDF로 다운로드할 수 있는 웹사이트를 조사하고, 다운로드 방법을 상세히 정리하세요. → 산출물 sessions/2026-06-06T04-18/crawler.md
- [2026-06-06] 웹에서 수능 문제의 다운로드 가능 여부 확인 및 필요한 URL 수집 → 산출물 sessions/2026-06-06T04-18/crawler.md
- [2026-06-06] 원영 에이전트에게 2025년 수능 문제 다운하라고 지시 → 산출물 sessions/2026-06-06T04-49/crawler.md
- [2026-06-06] 2025년 수능 수리영역 문제의 웹 다운로드 가능 여부와 URL을 조사하고, 필요한 방법을 상세히 정리하세요. → 산출물 sessions/2026-06-06T04-50/crawler.md
- [2026-06-06] 원영 에이전트 빼고 모든일 중단시켜 → 산출물 sessions/2026-06-06T04-51/crawler.md
- [2026-06-06] 원영아 2024년 수능 다운 → 산출물 sessions/2026-06-06T04-56/crawler.md
## 교훈 — 잘못된 수집 패턴 (2026-06-06 검토)
- ❌ `web_search "수능 다운로드 사이트"` → 호랭이·티스토리·네이버 블로그 등 **서드파티**만 나옴
- ❌ 공식 사이트(suneung.re.kr) 8위에 있어도 무시하고 블로그 URL 보고
- ❌ PDF 실제 다운로드 없이 "URL 조사"만 하고 완료 처리
- ✅ 수능 PDF → **kice_pdf_fetch.py --year <학년도>** 만 사용
- ✅ 공식 도메인: suneung.re.kr, kice.re.kr, ebsi.co.kr

- [2026-06-06] 원영아 24년도 다운 → 산출물 sessions/2026-06-06T04-59/crawler.md
## 학습 기록 — KICE·수능 PDF 수집 (2026-06-06)
- `kice_pdf_fetch` 필수. web_search로 PDF 찾지 말 것
- `SKIP duplicate` / `INFO 이미 수집됨` = 성공 (exit 0)
- 저장: 데이터베이스/ + manifest.json
