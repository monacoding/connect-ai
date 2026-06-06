#!/usr/bin/env python3
# korean_resource_collect_v1 — 수능 국어 학습 자료 웹 수집
import importlib.util
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "korean_resource_collect.json"
DEFAULT_OUTPUT = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스/국어"

DEFAULT_QUERIES = [
    "수능 국어 화법과 작문 개념 정리 site:ebsi.co.kr",
    "수능 국어 언어와 매체 문법 site:kice.re.kr",
    "수능 국어 문학 화자 태도 분석",
    "수능 국어 비문학 독해 전략",
    "2015 개정 교육과정 국어 성취기준",
]

TRUSTED = ("kice.re.kr", "suneung.re.kr", "ebsi.co.kr", "ebs.co.kr", "ncic.re.kr")


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_web_search():
    candidates = [
        HERE.parent / "crawler" / "web_search.py",
        Path(__file__).resolve().parents[2] / "tool-seeds" / "crawler" / "web_search.py",
    ]
    for c in candidates:
        if not c.exists():
            continue
        spec = importlib.util.spec_from_file_location("web_search", c)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise RuntimeError("web_search.py not found")


def main() -> int:
    cfg = load_config()
    out_dir = Path(cfg.get("OUTPUT_DIR") or DEFAULT_OUTPUT)
    out_dir.mkdir(parents=True, exist_ok=True)
    queries = cfg.get("QUERIES") or DEFAULT_QUERIES
    if isinstance(queries, str):
        queries = [q.strip() for q in queries.splitlines() if q.strip()]
    max_per = int(cfg.get("MAX_RESULTS_PER_QUERY") or 5)

    ws = _load_web_search()
    rows = []
    seen_urls = set()

    print("📖 한설 — 국어 학습 자료 웹 수집")
    for query in queries:
        print(f"🔎 {query}")
        try:
            results = ws.fetch_results(query, max_per)
        except Exception as e:
            print(f"  WARN {e}")
            continue
        for r in results:
            url = r.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            trusted = any(d in url for d in TRUSTED)
            rows.append(
                {
                    "query": query,
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("snippet", ""),
                    "trusted": trusted,
                    "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
            tag = "✅" if trusted else "⚠️"
            print(f"  {tag} {r.get('title', '')[:60]}")

    resources_path = out_dir / "resources.jsonl"
    with resources_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    trusted_n = sum(1 for r in rows if r["trusted"])
    print(f"✅ {len(rows)}건 수집 (공식/준공식 {trusted_n}건) → {resources_path}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
