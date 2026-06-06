#!/usr/bin/env python3
# video_uploader_v1
import json
import os
import sys
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def load_dotenv() -> dict:
    env = {}
    for base in [Path.cwd(), Path(__file__).resolve().parent]:
        for p in [base, *base.parents]:
            f = p / ".env"
            if f.exists():
                for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                    t = line.strip()
                    if not t or t.startswith("#") or "=" not in t:
                        continue
                    k, v = t.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
                return env
    return env


def truthy(value) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y", "on"}


def as_tags(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if not value:
        return []
    text = str(value).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(v).strip() for v in parsed if str(v).strip()]
    except Exception:
        pass
    return [v.strip() for v in text.split(",") if v.strip()]


def import_google():
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.auth.transport.requests import Request
    except Exception as exc:
        raise RuntimeError("필요 패키지를 설치하세요: python3 -m pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2") from exc
    return Credentials, build, MediaFileUpload, Request


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "video_uploader.json"
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    video_file = Path(cfg.get("VIDEO_FILE") or "").expanduser()
    if not video_file.exists():
        raise SystemExit(f"VIDEO_FILE이 없습니다: {video_file}")
    body = {"snippet": {"title": cfg.get("TITLE") or video_file.stem, "description": cfg.get("DESCRIPTION") or "", "tags": as_tags(cfg.get("TAGS", [])), "categoryId": str(cfg.get("CATEGORY_ID") or "27")}, "status": {"privacyStatus": cfg.get("PRIVACY_STATUS") or "private", "selfDeclaredMadeForKids": truthy(cfg.get("MADE_FOR_KIDS", "false")), "containsSyntheticMedia": truthy(cfg.get("CONTAINS_SYNTHETIC_MEDIA", "true"))}}
    if cfg.get("SCHEDULE_AT"):
        body["status"]["publishAt"] = cfg["SCHEDULE_AT"]
        body["status"]["privacyStatus"] = "private"
    if truthy(cfg.get("DRY_RUN", "true")):
        print(json.dumps({"dry_run": True, "video_file": str(video_file), "request_body": body}, ensure_ascii=False, indent=2))
        return 0

    dot_env = load_dotenv()
    client_id = cfg.get("YOUTUBE_OAUTH_CLIENT_ID") or dot_env.get("YOUTUBE_OAUTH_CLIENT_ID") or os.environ.get("YOUTUBE_OAUTH_CLIENT_ID")
    client_secret = cfg.get("YOUTUBE_OAUTH_CLIENT_SECRET") or dot_env.get("YOUTUBE_OAUTH_CLIENT_SECRET") or os.environ.get("YOUTUBE_OAUTH_CLIENT_SECRET")
    refresh_token = cfg.get("YOUTUBE_OAUTH_REFRESH_TOKEN") or dot_env.get("YOUTUBE_OAUTH_REFRESH_TOKEN") or os.environ.get("YOUTUBE_OAUTH_REFRESH_TOKEN")
    if not (client_id and client_secret and refresh_token):
        raise SystemExit("YOUTUBE_OAUTH_CLIENT_ID/SECRET/REFRESH_TOKEN이 필요합니다.")
    Credentials, build, MediaFileUpload, Request = import_google()
    creds = Credentials(token=None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret, scopes=SCOPES)
    creds.refresh(Request())
    youtube = build("youtube", "v3", credentials=creds)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(str(video_file), mimetype="video/*", chunksize=-1, resumable=True))
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"UPLOAD {int(status.progress() * 100)}%")
    print(json.dumps({"uploaded": True, "video_id": response.get("id")}, ensure_ascii=False, indent=2))
    thumb = cfg.get("THUMBNAIL_FILE")
    if thumb and Path(thumb).expanduser().exists():
        youtube.thumbnails().set(videoId=response["id"], media_body=str(Path(thumb).expanduser())).execute()
        print("THUMBNAIL uploaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
