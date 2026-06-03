# 🧭 CEO (Chief Executive Agent) 개인 메모리

_CEO 에이전트만 읽고 쓰는 개인 노트. 학습·교훈·자주 쓰는 패턴이 누적됩니다._

## 학습 기록

- [2026-06-03] 한국교육과정평가원 들어가서 2025년도 수능 문제 다운받아줘 → 보고서 sessions/2026-06-03T13-23/_report.md
- [2026-06-03] 현재 3가지 문제 발생: 1) auto_planner.py 실행 실패 2) trend_sniper.py 설정 미완료 3) Google Calendar 미연결. 각각 '명령 팔레트 → 회사 GitHub 연결' 영역에서 확인/수정 필요. 모든 항목을 24시간 내에 해결해주세요. → 보고서 sessions/2026-06-03T13-33/_report.md
- [2026-06-03] 문제 파악해봐 지금 → 보고서 sessions/2026-06-03T13-38/_report.md
- [2026-06-03] 직원들 이름 내가 지을게 → 보고서 sessions/2026-06-03T13-40/_report.md
- [2026-06-03] CEO 이름을 그냥 Mona 로 바꿔줘 → 보고서 sessions/2026-06-03T13-41/_report.md
- [2026-06-03] 자동으로 git hub 랑 동기화 되게 만들어줘 → 보고서 sessions/2026-06-03T13-42/_report.md
- [2026-06-03] ✦ Connect AI 오후 10:43 ⚠️ [GitHub Sync 실패] GitHub에 새로운 내용이 있어요. 먼저 받아온 후 다시 시도해주세요.  💡 메뉴 → 🧠 → '깃허브 동기화' 에서 수동 해결을 시도해보세요. (로컬 파일은 안전합니다)  이 문제 해결 해봐 → 보고서 sessions/2026-06-03T13-44/_report.md
- [2026-06-03] CEO 이름을 Mona 로 수정 → 보고서 sessions/2026-06-03T13-46/_report.md
- [2026-06-03] Connect AI 오후 10:46 ⚠️ [GitHub Sync 실패] GitHub에 새로운 내용이 있어요. 먼저 받아온 후 다시 시도해주세요.  💡 메뉴 → 🧠 → '깃허브 동기화' 에서 수동 해결을 시도해보세요. (로컬 파일은 안전합니다)  왜 자꾸 이 오류가 나오는지 문제 확인 및 분석 , 해결 → 보고서 sessions/2026-06-03T13-47/_report.md
- [2026-06-03] 필수 패키지 설치해줘 → 보고서 sessions/2026-06-03T13-50/_report.md
- [2026-06-03] python 필수 패키지 다 설치 하고, api 설정도해줘 → 보고서 sessions/2026-06-03T13-54/_report.md
- [2026-06-03] 현재직원들이 하고 있는상황 브리핑 → 보고서 sessions/2026-06-03T15-28/_report.md
- [2026-06-03] 수능 문제 다운로드 담당 직원을 찾아주세요. 현재 Researcher가 KEAA 웹사이트에서 2025 수능 문제 다운로드 중이며, 경로는 프로젝트 폴더 내 'downloads/' 디렉토리에 있습니다. 필요시 경로 재확인 요청드릴게요. → 보고서 sessions/2026-06-03T15-33/_report.md
- [2026-06-03] https://www.kice.re.kr/main.do?s=kice에서 수능 문제 다운로드해줘. 경로 확인 및 파일 존재 여부 점검 필요 → 보고서 sessions/2026-06-03T15-34/_report.md
- [2026-06-03] KEAA 수능 문제 다운로드 작업 재시작 요청. 제공된 URL: https://www.suneung.re.kr/boardCnts/list.do?boardID=1500234&m=0403&s=suneung&searchStr= . download_keaa.py 스크립트에 해당 URL 기반 크롤링/API 로직 구현 필요 → 보고서 sessions/2026-06-03T15-38/_report.md
- [2026-06-03] 나는 외부 api 랑 연결 하고 싶어 먼저 시범적으로 날씨 api 를 연결할래 → 보고서 sessions/2026-06-03T15-42/_report.md
- [2026-06-03] 현재 진행 중인 작업: 1. 수능 문제 다운로드 (download_keaa.py 스크립트 개발 중) 2. OpenWeatherMap API 연결 시도 (LLM 호출 실패)  확인 사항: - download_keaa.py의 크롤링 로직 완료 여부 - LM Studio에서 모델 로드 실패 원인 (메모리/서버 상태/컨텍스트 길이) - .env 파일의 API 키 설정 상태  추천 조치: 1. LM Studio에서 작은 모델로 재시도 2. Ollama/LM Studio 서버 실행 여부 확인 3. download_keaa.py의 URL 파라미