#!/usr/bin/env python3
# web_search_v1
"""Web Search — DuckDuckGo HTML, API 키 불필요."""
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse, urlencode
from urllib.request import Request, urlopen

HERE = Path(__file__).parent
CONFIG = HERE / "web_search.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _resolve_href(href: str) -> str:
    if "uddg=" in href:
        try:
            qs = parse_qs(urlparse(href).query)
            if qs.get("uddg"):
                return unquote(qs["uddg"][0])
        except Exception:
            pass
    return href


def fetch_results(query: str, max_results: int) -> list:
    endpoint = "https://html.duckduckgo.com/html/"
    body = urlencode({"q": query}).encode("utf-8")
    req = Request(
        endpoint,
        data=body,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", errors="replace")

    results = []
    blocks = re.findall(
        r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    snippets = re.findall(
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    for i, (href, raw_title) in enumerate(blocks):
        title = re.sub(r"<[^>]+>", "", raw_title)
        title = unescape(title.strip())
        if not title:
            continue
        snippet = ""
        if i < len(snippets):
            snippet = re.sub(r"<[^>]+>", "", snippets[i])
            snippet = unescape(snippet.strip())
        results.append({"title": title, "url": _resolve_href(href), "snippet": snippet})
        if len(results) >= max_results:
            break
    return results


def main() -> int:
    cfg = load_config()
    query = (cfg.get("QUERY") or "").strip()
    if not query and len(sys.argv) > 1:
        query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("❌ QUERY가 비어있어요. web_search.json의 QUERY에 검색어를 넣거나 인자로 전달하세요.")
        return 1

    max_results = int(cfg.get("MAX_RESULTS") or 8)
    print(f"🔎 웹 검색: {query}")
    print(f"   (DuckDuckGo · 최대 {max_results}건)\n")

    try:
        results = fetch_results(query, max_results)
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return 1

    if not results:
        print("_(검색 결과 없음 — 쿼리를 바꿔보세요)_")
        return 0

    for i, row in enumerate(results, 1):
        print(f"### {i}. {row['title']}")
        print(f"- URL: {row['url']}")
        if row["snippet"]:
            print(f"- 요약: {row['snippet']}")
        print()

    print(f"✅ {len(results)}건 수집 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
