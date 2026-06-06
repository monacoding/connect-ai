#!/usr/bin/env python3
# page_fetcher_v1
"""Page Fetcher — URL 본문 텍스트 추출."""
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).parent
CONFIG = HERE / "page_fetcher.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def load_config() -> dict:
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def strip_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<noscript[\s\S]*?</noscript>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    text = unescape(html)
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    cfg = load_config()
    url = (cfg.get("URL") or "").strip()
    if not url and len(sys.argv) > 1:
        url = sys.argv[1].strip()
    if not url:
        print("❌ URL이 비어있어요. page_fetcher.json의 URL에 주소를 넣거나 인자로 전달하세요.")
        return 1

    max_chars = int(cfg.get("MAX_CHARS") or 8000)
    req = Request(url, headers={"User-Agent": UA})
    try:
        with urlopen(req, timeout=30) as r:
            ctype = (r.headers.get("Content-Type") or "").lower()
            raw = r.read()
            enc = "utf-8"
            if "charset=" in ctype:
                enc = ctype.split("charset=")[-1].split(";")[0].strip() or "utf-8"
            html = raw.decode(enc, errors="replace")
    except Exception as e:
        print(f"❌ 페이지 fetch 실패: {e}")
        return 1

    text = strip_html(html)[:max_chars]
    print(f"📄 **{url}**")
    print(f"_(본문 {len(text)}자 추출 · 최대 {max_chars}자)_\n")
    print(text)
    if len(text) >= max_chars:
        print(f"\n… _(잘림 — MAX_CHARS={max_chars})_")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
