# video_uploader

YouTube Data API v3 `videos.insert`로 **영상을 자동 업로드**합니다. 미니(YouTube 에이전트)의 공식 업로드 도구입니다.

기본값은 안전을 위해 `DRY_RUN=true`, `PRIVACY_STATUS=private`입니다.  
권장 순서: **기획·스코어링 → DRY_RUN 검증 → 사장님 승인 → 실제 업로드 → 48h 후 my_videos_check로 학습 기록**

필요:
- Google Cloud OAuth Client ID/Secret
- YouTube 업로드 권한이 있는 refresh token
- Python 패키지: `google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2`

```bash
python3 -m pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
python3 video_uploader.py video_uploader.json
```
