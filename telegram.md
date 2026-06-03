# 텔레그램 ↔ Connect-AI 연결

## 1. 봇 만들기 (2분)
1. 텔레그램 **@BotFather** → `/newbot`
2. 토큰 저장 (`123456:AAE...`)
3. 만든 봇에게 **`/start`** 메시지 1회

## 2. 맥에서 연결

```bash
cd "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai"
TELEGRAM_BOT_TOKEN=여기에_토큰 npm run setup:telegram
```

## 3. 사용 방법 (둘 중 하나)

| 방식 | 조건 |
|------|------|
| **A. Cursor + Connect-AI** | Cursor 켜두기 → 비서가 텔레그램 자동 수신 (권장) |
| **B. 백그라운드 브리지** | `npm run telegram:bridge` → Cursor 없이 RunPod로 답변 |

## 4. 텔레그램에서 할 수 있는 것

- "진행중인 프로젝트 뭐야?"
- "할일 뭐 있어?" (Connect-AI 비서 모드)
- `일지: 오늘 RunPod 연결 완료` → journal.md 기록 (브리지 모드)
- `/help` `/status` `/projects`

## 설정 파일 위치
`~/AI_BRAIN/_company/_agents/secretary/tools/telegram_setup.json` (git 제외)
