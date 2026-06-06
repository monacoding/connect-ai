# Connect AI Development Guide

이 문서는 현재 저장소 구조를 빠르게 파악하고, 다음 수정 작업에서 어디를 먼저 봐야 하는지 정리한 개발 지도입니다.

## Summary

- 이 저장소는 `connect-ai-lab` VS Code 확장 프로젝트입니다.
- 런타임 진입점은 `package.json`의 `main: ./out/extension.js`, 소스 진입점은 `src/extension.ts`입니다.
- 현재 구조는 "큰 단일 확장 파일 + 일부 분리 모듈" 형태입니다. `src/extension.ts`가 대부분의 기능을 담고, `src/agents.ts`, `src/paths.ts`, `src/system-specs.ts`가 핵심 공용 정의를 일부 분리합니다.
- 빌드는 `npm run compile`로 실행하며, 내부적으로 `esbuild src/extension.ts --bundle --platform=node --external:vscode --outfile=out/extension.js`를 수행합니다.

## Key Structure

### `package.json`

- VS Code 확장 메타데이터, activation event, 명령어, 사이드바 webview, 설정 스키마를 정의합니다.
- 주요 설정 키:
  - `connectAiLab.ollamaUrl`
  - `connectAiLab.llmApiKey`
  - `connectAiLab.pythonPath`
  - `connectAiLab.defaultModel`
  - `connectAiLab.requestTimeout`
  - `connectAiLab.localBrainPath`
  - `connectAiLab.secondBrainRepo`
  - `connectAiLab.companyDir`
  - `connectAiLab.companyRepo`
  - `connectAiLab.dailyBriefingTime`
  - `connectAiLab.secretaryBridgeMode`

### `src/extension.ts`

확장 활성화, HTTP 브릿지 서버, 채팅/오피스/대시보드 webview, 에이전트 실행, Telegram, Google Calendar, PayPal, YouTube, tracker, Git 동기화 로직이 집중된 핵심 파일입니다.

`activate()`에서 주로 수행하는 일:

- 기존 사용자 데이터 마이그레이션
- 회사/두뇌 폴더 구조 보장
- OpenAI API 모델 설정 보정
- `SidebarChatProvider` 생성
- auto-cycle, Telegram polling, tracker nudge, daily briefing, revenue watcher, report scheduler, recurrence, pre-alarm loop 시작
- `127.0.0.1:4825` HTTP bridge 서버 시작
- command palette 및 view command 등록

### `src/agents.ts`

- CEO 및 specialist 에이전트 정의를 관리합니다.
- 표시 이름, 역할, 색상, 전문 영역, tagline, persona, profile image, 정렬 순서를 포함합니다.
- 에이전트 추가/수정은 먼저 이 파일을 확인하고, 이후 prompt와 `buildSpecialistPrompt()` 영향 범위를 확인합니다.

### `src/paths.ts`

- 두뇌 폴더와 회사 폴더 경로 정책을 관리합니다.
- 기본 두뇌 폴더는 `~/.connect-ai-brain`입니다.
- 기본 회사 폴더는 `<brain>/_company`입니다.
- 경로 정책 변경은 Git 동기화, tracker, Telegram, dashboard 데이터 위치에 영향을 줄 수 있습니다.

### `src/system-specs.ts`

- 로컬 머신 사양과 모델 메모리 추정을 담당합니다.
- 모델 자동 오케스트레이션에서 사용자 머신이 감당 가능한 모델을 고르기 위해 사용됩니다.

### `assets/prompts/*`

- LLM system/user prompt 원본입니다.
- 주요 파일:
  - `system.md`
  - `ceo-planner.md`
  - `ceo-chat.md`
  - `ceo-report.md`
  - `confer.md`
  - `ceo-classifier.md`
  - `secretary-triage.md`
  - `secretary-telegram.md`
  - `skill-distill.md`
  - `decisions-extract.md`

### `assets/webview/*`

- dashboard, API panel, revenue dashboard, sidebar 관련 HTML/CSS/JS 자산입니다.
- Webview 변경 전에는 panel class의 `onDidReceiveMessage` contract와 자산 로딩 방식을 함께 확인해야 합니다.

### `scripts/*`

