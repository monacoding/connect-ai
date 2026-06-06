# video_uploader

YouTube Data API v3 `videos.insert`로 영상을 업로드합니다. 기본값은 안전을 위해 `DRY_RUN=true`, `PRIVACY_STATUS=private`입니다.

필요:
- Google Cloud OAuth Client ID/Secret
- YouTube 업로드 권한이 있는 refresh token
- Python 패키지: `google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2`

```bash
python3 -m pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
python3 video_uploader.py video_uploader.json
```
