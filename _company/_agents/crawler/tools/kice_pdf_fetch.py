#!/usr/bin/env python3
# kice_pdf_fetch_v2 — 원영 전용 KICE/수능 기출 PDF 수집 (자체 완결)
import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "kice_pdf_fetch.json"
DEFAULT_OUTPUT = "/Users/gimtaehyeong/Desktop/태형/4. 코딩/connect-ai/데이터베이스"
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
DEFAULT_BOARD = "https://www.suneung.re.kr/boardCnts/list.do?boardID=1500234&m=0403&s=suneung"
FILE_DOWN = "https://www.suneung.re.kr/boardCnts/fileDown.do"


def load_config(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [value]
        except Exception:
            return [v.strip() for v in value.splitlines() if v.strip()]
    return []


def as_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_html(url: str, referer: str = "") -> str:
    headers = {"User-Agent": BROWSER_UA}
    if referer:
        headers["Referer"] = referer
    with urlopen(Request(url, headers=headers), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return cleaned or "downloaded_source"


def is_kice_info(url: str) -> bool:
    p = urlparse(url)
    return "kice.re.kr" in p.netloc.lower() and "/sub/info.do" in p.path


def is_board_list(url: str) -> bool:
    p = urlparse(url)
    return "suneung.re.kr" in p.netloc.lower() and "boardCnts/list.do" in p.path


def board_id(url: str) -> str:
    return (parse_qs(urlparse(url).query).get("boardID") or [""])[0]


def extract_board_links(html: str, base_url: str, allowed_ids: list[str]) -> list[str]:
    links: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(
        r"(?:https?:)?//www\.suneung\.re\.kr/boardCnts/list\.do\?[^\"'\s<>]+",
        html,
    ):
        href = match.group(0)
        if not href.startswith("http"):
            href = "https://" + href.lstrip("/").lstrip(":")
        if href in seen:
            continue
        if allowed_ids and board_id(href) not in allowed_ids:
            continue
        seen.add(href)
        links.append(href)
    for match in re.finditer(r'href=["\']([^"\']*boardCnts/list\.do[^"\']*)["\']', html):
        href = urljoin(base_url, match.group(1))
        if "suneung.re.kr" not in href or href in seen:
            continue
        if allowed_ids and board_id(href) not in allowed_ids:
            continue
        seen.add(href)
        links.append(href)
    return links


def parse_board(html: str) -> list[dict]:
    tbody = re.search(r"<tbody>(.*?)</tbody>", html, re.S)
    if not tbody:
        return []
    entries: list[dict] = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1), re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 7:
            continue
        year = re.sub(r"<[^>]+>", "", cells[1]).strip()
        subject = re.sub(r"<[^>]+>", "", cells[2]).strip()
        for m in re.finditer(r"fn_fileDown\('([a-f0-9]+)'\)[^>]*title='([^']+)'", row):
            entries.append(
                {"file_seq": m.group(1), "title": m.group(2), "year": year, "subject": subject}
            )
    return entries


def board_page_url(board_url: str, page: int) -> str:
    parsed = urlparse(board_url)
    query = parse_qs(parsed.query)
    query["page"] = [str(page)]
    qs = "&".join(f"{k}={v[0]}" for k, v in query.items())
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{qs}"


def entry_filename(entry: dict) -> str:
    title = sanitize_filename(entry.get("title") or "file")
    year = sanitize_filename(entry.get("year") or "")
    subject = sanitize_filename(entry.get("subject") or "")
    if year and subject:
        return f"{year}_{subject}_{title}"
    return title


def match_entry(entry: dict, year: str, subject: str, extensions: list[str]) -> bool:
    if year and entry.get("year") != year:
        return False
    if subject and subject not in (entry.get("subject") or ""):
        return False
    if extensions:
        title = (entry.get("title") or "").lower()
        if not any(title.endswith(ext.lower()) for ext in extensions):
            return False
    return True


def collect_entries(board_url: str, max_pages: int, year_filter: str = "") -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    # 학년도 지정 시 1페이지(최신 2025·2026)만 보면 과거 연도 누락 → 자동으로 더 탐색
    scan_limit = max(max_pages, 12) if year_filter else max_pages
    found_target = False

    for page in range(1, scan_limit + 1):
        page_url = board_page_url(board_url, page)
        html = fetch_html(page_url, referer=board_url)
        rows = parse_board(html)
        if not rows:
            break
        page_years: list[int] = []
        for entry in rows:
            if entry["file_seq"] in seen:
                continue
            seen.add(entry["file_seq"])
            entry["page_url"] = page_url
            entry["board_url"] = board_url
            out.append(entry)
            if year_filter and entry.get("year") == year_filter:
                found_target = True
            y = (entry.get("year") or "").strip()
            if y.isdigit():
                page_years.append(int(y))

        if year_filter and found_target and page_years:
            # 게시판은 최신순 — 목표 연도를 지나 더 오래된 페이지만 남으면 중단
            if max(page_years) < int(year_filter):
                break
    return out


def download_file_seq(file_seq: str, dest: Path, referer: str) -> str:
    url = f"{FILE_DOWN}?fileSeq={file_seq}"
    headers = {"User-Agent": BROWSER_UA, "Referer": referer}
    with urlopen(Request(url, headers=headers), timeout=120) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)
    return url


