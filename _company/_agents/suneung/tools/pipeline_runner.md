# pipeline_runner

수능 자료 파이프라인을 순서대로 실행합니다.

순서:
1. `source_ingest.py`
2. `md_convert.py`
3. `curriculum_builder.py`
4. `video_planner.py`

`AUTO_UPLOAD`는 기본 `false`입니다. 실제 업로드는 YouTube OAuth와 별도 승인 후 `youtube/video_uploader.py`를 사용하세요.

```bash
python3 pipeline_runner.py pipeline_runner.json
```
