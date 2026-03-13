#!/usr/bin/env python3
"""
YouTube Upload — MoneyMath Edition

Uploads a rendered video to YouTube with Education category,
MoneyMath-specific playlist, and optional scheduling.

Usage:
    python youtube_upload.py <video_path> --title "Title" --description "Desc" \
        [--schedule "2026-03-15T12:00:00Z"] [--tags "tag1,tag2"] \
        [--thumbnail path/to/thumb.jpg]
"""

import argparse
import os
import pickle
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = ROOT / "token.pickle"

# MoneyMath channel defaults
PLAYLIST_ID = ""  # Set after first upload, or leave empty to auto-create
PLAYLIST_TITLE = "Money Math"
CATEGORY_ID = "27"  # Education
SCHEDULE_GAP_DAYS = 2

DESCRIPTION_TEMPLATE = """{description}

{tags_block}"""


def get_youtube_service():
    if not TOKEN_FILE.exists():
        print("ERROR: No token.pickle found. Run youtube_auth.py first.")
        sys.exit(1)

    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def get_or_create_playlist(youtube, title=PLAYLIST_TITLE):
    """Find or create the MoneyMath playlist."""
    if PLAYLIST_ID:
        return PLAYLIST_ID

    playlists = youtube.playlists().list(
        part="snippet",
        mine=True,
        maxResults=50,
    ).execute()

    for pl in playlists.get("items", []):
        if title.lower() in pl["snippet"]["title"].lower():
            print(f"Found playlist: {pl['snippet']['title']} ({pl['id']})")
            return pl["id"]

    resp = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "Money Math — breaking down the money side of everyday life.",
            },
            "status": {"privacyStatus": "public"},
        },
    ).execute()

    print(f"Created playlist: {resp['snippet']['title']} ({resp['id']})")
    return resp["id"]


def get_next_schedule_time(youtube):
    """Check channel uploads for recent/scheduled videos and enforce gap."""
    # Get the channel's auto-generated uploads playlist
    try:
        channel_resp = youtube.channels().list(
            part="contentDetails",
            mine=True,
        ).execute()
        uploads_playlist_id = (
            channel_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        )
    except Exception:
        return None

    try:
        playlist_resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
        ).execute()
    except Exception:
        return None

    video_ids = [
        item["contentDetails"]["videoId"]
        for item in playlist_resp.get("items", [])
    ]
    if not video_ids:
        return None

    videos_resp = youtube.videos().list(
        part="status,snippet",
        id=",".join(video_ids),
    ).execute()

    now = datetime.now(timezone.utc)
    gap_ago = now - timedelta(days=SCHEDULE_GAP_DAYS)
    latest = None

    for video in videos_resp.get("items", []):
        status = video.get("status", {})
        snippet = video.get("snippet", {})

        publish_at = status.get("publishAt")
        if publish_at and status.get("privacyStatus") == "private":
            dt = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
            if latest is None or dt > latest:
                latest = dt

        elif status.get("privacyStatus") == "public":
            published_at = snippet.get("publishedAt")
            if published_at:
                dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                if dt > gap_ago and (latest is None or dt > latest):
                    latest = dt

    if latest:
        return latest + timedelta(days=SCHEDULE_GAP_DAYS)
    return None


def resolve_schedule_time(youtube, explicit_time=None):
    """Determine schedule time: explicit, last upload + gap, or publish now."""
    if explicit_time:
        print(f"Using explicit schedule time: {explicit_time}")
        return explicit_time

    print("Checking channel uploads for scheduled/recent videos...")
    next_time = get_next_schedule_time(youtube)

    if next_time:
        iso = next_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"Next slot: {iso}")
        return iso

    print("No scheduled videos found. Publishing immediately.")
    return None


def get_video_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def extract_thumbnail(video_path, timestamp):
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.close()

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-frames:v", "1",
            "-q:v", "2",
            tmp.name,
        ],
        capture_output=True,
    )

    if os.path.getsize(tmp.name) > 0:
        return tmp.name

    os.unlink(tmp.name)
    return None


