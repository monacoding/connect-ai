#!/usr/bin/env python3
# pipeline_runner_v1
import json
import subprocess
import sys
from pathlib import Path


STEPS = [("RUN_INGEST", "source_ingest.py", "source_ingest.json"), ("RUN_CONVERT", "md_convert.py", "md_convert.json"), ("RUN_CURRICULUM", "curriculum_builder.py", "curriculum_builder.json"), ("RUN_VIDEO_PLAN", "video_planner.py", "video_planner.json")]


def truthy(value) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "pipeline_runner.json"
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    here = Path(__file__).resolve().parent
    for flag, script, script_config in STEPS:
        if not truthy(cfg.get(flag, "true")):
            print(f"SKIP {script}")
            continue
        print(f"RUN {script}")
        subprocess.check_call([sys.executable, str(here / script), str(here / script_config)])
    if truthy(cfg.get("AUTO_UPLOAD", "false")):
        raise SystemExit("AUTO_UPLOAD=true는 안전상 자동 실행하지 않습니다. youtube/video_uploader.py를 별도로 실행하세요.")
    print("DONE pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
