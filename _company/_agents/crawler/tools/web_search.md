# 🔎 웹 검색 (web_search)

DuckDuckGo HTML API로 웹을 검색합니다. **API 키 불필요.**

## 어떻게 도와주나요?
- 검색어에 맞는 상위 결과 N건 수집 (제목·URL·스니펫)
- CEO·원영이 "자료 찾아줘" 요청 시 1차 수집용
- 결과 URL을 `page_fetcher`로 이어서 본문 추출 가능

## 설정값 (web_search.json)
- `QUERY` — 검색어 (비우면 실행 인자 사용)
- `MAX_RESULTS` — 최대 결과 수 (기본 8)

## 사용 예
- "2026 AI 에이전트 트렌드 자료 찾아줘"
- "원영아 수능 기출 PDF 사이트 검색해줘"
