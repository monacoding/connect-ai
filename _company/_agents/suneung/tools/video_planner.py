#!/usr/bin/env python3
# video_planner_v1
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen


def load_dotenv() -> dict:
    env = {}
    for base in [Path.cwd(), Path(__file__).resolve().parent]:
        for p in [base, *base.parents]:
            f = p / ".env"
            if f.exists():
                for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                    t = line.strip()
                    if not t or t.startswith("#") or "=" not in t:
                        continue
                    k, v = t.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
                return env
    return env


def chat(base_url: str, api_key: str, model: str, messages):
    body = json.dumps({"model": model, "messages": messages, "temperature": 0.4}, ensure_ascii=False).encode("utf-8")
    req = Request(base_url.rstrip("/") + "/chat/completions", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"]


def slug(text: str) -> str:
    text = re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", text).strip("-")
    return text[:60] or "suneung-video"


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "video_planner.json"
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    dot_env = load_dotenv()
    api_key = cfg.get("OPENAI_API_KEY") or dot_env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY가 필요합니다.")
    curriculum = json.loads(Path(cfg.get("CURRICULUM_JSON") or "_company/suneung/curriculum/curriculum.json").read_text(encoding="utf-8"))
    prompt = {"curriculum": curriculum, "target_duration_minutes": cfg.get("TARGET_DURATION_MINUTES", 8), "channel_style": cfg.get("CHANNEL_STYLE", "수능 개념 교육 채널"), "rules": ["저작권 있는 수능 원문을 길게 낭독하지 말고 개념 설명과 풀이 전략 중심으로 구성", "script_md, shotlist_md, metadata_json 세 키를 가진 JSON만 출력", "metadata_json에는 title, description, tags, categoryId=27, privacyStatus=private 포함"]}
    content = chat(cfg.get("OPENAI_BASE_URL") or dot_env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1", api_key, cfg.get("MODEL") or dot_env.get("OPENAI_MODEL") or "gpt-5.1", [{"role": "system", "content": "You create concise Korean YouTube education video production plans. Return valid JSON only."}, {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}])
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"script_md": content, "shotlist_md": "", "metadata_json": {"title": "수능 개념 강의", "tags": ["수능"], "categoryId": "27", "privacyStatus": "private"}}
    meta = parsed.get("metadata_json") or {}
    title = meta.get("title") or "수능 개념 강의"
    out_dir = Path(cfg.get("OUTPUT_DIR") or "_company/suneung/videos") / (time.strftime("%Y%m%d-") + slug(title))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "script.md").write_text(parsed.get("script_md", ""), encoding="utf-8")
    (out_dir / "shotlist.md").write_text(parsed.get("shotlist_md", ""), encoding="utf-8")
    (out_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
