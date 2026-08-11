from database import (
    init_db,
    add_video,
    get_pending_videos,
    get_stats,
)


MAX_VIDEOS = 480


def add_url(url):
    stats = get_stats()

    total = sum(stats.values())

    if total >= MAX_VIDEOS:
        print("Queue sudah penuh.")
        return False

    video_id = add_video(url)

    if video_id is None:
        print("URL sudah ada.")
        return False

    print(f"URL ditambahkan. ID: {video_id}")

    return True


def show_queue():
    stats = get_stats()

    print()
    print("Queue:")
    print(f"Pending:     {stats.get('pending', 0)}")
    print(f"Downloading: {stats.get('downloading', 0)}")
    print(f"Completed:   {stats.get('completed', 0)}")
    print(f"Failed:      {stats.get('failed', 0)}")
    print(f"Total:       {sum(stats.values())}")
    print()


def main():
    init_db()

    print("TikTok Offline Queue")
    print("--------------------")

    while True:
        url = input("URL (Enter untuk selesai): ").strip()

        if not url:
            break

        add_url(url)

    show_queue()


if __name__ == "__main__":
    main()