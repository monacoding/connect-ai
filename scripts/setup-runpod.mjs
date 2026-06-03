#!/usr/bin/env node
/**
 * RunPod GPU LLM → Connect AI (Cursor/VS Code) 전역 설정
 *
 * 1) .env.runpod 파일을 채우거나 환경변수를 export
 * 2) npm run setup:runpod
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
    const key = t.slice(0, i).trim();
    let val = t.slice(i + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[key] = val;
  }
  return out;
}

function detectEngineType(url) {
  const u = url.toLowerCase();
  if (u.includes('/v1') || u.includes(':1234') || u.includes('-8000.')) return 'openai';
  return 'ollama';
}

function normalizeUrl(url, engineType) {
  let u = url.trim().replace(/\/+$/, '');
  if (engineType === 'openai' && !u.endsWith('/v1')) u += '/v1';
  return u;
}

function cursorSettingsPath() {
  const home = os.homedir();
  if (process.platform === 'darwin') {
    return path.join(home, 'Library/Application Support/Cursor/User/settings.json');
  }
  if (process.platform === 'win32') {
    return path.join(process.env.APPDATA || path.join(home, 'AppData', 'Roaming'), 'Cursor/User/settings.json');
  }
  return path.join(home, '.config/Cursor/User/settings.json');
}

function mergeSettings(filePath, patch) {
  let current = {};
  if (fs.existsSync(filePath)) {
    try {
      current = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (e) {
      console.error(`기존 settings.json 파싱 실패: ${e.message}`);
      process.exit(1);
    }
  }
  const next = { ...current, ...patch };
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(next, null, 4) + '\n', 'utf8');
}

const envFromFile = loadEnvFile(path.join(projectRoot, '.env.runpod'));
const env = { ...envFromFile, ...process.env };

const rawUrl = (env.RUNPOD_LLM_URL || env.OLLAMA_URL || '').trim();
const model = (env.RUNPOD_MODEL || env.OLLAMA_MODEL || '').trim();
const apiKey = (env.RUNPOD_API_KEY || env.RUNPOD_API_TOKEN || env.LLM_API_KEY || '').trim();
const engineHint = (env.RUNPOD_ENGINE || env.LLM_ENGINE || 'auto').trim().toLowerCase();
const timeoutSec = Number(env.RUNPOD_REQUEST_TIMEOUT || env.REQUEST_TIMEOUT || 600);

if (!rawUrl) {
  console.error(`
RunPod URL이 없습니다.

1) ${path.join(projectRoot, '.env.runpod.example')} 를 .env.runpod 로 복사
2) RunPod Pod → Connect → HTTP Service 에서 프록시 URL 복사
3) npm run setup:runpod

예 (Ollama on RunPod, 포트 11434):
  RUNPOD_LLM_URL=https://xxxxxxxx-11434.proxy.runpod.net
  RUNPOD_MODEL=llama3.2

예 (vLLM / OpenAI 호환, 포트 8000):
  RUNPOD_LLM_URL=https://xxxxxxxx-8000.proxy.runpod.net
  RUNPOD_ENGINE=openai
  RUNPOD_MODEL=your-model-id
`);
  process.exit(1);
}

const engineType = engineHint === 'openai' || engineHint === 'vllm' || engineHint === 'lmstudio'
  ? 'openai'
  : engineHint === 'ollama'
    ? 'ollama'
    : detectEngineType(rawUrl);

const ollamaUrl = engineType === 'openai' ? normalizeUrl(rawUrl, 'openai') : rawUrl.replace(/\/+$/, '');

const patch = {
  'connectAiLab.ollamaUrl': ollamaUrl,
  'connectAiLab.requestTimeout': Number.isFinite(timeoutSec) ? timeoutSec : 600,
  'connectAiLab.streamFirstTokenTimeoutSec': Math.max(240, Number(env.STREAM_FIRST_TOKEN_TIMEOUT || 480)),
};

if (model) patch['connectAiLab.defaultModel'] = model;
if (apiKey) patch['connectAiLab.llmApiKey'] = apiKey;

const settingsPath = cursorSettingsPath();
mergeSettings(settingsPath, patch);

console.log('Connect AI RunPod 설정 완료');
console.log(`  settings: ${settingsPath}`);
console.log(`  connectAiLab.ollamaUrl = ${ollamaUrl}`);
console.log(`  engine = ${engineType === 'openai' ? 'OpenAI-compatible (/v1)' : 'Ollama (/api)'}`);
if (model) console.log(`  connectAiLab.defaultModel = ${model}`);
if (apiKey) console.log('  connectAiLab.llmApiKey = (설정됨)');
console.log('\nCursor를 Reload Window 한 뒤 Connect AI 채팅을 사용하세요.');
console.log('연결 확인: Cmd+Shift+P → "Connect AI: Diagnose Connection"');