- RunPod, Telegram 설정 및 bridge 실행 보조 스크립트입니다.
- 주요 스크립트:
  - `setup-runpod.mjs`
  - `setup-telegram.mjs`
  - `telegram-bridge.mjs`
  - `cycle.js`

## Runtime Flow

1. VS Code가 시작되고 `onStartupFinished` activation event로 확장이 활성화됩니다.
2. `activate()`가 마이그레이션, 회사 구조 보장, 모델 자동 감지, `SidebarChatProvider` 초기화를 수행합니다.
3. 백그라운드 루프가 시작됩니다.
   - auto-cycle
   - Telegram polling
   - tracker nudge
   - daily briefing
   - revenue watcher
   - report scheduler
   - recurring task loop
   - pre-alarm loop
4. 로컬 HTTP bridge 서버가 `127.0.0.1:4825`에서 시작됩니다.
5. VS Code command와 webview provider가 등록됩니다.
6. 외부 웹/플랫폼은 HTTP bridge endpoint를 통해 확장과 통신합니다.
7. LLM 호출은 설정된 base URL의 OpenAI-compatible Chat Completions API로 정규화됩니다.
8. 사용자 지식과 회사 상태는 기본적으로 `~/.connect-ai-brain` 및 그 안의 `_company`에 저장됩니다.

## Public Interfaces

### VS Code Commands

명령은 `package.json > contributes.commands`와 `src/extension.ts`의 `registerCommand()`를 함께 확인해야 합니다.

주요 사용자 명령:

- `connect-ai-lab.newChat`
- `connect-ai-lab.openSettings`
- `connect-ai-lab.explainSelection`
- `connect-ai-lab.showBrainNetwork`
- `connect-ai-lab.changeCompanyDir`
- `connectAiLab.dashboard.open`
- `connectAiLab.apiConnections.open`
- `connectAiLab.revenueDashboard.open`
- `connectAiLab.diagnoseConnection`
- `connectAiLab.developer.scaffoldProject`

### Local HTTP Bridge

주요 endpoint:

- `GET /ping`
- `POST /api/exam`
- `POST /api/evaluate`
- `GET /api/evaluate-history`
- `POST /api/brain-inject`
- `POST /api/skill-inject`
- `POST /api/template-inject`

## Development Notes

- 구조 변경이나 버그 수정은 우선 `src/extension.ts`에서 실제 실행 흐름을 좁혀서 확인합니다.
- `ARCHITECTURE.md`는 Brain/GitHub 동기화 중심 문서이며, 현재 전체 코드 구조와는 일부 차이가 있습니다.
- `src/api/example.ts`는 `apiClient`를 import하지 않아 독립 사용 시 깨질 수 있는 예제 파일입니다. 현재 확장 핵심 경로에서 사용되는 파일로 보이지 않습니다.
- `out/extension.js`와 `.vsix`는 빌드 산출물입니다. 소스 변경은 `src/*`와 `assets/*`를 기준으로 합니다.
- 현재 워크트리에 기존 수정/추가 파일이 있을 수 있으므로, 작업 전 `git status --short`로 변경 범위를 확인합니다.

## Test Plan

구조 학습 검증:

- `npm run compile`로 번들 빌드가 되는지 확인합니다.
- `package.json`의 command/view/config 선언과 `activate()`의 등록 코드가 일치하는지 확인합니다.

기능 수정 전 기본 확인:

- LLM 연결 관련 변경: `connectAiLab.diagnoseConnection` 흐름 확인
- Webview 변경: 관련 `assets/webview/*`와 panel class의 message contract 확인
- 두뇌/회사 폴더 변경: `src/paths.ts`, `_getBrainDir()`, `getCompanyDir()`, Git sync 함수 영향 확인
- 에이전트 변경: `src/agents.ts`, prompt asset, `buildSpecialistPrompt()` 영향 확인

## Working Assumptions

- 이 문서는 개발용 구조 지도를 목표로 합니다.
- 새 기능 구현 전에 `src/extension.ts`에서 해당 기능군을 먼저 좁히고, 필요한 경우 작은 모듈로 분리하는 방향을 검토합니다.
- 문서 내용은 현재 코드 구조를 기준으로 하며, 기능별 상세 구현 절차는 해당 코드 섹션을 직접 확인해야 합니다.
