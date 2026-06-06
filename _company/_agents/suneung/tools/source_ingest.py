#!/usr/bin/env python3
# source_ingest_v1
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name or "downloaded_source"
    return name if "." in name else name + ".pdf"


def download(url: str, dest: Path) -> None:
    req = Request(url, headers={"User-Agent": "connect-ai-suneung-ingest/1.0"})
    with urlopen(req, timeout=60) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "source_ingest.json"
    cfg = load_config(config_path)
    if str(cfg.get("REQUIRE_AUTHORIZED_SOURCE", "true")).lower() == "true":
        print("AUTHORIZED_SOURCE_CHECK: 공식/허가된 출처인지 확인한 입력만 처리합니다.")

    out_dir = Path(cfg.get("OUTPUT_DIR") or "_company/suneung/sources")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    existing = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8")).get("items", [])
    items = list(existing)
    seen = {item.get("sha256") for item in items if item.get("sha256")}

    for url in as_list(cfg.get("SOURCE_URLS", [])):
        target = out_dir / filename_from_url(url)
        download(url, target)
        digest = sha256(target)
        if digest not in seen:
            items.append({"kind": "url", "source_url": url, "local_path": str(target), "sha256": digest, "bytes": target.stat().st_size, "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rights_note": "Use only official/authorized materials; do not republish copyrighted exam text without permission."})
            seen.add(digest)

    for raw in as_list(cfg.get("LOCAL_FILES", [])):
        src = Path(raw).expanduser()
        if not src.exists():
            print(f"SKIP missing local file: {src}")
            continue
        target = out_dir / src.name
        if src.resolve() != target.resolve():
            shutil.copy2(src, target)
        digest = sha256(target)
        if digest not in seen:
            items.append({"kind": "local", "source_url": "", "local_path": str(target), "sha256": digest, "bytes": target.stat().st_size, "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rights_note": "Local file supplied by user; user is responsible for usage rights."})
            seen.add(digest)

    manifest_path.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {manifest_path} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
