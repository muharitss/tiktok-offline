from pathlib import Path
from datetime import datetime
import yt_dlp

from database import (
    init_db,
    get_pending_videos,
    update_status,
)


ROOT_DIR = Path(__file__).parent.parent
VIDEOS_DIR = ROOT_DIR / "videos"

VIDEOS_DIR.mkdir(exist_ok=True)


def download_video(video):
    url = video["url"]
    database_id = video["id"]

    print()
    print("=" * 50)
    print(f"Video ID : {database_id}")
    print(f"URL      : {url}")
    print("=" * 50)

    # Tandai sedang didownload
    update_status(
        database_id,
        "downloading"
    )

    options = {
        "outtmpl": str(
            VIDEOS_DIR / "%(id)s.%(ext)s"
        ),

        "format": "best[ext=mp4]/best",

        "noplaylist": True,

        "nooverwrites": True,

        "ignoreerrors": False,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            if not info:
                raise Exception(
                    "Tidak mendapatkan informasi video."
                )

            video_id = info.get("id")

            extension = info.get(
                "ext",
                "mp4"
            )

            filename = f"{video_id}.{extension}"

        update_status(
            database_id,
            "completed",
            filename=filename,
            downloaded_at=datetime.now().isoformat()
        )

        print()
        print("✓ Download berhasil")
        print(f"File: {filename}")

    except Exception as error:

        update_status(
            database_id,
            "failed",
            error=str(error)
        )

        print()
        print("✗ Download gagal")
        print(error)


def main():
    init_db()

    pending_videos = get_pending_videos()

    if not pending_videos:
        print("Tidak ada video pending.")
        return

    print(
        f"Video pending: {len(pending_videos)}"
    )

    for video in pending_videos:
        download_video(video)

    print()
    print("Download queue selesai.")


if __name__ == "__main__":
    main()