def expand_urls(urls: list[str], cfg: dict) -> list[str]:
    allowed = as_list(cfg.get("SUNEUNG_BOARD_IDS", ["1500234"]))
    expanded: list[str] = []
    seen: set[str] = set()
    for raw in urls:
        url = raw.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        if is_kice_info(url):
            print(f"KICE_INFO_PAGE: {url} — PDF 없음, 수능 게시판 링크 추출")
            html = fetch_html(url)
            for link in extract_board_links(html, url, allowed):
                if link not in seen:
                    seen.add(link)
                    expanded.append(link)
            continue
        expanded.append(url)
    default_board = str(cfg.get("SUNEUNG_BOARD_URL") or DEFAULT_BOARD).strip()
    if not expanded:
        expanded.append(default_board)
    return expanded


def run_fetch(cfg: dict) -> int:
    out_dir = Path(cfg.get("OUTPUT_DIR") or DEFAULT_OUTPUT)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    existing = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8")).get("items", [])
    items = list(existing)
    seen = {x.get("sha256") for x in items if x.get("sha256")}

    year = str(cfg.get("SUNEUNG_YEAR") or "").strip()
    subject = str(cfg.get("SUNEUNG_SUBJECT") or "").strip()
    extensions = as_list(cfg.get("SUNEUNG_EXTENSIONS", [".pdf"])) or [".pdf"]
    max_pages = max(1, as_int(cfg.get("SUNEUNG_MAX_PAGES"), 1))

    print("🕸️ 원영 — KICE/수능 기출 PDF 수집")
    if year:
        print(f"📅 학년도 필터: {year}")
    if subject:
        print(f"📚 영역 필터: {subject}")
    print(f"📁 저장: {out_dir}")

    added = 0
    for board_url in expand_urls(as_list(cfg.get("SOURCE_URLS", [])), cfg):
        if not is_board_list(board_url):
            continue
        entries = collect_entries(board_url, max_pages, year)
        if not entries:
            print(f"WARN 게시판에 파일 없음: {board_url}")
            continue
        for entry in entries:
            if not match_entry(entry, year, subject, extensions):
                continue
            target = out_dir / entry_filename(entry)
            source_url = download_file_seq(entry["file_seq"], target, entry["page_url"])
            digest = sha256(target)
            if digest in seen:
                print(f"SKIP duplicate {target.name}")
                continue
            items.append(
                {
                    "kind": "suneung_board",
                    "source_url": source_url,
                    "board_url": board_url,
                    "file_seq": entry["file_seq"],
                    "title": entry.get("title"),
                    "year": entry.get("year"),
                    "subject": entry.get("subject"),
                    "local_path": str(target),
                    "sha256": digest,
                    "bytes": target.stat().st_size,
                    "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "rights_note": "Official KICE/suneung.re.kr — internal use only.",
                }
            )
            seen.add(digest)
            added += 1
            print(f"DOWNLOADED {target.name} ({target.stat().st_size} bytes)")

    manifest_path.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 완료: {added}건 추가, 총 {len(items)}건")
    print(f"📄 manifest: {manifest_path}")

    matched = 0
    for item in items:
        if year and str(item.get("year") or "") != year:
            continue
        if subject and subject not in str(item.get("subject") or ""):
            continue
        matched += 1

    if added > 0:
        return 0
    if matched > 0:
        print(f"INFO 이미 수집됨: {matched}건 (중복 SKIP — 정상)")
        for item in items:
            if year and str(item.get("year") or "") != year:
                continue
            if subject and subject not in str(item.get("subject") or ""):
                continue
            lp = item.get("local_path") or ""
            if lp:
                print(f"EXISTS {Path(lp).name}")
        return 0

    if year:
        print(f"WARN {year}학년도 PDF 0건 — 영역 필터·게시판 확인 (과거 연도는 2페이지 이후에 있음)")
    else:
        print("WARN 다운로드 0건 — SUNEUNG_YEAR/SUNEUNG_SUBJECT 필터 또는 게시판 URL 확인")
    return 1


def default_cfg() -> dict:
    return {
        "SOURCE_URLS": [DEFAULT_BOARD],
        "SUNEUNG_BOARD_URL": DEFAULT_BOARD,
        "SUNEUNG_BOARD_IDS": ["1500234"],
        "SUNEUNG_YEAR": "",
        "SUNEUNG_SUBJECT": "",
        "SUNEUNG_EXTENSIONS": [".pdf"],
        "SUNEUNG_MAX_PAGES": 1,
        "OUTPUT_DIR": DEFAULT_OUTPUT,
        "REQUIRE_AUTHORIZED_SOURCE": "true",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="원영 — KICE/수능 기출 PDF 수집")
    parser.add_argument("config", nargs="?", default=str(CONFIG), help="설정 JSON 경로")
    parser.add_argument("--year", help="학년도 필터 (예: 2025)")
    parser.add_argument("--subject", help="영역 필터 (예: 수학)")
    parser.add_argument("--output-dir", help="저장 폴더")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    cfg = default_cfg()
    cfg.update(load_config(cfg_path))
    if args.year:
        cfg["SUNEUNG_YEAR"] = args.year
    if args.subject:
        cfg["SUNEUNG_SUBJECT"] = args.subject
    if args.output_dir:
        cfg["OUTPUT_DIR"] = args.output_dir

    if not cfg_path.exists():
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"WROTE default config: {cfg_path}")

    return run_fetch(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
