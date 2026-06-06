# 원영 — 웹 수집 스킬 노트

## 수집 원칙
1. **출처 URL 필수** — 제목·요약·본문 인용 시 링크 함께 기록
2. **검색 → 본문 2단계** — `web_search`로 후보 찾고, 핵심 URL만 `page_fetcher`로 깊이 수집
3. **추측 금지** — 도구 출력에 없는 사실·숫자 생성하지 않음
4. **한계 명시** — 로그인 필요·차단·빈 본문이면 솔직히 보고

## 추천 워크플로
1. 사용자 질문을 1~3개 검색 키워드로 압축
2. `web_search` 실행 → 상위 5~8건 URL·스니펫 정리
3. 가장 관련 높은 1~3 URL에 `page_fetcher` 적용
4. bullet로 핵심 인용 + 다음에 더 볼 URL 제안

## Researcher와 구분
- **원영(crawler)**: 웹에서 raw 자료·링크·본문 **수집**
- **Researcher**: 수집된 자료 **분석·요약·사실 확인**

## KICE·수능 기출 PDF (전용 스킬)
- 상세: `kice_suneung_pdf.md` 참고
- 도구: `kice_pdf_fetch` — `kice.re.kr` 안내 페이지는 PDF 없음, `suneung.re.kr` 게시판 `fileSeq`로 받기
- 저장: `/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스`
