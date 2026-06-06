#!/usr/bin/env python3
# pipeline_runner_v1
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    ("RUN_DB", "korean_db_build.py", "korean_db_build.json"),
    ("RUN_RESOURCES", "korean_resource_collect.py", "korean_resource_collect.json"),
    ("RUN_ANALYZE", "korean_analyze.py", "korean_analyze.json"),
    ("RUN_GUIDE", "korean_study_guide.py", "korean_study_guide.json"),
]


def truthy(v) -> bool:
    return str(v).lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    cfg_path = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "pipeline_runner.json")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    for flag, script, conf in STEPS:
        if not truthy(cfg.get(flag, "true")):
            print(f"SKIP {script}")
            continue
        print(f"RUN {script}")
        subprocess.check_call([sys.executable, str(HERE / script), str(HERE / conf)])
    print("DONE korean pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
