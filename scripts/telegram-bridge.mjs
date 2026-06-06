#!/usr/bin/env node
/**
 * 텔레그램 → AI_BRAIN + OpenAI API 브리지 (Cursor 꺼져 있을 때)
 * Cursor + Connect-AI 가 4825 포트로 떠 있으면 폴링하지 않음 (중복 방지).
 */
import fs from 'fs';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

function loadEnvFile(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const out = {};
  for (const line of fs.readFileSync(filePath, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const i = t.indexOf('=');
    if (i < 1) continue;
    let val = t.slice(i + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[t.slice(0, i).trim()] = val;
  }
  return out;
}

const env = {
  ...loadEnvFile(path.join(projectRoot, '.env.runpod')),
  ...loadEnvFile(path.join(projectRoot, '.env.telegram')),
  ...process.env,
};

const BRAIN_DIR = (env.AI_BRAIN_DIR || path.join(os.homedir(), 'AI_BRAIN')).replace(/^~/, os.homedir());
const CONFIG_PATH = path.join(BRAIN_DIR, '_company', '_agents', 'secretary', 'tools', 'telegram_setup.json');
const OFFSET_PATH = path.join(BRAIN_DIR, '.telegram_offset.json');
const LOCK_PATH = path.join(BRAIN_DIR, '.telegram_poll.lock');
const LOCK_TTL_MS = 15000;
const BRIDGE_URL = env.CONNECT_AI_BRIDGE || 'http://127.0.0.1:4825';

function readConfig() {
  if (!fs.existsSync(CONFIG_PATH)) return null;
  const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  const token = String(cfg.TELEGRAM_BOT_TOKEN || '').trim();
  const chatId = String(cfg.TELEGRAM_CHAT_ID || '').trim();
  if (!token || !chatId) return null;
  return { token, chatId };
}

function readOffset() {
  try {
    return JSON.parse(fs.readFileSync(OFFSET_PATH, 'utf8')).offset || 0;
  } catch {
    return 0;
  }
}

function writeOffset(offset) {
  fs.writeFileSync(OFFSET_PATH, JSON.stringify({ offset, ts: Date.now() }), 'utf8');
}

function tryLock() {
  const now = Date.now();
  try {
    if (fs.existsSync(LOCK_PATH)) {
      const data = JSON.parse(fs.readFileSync(LOCK_PATH, 'utf8'));
      if (data.pid !== process.pid && now - (data.heartbeat || 0) < LOCK_TTL_MS) return false;
    }
  } catch { /* stale */ }
  fs.writeFileSync(LOCK_PATH, JSON.stringify({ pid: process.pid, heartbeat: now }), 'utf8');
  return true;
}

function touchLock() {
  try {
    fs.writeFileSync(LOCK_PATH, JSON.stringify({ pid: process.pid, heartbeat: Date.now() }), 'utf8');
  } catch { /* ignore */ }
}

async function bridgeAlive() {
  try {
    const r = await fetch(`${BRIDGE_URL}/ping`, { signal: AbortSignal.timeout(2000) });
    const d = await r.json();
    return d?.app === 'connect-ai-bridge';
  } catch {
    return false;
  }
}

async function tgSend(token, chatId, text) {
  const chunks = [];
  let rem = text;
  while (rem.length > 3800) {
    chunks.push(rem.slice(0, 3800));
    rem = rem.slice(3800);
  }
  chunks.push(rem);
  for (const chunk of chunks) {
    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: chatId, text: chunk }),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.description || 'send failed');
  }
}

function loadBrainContext() {
  const files = ['profile.md', 'projects.md', 'ideas.md', 'learning.md'];
  const parts = [];
  for (const f of files) {
    const p = path.join(BRAIN_DIR, f);
    if (fs.existsSync(p)) {
      const body = fs.readFileSync(p, 'utf8').trim().slice(0, 2500);
      if (body) parts.push(`## ${f}\n${body}`);
    }
  }
  return parts.join('\n\n');
}

