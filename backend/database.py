from pathlib import Path
import sqlite3


ROOT_DIR = Path(__file__).parent.parent
DB_FILE = ROOT_DIR / "backend" / "videos.db"


def get_connection():
    connection = sqlite3.connect(DB_FILE)

    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            video_id TEXT,
            filename TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            error TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            downloaded_at DATETIME
        )
    """)

    connection.commit()
    connection.close()


def add_video(url):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO videos (url)
            VALUES (?)
            """,
            (url,)
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        connection.close()


def get_pending_videos():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM videos
        WHERE status = 'pending'
        ORDER BY id ASC
        """
    ).fetchall()

    connection.close()

    return rows


def update_status(
    video_id,
    status,
    error=None,
    filename=None,
    downloaded_at=None
):
    connection = get_connection()

    connection.execute(
        """
        UPDATE videos
        SET
            status = ?,
            error = ?,
            filename = COALESCE(?, filename),
            downloaded_at = COALESCE(?, downloaded_at)
        WHERE id = ?
        """,
        (
            status,
            error,
            filename,
            downloaded_at,
            video_id
        )
    )

    connection.commit()
    connection.close()


def get_stats():
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT status, COUNT(*) AS count
        FROM videos
        GROUP BY status
        """
    ).fetchall()

    connection.close()

    return {
        row["status"]: row["count"]
        for row in rows
    }


if __name__ == "__main__":
    init_db()

    print("Database siap.")