def upload_video(video_path, title, description, schedule_time=None,
                 tags=None, thumbnail_path=None, skip_thumbnail=False, skip_playlist=False):
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        sys.exit(1)

    youtube = get_youtube_service()

    schedule_time = resolve_schedule_time(youtube, schedule_time)

    # Build description
    tag_hashtags = " ".join(f"#{t.replace(' ', '')}" for t in (tags or []))
    tags_block = tag_hashtags if tag_hashtags else "#MoneyMath #PersonalFinance #MoneyLesson"
    full_description = DESCRIPTION_TEMPLATE.format(
        description=description,
        tags_block=tags_block,
    )

    status_body = {"selfDeclaredMadeForKids": False}
    if schedule_time:
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = schedule_time
    else:
        status_body["privacyStatus"] = "public"

    body = {
        "snippet": {
            "title": title,
            "description": full_description,
            "tags": tags or ["money math", "personal finance", "financial literacy",
                             "money tips", "investing", "budgeting"],
            "categoryId": CATEGORY_ID,
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": status_body,
    }

    media = MediaFileUpload(video_path, chunksize=10 * 1024 * 1024, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print(f"Uploading: {video_path}")
    print(f"Title: {title}")
    if schedule_time:
        print(f"Scheduled for: {schedule_time}")
    else:
        print(f"Publishing: immediately (public)")

    response = None
    retry_count = 0
    max_retries = 10
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"  Uploaded {int(status.progress() * 100)}%")
            retry_count = 0
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError) as e:
            retry_count += 1
            if retry_count > max_retries:
                raise
            wait = min(2 ** retry_count, 60)
            print(f"  Network error ({e}), retry {retry_count}/{max_retries} in {wait}s...")
            import time
            time.sleep(wait)

    video_id = response["id"]
    print(f"\nUpload complete!")
    print(f"Video ID: {video_id}")
    print(f"URL: https://youtube.com/watch?v={video_id}")

    # Playlist disabled

    # Thumbnail
    if not skip_thumbnail:
        if thumbnail_path and os.path.exists(thumbnail_path):
            print(f"\nUsing custom thumbnail: {thumbnail_path}")
            thumb_to_upload = thumbnail_path
            # YouTube API limit is 2MB — compress if needed
            if os.path.getsize(thumbnail_path) > 2 * 1024 * 1024:
                from PIL import Image
                import io
                print(f"  Thumbnail too large ({os.path.getsize(thumbnail_path) // 1024} KB), compressing...")
                img = Image.open(thumbnail_path).convert("RGB")
                compressed = thumbnail_path.rsplit(".", 1)[0] + ".jpg"
                for quality in range(85, 5, -5):
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=quality)
                    if buf.tell() < 2 * 1024 * 1024:
                        with open(compressed, "wb") as f:
                            f.write(buf.getvalue())
                        print(f"  Compressed to {buf.tell() // 1024} KB (quality {quality})")
                        thumb_to_upload = compressed
                        break
            media = MediaFileUpload(thumb_to_upload, mimetype="image/jpeg")
            youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
            print(f"Thumbnail set")
        else:
            duration = get_video_duration(video_path)
            thumbnail_at = duration / 2
            print(f"\nExtracting thumbnail at {thumbnail_at:.1f}s...")
            thumb_path = extract_thumbnail(video_path, thumbnail_at)
            if thumb_path:
                try:
                    media = MediaFileUpload(thumb_path, mimetype="image/jpeg")
                    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
                    print(f"Thumbnail set")
                finally:
                    os.unlink(thumb_path)

    return response


def main():
    parser = argparse.ArgumentParser(description="Upload MoneyMath video to YouTube")
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--description", required=True, help="Video description")
    parser.add_argument("--schedule", default=None, help="Publish time (ISO 8601)")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--thumbnail", default=None, help="Custom thumbnail image path")
    parser.add_argument("--no-thumbnail", action="store_true")
    parser.add_argument("--no-playlist", action="store_true")

    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else None

    upload_video(
        video_path=args.video_path,
        title=args.title,
        description=args.description,
        schedule_time=args.schedule,
        tags=tags,
        thumbnail_path=args.thumbnail,
        skip_thumbnail=args.no_thumbnail,
        skip_playlist=args.no_playlist,
    )


if __name__ == "__main__":
    main()
