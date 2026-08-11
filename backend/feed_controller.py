from pathlib import Path

ROOT_DIR = Path(__file__).parent
URLS_FILE = ROOT_DIR / "urls.txt"

MAX_VIDEOS = 480


def load_urls():
    if not URLS_FILE.exists():
        return []

    urls = []

    for line in URLS_FILE.read_text().splitlines():
        url = line.strip()

        if not url:
            continue

        if url.startswith("#"):
            continue

        if url not in urls:
            urls.append(url)

    return urls


def add_url(url):
    url = url.strip()

    if not url:
        return False

    urls = load_urls()

    if url in urls:
        return False

    if len(urls) >= MAX_VIDEOS:
        return False

    with URLS_FILE.open("a") as file:
        file.write(url + "\n")

    return True


def get_count():
    return len(load_urls())


if __name__ == "__main__":
    print(f"URL tersimpan: {get_count()}/{MAX_VIDEOS}")

    while get_count() < MAX_VIDEOS:
        url = input("Masukkan URL video (Enter untuk selesai): ").strip()

        if not url:
            break

        if add_url(url):
            print(f"Ditambahkan. Total: {get_count()}/{MAX_VIDEOS}")
        else:
            print("URL sudah ada atau queue sudah penuh.")

    print(f"Selesai. Total URL: {get_count()}")