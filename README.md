<p align="center">
  <img src="assets/icon.png" width="120" alt="Connect AI Logo" />
</p>

<h1 align="center">Connect AI v2 (P-Reinforce)</h1>

<p align="center">
  <strong>OpenAI API · Autonomous Knowledge Engine</strong><br/>
  VS Code / Cursor 확장 프로그램으로, 당신의 낡은 IDE를 최상위 에이전트 대학(A.U)의 심장으로 진화시킵니다.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.1.30-blue" alt="version" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license" />
  <img src="https://img.shields.io/badge/integration-Agent_University-purple" alt="integration" />
  <img src="https://img.shields.io/badge/engine-OpenAI%20API-orange" alt="engine" />
</p>

---

## 🌟 Overview: The P-Reinforce Architecture

Connect AI v2.1.30은 단순한 코딩 에이전트를 넘어섭니다. **P-Reinforce 아키텍처**를 기반으로 설계된 이 에이전트는 사용자의 모든 정보와 지시를 받아들여 **스스로 의미를 분석하고, 폴더를 생성하고, 마크다운 위키 파일로 정리하여 클라우드에 자동 백업**하는 자율 지식 정원사(Autonomous Gardener)입니다.

---

## ⚡ Core Features

### 1. 🧠 Agent University (A.U) 완벽 연동
Agent University 웹 플랫폼과 실시간으로 통신합니다. 
웹에서 버튼 한 번 누르는 즉시, 로컬 VS Code의 `4825` 포트를 통해 프리미엄 브레인 팩(Premium Brain Pack) 지식이 로컬 인공지능 뇌(`~/.connect-ai-brain`)에 자동 주입되어 신경망을 확장합니다.

### 2. 📂 자율 지식 구조화 (Zero-Interaction Styling)
유저가 던져주는 원시 데이터(Raw Data)를 에이전트가 스스로 판단해 `10_Wiki`, `00_Raw`, `🚀 Skills` 와 같은 완벽한 P-Reinforce 템플릿 규격의 Markdown 파일로 분할-조립하여 저장합니다.

### 3. ☁️ 클라우드 동기화 (Auto-Git Sync 100%)
로컬 PC에서 파일 생성이 일어나는 순간, 에이전트가 스스로 GitHub 저장소에 `git add`, `commit`, `push`를 수행합니다. 
마스터는 이제 지루한 푸시 커맨드를 입력할 필요가 없습니다.

### 4. 🔗 OpenAI API 기반 모델 라우팅
Connect AI는 기본적으로 OpenAI API(`https://api.openai.com/v1`)와 `gpt-5.1` 모델을 사용합니다. API 키만 설정하면 모든 채팅·에이전트·자동화 호출이 외부 API로 처리됩니다.

---

## ⚒️ Agent Capabilities (에이전트 권한)

로컬 머신의 파일 시스템과 터미널에 대한 통제권을 인공지능에게 부여합니다. (100% 안전한 권한 승인 기반)

| Action | Description |
|:--|:--|
| **📄 Create Files** | 새로운 파일과 폴더를 생성합니다 |
| **✏️ Edit Files** | 기존 파일 내의 코드를 수정합니다 |
| **🗑️ Delete Files** | 불필요한 파일을 즉각 파쇄합니다 |
| **📖 Read Files** | 마스터의 프로젝트 파일을 읽어 맥락을 파악합니다 |
| **📂 Browse Directories** | 디렉토리 구조를 분석합니다 |
| **🖥️ Run Commands** | `npm run build`, `git push` 등 터미널 명령을 수행합니다 |

---

## 📥 Installation (설치 방법)

개발자가 현재 코드 구조를 빠르게 파악해야 한다면 [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)를 먼저 읽으세요.
사무실 화면의 좌표·구역명·배경을 바꾸려면 [OFFICE_LAYOUT_GUIDE.md](OFFICE_LAYOUT_GUIDE.md)를 참고하세요.

### A.U 멤버십 유저 (Recommended)
1. 상단 탭의 [Releases](https://github.com/wonseokjung/connect-ai/releases) 메뉴로 진입.
2. 최신 `v2.1.30.vsix` 파일을 다운로드.
3. VS Code 에서 `Cmd+Shift+P` → **Extensions: Install from VSIX** → 다운받은 파일 선택

### 개발자 빌드 (Build from Source)
```bash
git clone https://github.com/wonseokjung/connect-ai.git
cd connect-ai
npm install
npm run compile
npx vsce package
```

---

## ⚙️ Engine Setup (엔진 설정 방법)

### ✅ OpenAI API
1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키를 발급합니다.
2. VS Code 설정의 `connectAiLab.llmApiKey`에 키를 입력하거나 환경변수 `OPENAI_API_KEY`를 설정합니다.
3. 기본 서버 주소는 `https://api.openai.com/v1`, 기본 모델은 `gpt-5.1`입니다.

---

## 🔒 Privacy

- LLM 추론은 OpenAI API로 전송됩니다. 민감한 데이터는 전송 전 회사 정책에 맞게 검토하세요.
- 로컬 지식 파일과 회사 상태는 사용자가 지정한 두뇌 폴더에 저장됩니다.

---

<p align="center">
  <strong>Built for Antigravity & Agent University</strong><br/>
  Designed by <a href="https://github.com/wonseokjung">Jay</a> × Connect AI Architect
</p>
