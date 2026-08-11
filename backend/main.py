from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import mimetypes
from urllib.parse import unquote


ROOT_DIR = Path(__file__).parent.parent
VIDEOS_DIR = ROOT_DIR / "videos"

VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
    ".mkv",
}

CHUNK_SIZE = 1024 * 1024  # 1 MB


class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/api/health":
            self.send_json({
                "status": "ok"
            })
            return

        if self.path == "/api/videos":
            videos = []

            for file in sorted(VIDEOS_DIR.iterdir()):
                if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
                    videos.append({
                        "name": file.name,
                        "url": f"/videos/{file.name}"
                    })

            self.send_json({
                "count": len(videos),
                "videos": videos
            })

            return

        if self.path.startswith("/videos/"):
            self.serve_video()
            return

        self.send_json({
            "error": "Not found"
        }, 404)

    def serve_video(self):
        filename = unquote(self.path[len("/videos/"):])

        file_path = (VIDEOS_DIR / filename).resolve()

        try:
            file_path.relative_to(VIDEOS_DIR.resolve())
        except ValueError:
            self.send_json({
                "error": "Invalid path"
            }, 400)
            return

        if not file_path.exists() or not file_path.is_file():
            self.send_json({
                "error": "Video not found"
            }, 404)
            return

        if file_path.suffix.lower() not in VIDEO_EXTENSIONS:
            self.send_json({
                "error": "Unsupported video format"
            }, 400)
            return

        file_size = file_path.stat().st_size

        content_type = mimetypes.guess_type(file_path.name)[0]

        if not content_type:
            content_type = "application/octet-stream"

        range_header = self.headers.get("Range")

        if not range_header:
            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(file_size)
            )

            self.send_header(
                "Accept-Ranges",
                "bytes"
            )

            self.end_headers()

            self.stream_file(
                file_path,
                start=0,
                length=file_size
            )

            return

        if not range_header.startswith("bytes="):
            self.send_response(416)

            self.send_header(
                "Content-Range",
                f"bytes */{file_size}"
            )

            self.end_headers()

            return

        range_value = range_header.replace(
            "bytes=",
            "",
            1
        ).split(",")[0].strip()

        try:
            start_str, end_str = range_value.split("-")

            if start_str:
                start = int(start_str)
            else:
                requested_size = int(end_str)

                if requested_size <= 0:
                    raise ValueError

                requested_size = min(
                    requested_size,
                    file_size
                )

                start = file_size - requested_size

            if end_str:
                end = int(end_str)
            else:
                end = file_size - 1

        except ValueError:
            self.send_response(416)

            self.send_header(
                "Content-Range",
                f"bytes */{file_size}"
            )

            self.end_headers()

            return

        if start < 0 or start >= file_size:
            self.send_response(416)

            self.send_header(
                "Content-Range",
                f"bytes */{file_size}"
            )

            self.end_headers()

            return

        end = min(end, file_size - 1)

        if start > end:
            self.send_response(416)

            self.send_header(
                "Content-Range",
                f"bytes */{file_size}"
            )

            self.end_headers()

            return

        content_length = end - start + 1

        self.send_response(206)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Range",
            f"bytes {start}-{end}/{file_size}"
        )

        self.send_header(
            "Content-Length",
            str(content_length)
        )

        self.send_header(
            "Accept-Ranges",
            "bytes"
        )

        self.end_headers()

        self.stream_file(
            file_path,
            start=start,
            length=content_length
        )

    def stream_file(self, file_path, start, length):
        with file_path.open("rb") as file:
            file.seek(start)

            remaining = length

            while remaining > 0:
                chunk_size = min(
                    CHUNK_SIZE,
                    remaining
                )

                chunk = file.read(chunk_size)

                if not chunk:
                    break

                self.wfile.write(chunk)

                remaining -= len(chunk)


server = HTTPServer(
    ("localhost", 8000),
    Handler
)

print("Backend running at http://localhost:8000")

server.serve_forever()