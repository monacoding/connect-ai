#!/usr/bin/env node
/**
 * OpenAI API → Connect AI (Cursor/VS Code) 전역 설정
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

function normalizeUrl(url) {
  let u = url.trim().replace(/\/+$/, '');
  if (!u.endsWith('/v1')) u += '/v1';
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

const rawUrl = (env.OPENAI_BASE_URL || 'https://api.openai.com/v1').trim();
const model = (env.OPENAI_MODEL || 'gpt-5.1').trim();
const apiKey = (env.OPENAI_API_KEY || env.LLM_API_KEY || '').trim();
const timeoutSec = Number(env.RUNPOD_REQUEST_TIMEOUT || env.REQUEST_TIMEOUT || 600);

if (!apiKey) {
  console.error(`
OpenAI API 키가 없습니다.

1) ${path.join(projectRoot, '.env.runpod.example')} 를 .env.runpod 로 복사
2) OPENAI_API_KEY=sk-... 값을 입력
3) npm run setup:runpod
`);
  process.exit(1);
}

const apiBaseUrl = normalizeUrl(rawUrl);

const patch = {
  'connectAiLab.ollamaUrl': apiBaseUrl,
  'connectAiLab.requestTimeout': Number.isFinite(timeoutSec) ? timeoutSec : 600,
  'connectAiLab.streamFirstTokenTimeoutSec': Math.max(240, Number(env.STREAM_FIRST_TOKEN_TIMEOUT || 480)),
};

if (model) patch['connectAiLab.defaultModel'] = model;
if (apiKey) patch['connectAiLab.llmApiKey'] = apiKey;

const settingsPath = cursorSettingsPath();
mergeSettings(settingsPath, patch);

console.log('Connect AI OpenAI API 설정 완료');
console.log(`  settings: ${settingsPath}`);
console.log(`  connectAiLab.ollamaUrl = ${apiBaseUrl}`);
console.log('  engine = OpenAI-compatible (/v1)');
if (model) console.log(`  connectAiLab.defaultModel = ${model}`);
if (apiKey) console.log('  connectAiLab.llmApiKey = (설정됨)');
console.log('\nCursor를 Reload Window 한 뒤 Connect AI 채팅을 사용하세요.');
console.log('연결 확인: Cmd+Shift+P → "Connect AI: Diagnose Connection"');
