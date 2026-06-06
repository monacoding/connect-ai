#!/usr/bin/env python3
# kice_pdf_repair_v1 — 코다리: 원영 kice_pdf_fetch 실패 진단·복구
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "kice_pdf_repair.json"
CRAWLER_TOOLS = HERE.parent.parent / "crawler" / "tools"
FETCH = CRAWLER_TOOLS / "kice_pdf_fetch.py"


def load_cfg() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}


def diagnose(cfg: dict) -> list[str]:
    issues = []
    if not FETCH.exists():
        issues.append("MISSING_TOOL: crawler/tools/kice_pdf_fetch.py 없음 → 도구 재시드 필요")
    out_dir = Path(cfg.get("OUTPUT_DIR") or "")
    if out_dir and not out_dir.exists():
        issues.append(f"MISSING_DIR: {out_dir} 없음 → mkdir 필요")
    if not cfg.get("SUNEUNG_YEAR"):
        issues.append("NO_YEAR: --year 미지정 → 프롬프트에서 학년도 추출 후 재실행")
    return issues


def main() -> int:
    cfg = load_cfg()
    year = str(cfg.get("SUNEUNG_YEAR") or "").strip()
    subject = str(cfg.get("SUNEUNG_SUBJECT") or "").strip()
    prev_out = str(cfg.get("PREVIOUS_OUTPUT") or "")[:2000]

    print("💻 코다리 — kice_pdf_fetch 복구 시작")
    if prev_out:
        print("--- 이전 원영 출력 ---")
        print(prev_out[-800:])
        print("---")

    for line in diagnose(cfg):
        print(f"DIAG {line}")

    if not FETCH.exists():
        print("FAIL kice_pdf_fetch.py 없음. extension Reload 후 ensureCompanyStructure 실행.")
        return 1

    args = [sys.executable, str(FETCH)]
    if year:
        args += ["--year", year]
    if subject:
        args += ["--subject", subject]

    print(f"RETRY {' '.join(args[2:])}")
    r = subprocess.run(args, cwd=str(CRAWLER_TOOLS), capture_output=True, text=True, timeout=180)
    out = (r.stdout or "") + (r.stderr or "")
    print(out)
    ok = r.returncode == 0 or any(
        k in out for k in ("DOWNLOADED", "SKIP duplicate", "INFO 이미 수집됨", "EXISTS ")
    )
    if ok:
        print("REPAIR_OK")
        return 0
    print("REPAIR_FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