async function askExternalApi(userText) {
  const base = (env.OPENAI_BASE_URL || 'https://api.openai.com/v1').replace(/\/+$/, '');
  const model = env.OPENAI_MODEL || 'gpt-5.1';
  const apiKey = env.OPENAI_API_KEY || '';
  if (!apiKey) throw new Error('OPENAI_API_KEY 없음 — .env.runpod 또는 환경변수 확인');

  const brain = loadBrainContext();
  const system = `당신은 태형님의 개인 AI 비서입니다. 아래 AI_BRAIN 메모리를 참고해 한국어로 간결히 답하세요.\n\n${brain}`;
  const url = `${base}/chat/completions`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({
      model,
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: userText },
      ],
      stream: false,
      max_tokens: 1024,
      temperature: 0.4,
    }),
    signal: AbortSignal.timeout(Number(env.RUNPOD_REQUEST_TIMEOUT || 600) * 1000),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data?.error?.message || `OpenAI API ${res.status}`);
  return data?.choices?.[0]?.message?.content?.trim() || '(응답 없음)';
}

async function handleMessage(text) {
  const t = text.trim();
  if (/^\/(help|start)\b/i.test(t)) {
    return `🤖 태형 AI (텔레그램 브리지)

자연어로 질문하세요. 예:
• "진행중인 프로젝트 뭐야?"
• "오늘 일지에 ○○ 기록해줘"

명령:
/status — 연결 상태
/projects — projects.md 요약

Cursor가 켜져 있으면 Connect-AI 비서가 자동 처리합니다.`;
  }
  if (/^\/status\b/i.test(t)) {
    const cfg = readConfig();
    const bridge = await bridgeAlive();
    return `📡 상태\n• 브리지: ${bridge ? 'Connect-AI (4825)' : '독립 모드 (OpenAI API)'}\n• 모델: ${env.OPENAI_MODEL || 'gpt-5.1'}\n• 두뇌: ${BRAIN_DIR}\n• chat_id: ${cfg?.chatId || '?'}`;
  }
  if (/^\/projects\b/i.test(t)) {
    const p = path.join(BRAIN_DIR, 'projects.md');
    return fs.existsSync(p) ? fs.readFileSync(p, 'utf8').slice(0, 3500) : 'projects.md 없음';
  }
  if (/^일지\s*[:：]|^journal\s*[:：]/i.test(t)) {
    const note = t.replace(/^[^\s]+\s*[:：]\s*/, '').trim();
    const line = `\n## ${new Date().toISOString().slice(0, 10)}\n- (텔레그램) ${note}\n`;
    fs.appendFileSync(path.join(BRAIN_DIR, 'journal.md'), line, 'utf8');
    return `📝 journal.md 에 기록했습니다.\n${note}`;
  }
  return await askExternalApi(t);
}

async function pollOnce(cfg) {
  if (!(await bridgeAlive())) {
    console.log('[telegram-bridge] Connect-AI 미실행 → 독립 OpenAI API 모드');
  } else {
    return;
  }

  if (!tryLock()) return;
  touchLock();

  let offset = readOffset();
  const url = `https://api.telegram.org/bot${cfg.token}/getUpdates?offset=${offset}&timeout=25&allowed_updates=${encodeURIComponent(JSON.stringify(['message']))}`;
  const res = await fetch(url, { signal: AbortSignal.timeout(35000) });
  const data = await res.json();
  if (!data.ok) throw new Error(data.description);

  for (const u of data.result || []) {
    offset = u.update_id + 1;
    writeOffset(offset);
    const m = u.message;
    if (!m?.text) continue;
    if (String(m.chat?.id) !== cfg.chatId) continue;
    const text = m.text.trim();
    console.log(`[telegram-bridge] ← ${text.slice(0, 80)}`);
    try {
      await fetch(`https://api.telegram.org/bot${cfg.token}/sendChatAction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chat_id: cfg.chatId, action: 'typing' }),
      });
      const reply = await handleMessage(text);
      await tgSend(cfg.token, cfg.chatId, reply);
      console.log(`[telegram-bridge] → ${reply.slice(0, 60)}...`);
    } catch (e) {
      await tgSend(cfg.token, cfg.chatId, `⚠️ 오류: ${e.message}`);
    }
  }
}

async function main() {
  const cfg = readConfig();
  if (!cfg) {
    console.error(`설정 없음. 먼저: npm run setup:telegram\n  경로: ${CONFIG_PATH}`);
    process.exit(1);
  }

  console.log('텔레그램 브리지 시작');
  console.log(`  두뇌: ${BRAIN_DIR}`);
  console.log(`  Connect-AI 감지 시 자동 양보 (포트 4825)`);

  const loop = async () => {
    try {
      if (await bridgeAlive()) {
        await new Promise((r) => setTimeout(r, 5000));
        return;
      }
      await pollOnce(cfg);
    } catch (e) {
      console.error('[telegram-bridge]', e.message);
    }
  };

  setInterval(loop, 2000);
  await loop();
}

main();
