#!/usr/bin/env python3
# curriculum_builder_v1
import json
import os
import sys
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
    body = json.dumps({"model": model, "messages": messages, "temperature": 0.2}, ensure_ascii=False).encode("utf-8")
    req = Request(base_url.rstrip("/") + "/chat/completions", data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"]


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "curriculum_builder.json"
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    dot_env = load_dotenv()
    api_key = cfg.get("OPENAI_API_KEY") or dot_env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY가 필요합니다.")
    dataset = Path(cfg.get("DATASET_PATH") or "_company/suneung/datasets/suneung_learning.jsonl")
    rows = []
    with dataset.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
            if len(rows) >= 80:
                break
    prompt = {"task": "수능/모의평가 문항 요약을 교과과정 기반 커리큘럼으로 구조화", "subject": cfg.get("SUBJECT", "auto"), "requirements": ["원문을 길게 재출력하지 말 것", "개념 태그, 성취기준 후보, 선수 개념, 영상 모듈 순서를 만들 것", "JSON만 출력할 것"], "rows": rows}
    content = chat(cfg.get("OPENAI_BASE_URL") or dot_env.get("OPENAI_BASE_URL") or "https://api.openai.com/v1", api_key, cfg.get("MODEL") or dot_env.get("OPENAI_MODEL") or "gpt-5.1", [{"role": "system", "content": "You are a rigorous Korean CSAT curriculum architect. Return valid JSON only."}, {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}])
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"raw_model_output": content}
    out_dir = Path(cfg.get("OUTPUT_DIR") or "_company/suneung/curriculum")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "curriculum.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "curriculum.md").write_text("# 수능 커리큘럼 초안\n\n```json\n" + json.dumps(parsed, ensure_ascii=False, indent=2) + "\n```\n", encoding="utf-8")
    print(f"WROTE {out_dir / 'curriculum.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
