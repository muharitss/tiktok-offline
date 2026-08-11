Bisa. Saya sarankan kita **jangan membuat satu prompt raksasa**. Untuk project seperti ini, AI coding agent akan jauh lebih stabil kalau setiap prompt punya satu tujuan yang jelas, ada acceptance criteria, dan **tidak mengubah bagian yang belum waktunya disentuh**.

Dari kondisi project kamu sekarang sampai versi MVP yang cukup matang, saya perkirakan **sekitar 18 prompt**.

Urutannya:

```text
01. Audit & stabilisasi kondisi sekarang
02. Downloader recovery
03. Retry downloader
04. Progress downloader
05. Validasi hasil download
06. Queue API
07. Backend video streaming improvement
08. Viewer loading & error state
09. Viewer navigation
10. Autoplay / active video refinement
11. Preload video
12. UI viewer cleanup
13. Automatic feed collector — fondasi
14. Feed collector — browser automation
15. Feed collector — queue integration
16. Pipeline end-to-end 480 videos
17. Offline/PWA/local experience
18. Final testing & cleanup
```

**Catatan penting:** bagian automatic TikTok feed collector adalah bagian yang paling tidak stabil karena struktur TikTok dapat berubah dan dapat menggunakan login challenge, CAPTCHA, rate limit, atau anti-automation. Prompt kita akan secara eksplisit melarang agent mencoba melewati security controls tersebut.

Di bawah ini saya buat prompt-nya **satu per satu dan berurutan**. Kamu tinggal copy Prompt 1 ke Antigravity, selesaikan, lalu Prompt 2, dan seterusnya.

---

# PROMPT 01 — Audit & Stabilisasi

Tujuan prompt pertama hanya memastikan AI memahami project dan tidak merusak fondasi yang sudah ada.

```text
Saya sedang mengembangkan project lokal bernama `tiktok-offline`.

Jangan melakukan rewrite besar-besaran.
Jangan mengulang initial setup.
Jangan mengganti tech stack.

TECH STACK:
- Python backend
- yt-dlp
- React + Vite
- Tailwind CSS
- SQLite
- 1 repository

STRUKTUR SAAT INI:

tiktok-offline/
├── backend/
│   ├── main.py
│   ├── downloader.py
│   ├── database.py
│   ├── queue_manager.py
│   ├── feed_collector.py
│   ├── urls.txt
│   └── downloaded.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── VideoItem.jsx
│   └── ...
├── videos/
├── .venv/
├── .gitignore
└── README.md

KONDISI YANG SUDAH ADA:

1. Python HTTP server berjalan di localhost:8000.
2. Endpoint:
   GET /api/health
   GET /api/videos
   GET /videos/<filename>
3. Video server sudah mendukung HTTP Range Request.
4. React viewer sudah:
   - vertical scroll
   - CSS snap
   - autoplay ketika terlihat
   - pause ketika keluar viewport
   - loop
   - click play/pause
   - fullscreen
   - keyboard ArrowUp / ArrowDown
5. yt-dlp sudah digunakan untuk download.
6. SQLite sudah dibuat di:
   backend/videos.db
7. Tabel SQLite bernama `videos`.
8. `queue_manager.py` sudah bisa memasukkan URL ke SQLite.
9. `downloader.py` sudah membaca status `pending` dari SQLite.
10. Status dasar:
    pending
    downloading
    completed
    failed

TUJUAN PROJECT:

Aplikasi lokal seperti TikTok Offline Videos.

Saat online:
TikTok feed
↓
collect video URLs
↓
queue maksimal 480
↓
download dengan yt-dlp
↓
videos lokal

Saat offline:
Python backend
↓
React viewer
↓
vertical video feed

UNTUK TASK INI:

1. Audit seluruh repository.
2. Jangan langsung membuat fitur baru.
3. Periksa apakah import, path, SQLite, downloader, frontend, dan backend konsisten.
4. Jalankan test sederhana jika memungkinkan.
5. Identifikasi error nyata.
6. Perbaiki hanya error yang memang diperlukan agar kondisi project saat ini stabil.
7. Jangan menghapus fitur yang sudah bekerja.
8. Jangan membuat automatic TikTok collector dulu.
9. Jangan menambahkan concurrency dulu.
10. Jangan menambahkan dependency baru kecuali benar-benar diperlukan.

Setelah selesai:
- tampilkan file yang diubah
- jelaskan perubahan
- tampilkan command untuk menjalankan backend
- tampilkan command untuk menjalankan frontend
- tampilkan command untuk menjalankan downloader
- tampilkan hasil test

Acceptance criteria:

- backend dapat start
- /api/health bekerja
- /api/videos bekerja
- video lokal dapat diakses
- Range Request tetap bekerja
- SQLite dapat dibuka
- queue dapat menambahkan URL
- downloader dapat membaca pending queue
- React dapat menampilkan video lokal

Berhenti setelah task ini selesai.
Jangan lanjut ke fitur berikutnya.
```

---

# PROMPT 02 — Downloader Recovery

Setelah Prompt 1 selesai dan project stabil:

```text
Sekarang fokus hanya pada DOWNLOAD RECOVERY.

Jangan mengubah frontend.
Jangan membuat automatic TikTok collector.
Jangan menambahkan concurrency.
Jangan mengubah arsitektur besar.

Masalah saat ini:

Jika downloader sedang berjalan lalu proses mati/crash/terminal ditutup, sebuah video dapat tertinggal dengan status:

downloading

Ketika downloader dijalankan lagi, video tersebut tidak diproses karena downloader hanya mengambil:

pending

TASK:

Implementasikan recovery mechanism.

Aturan:

1. Saat downloader dimulai, cari semua record:
   status = "downloading"

2. Ubah status tersebut kembali menjadi:
   pending

3. Hapus error lama jika ada.

4. Setelah recovery, downloader memproses queue pending seperti biasa.

5. Jangan mengubah record:
   completed
   failed
   pending

6. Recovery harus aman dijalankan berkali-kali.

Contoh:

Sebelum restart:

id 1 = completed
id 2 = downloading
id 3 = pending
id 4 = failed

Setelah startup:

id 1 = completed
id 2 = pending
id 3 = pending
id 4 = failed

TASK IMPLEMENTATION:

- update database.py jika diperlukan
- update downloader.py
- tambahkan fungsi recovery yang jelas
- jangan membuat kode duplikat

TEST:

Buat test sederhana yang membuktikan:
downloading → pending

Kemudian jalankan downloader dan pastikan pending diproses.

Setelah selesai:
- tampilkan file yang diubah
- jelaskan perubahan
- tampilkan hasil test

Berhenti setelah task selesai.
```

---

# PROMPT 03 — Retry

```text
Sekarang fokus hanya pada RETRY DOWNLOAD.

Jangan mengubah frontend.
Jangan membuat feed collector.
Jangan menambahkan concurrency.

Saat ini status failed sudah tersedia, tetapi downloader belum memiliki retry mechanism yang baik.

TASK:

Tambahkan retry untuk download yang gagal.

Requirement:

1. Default retry maksimal:
   3 kali.

2. Retry hanya untuk kegagalan download yang terjadi saat proses yt-dlp.

3. Jangan retry URL yang sudah:
   completed

4. Setelah semua retry gagal:
   status = failed

5. Simpan pesan error terakhir di kolom:
   error

6. Jangan membuat record database baru saat retry.

7. Gunakan backoff sederhana:
   percobaan berikutnya menunggu beberapa detik.

8. Jangan membuat infinite loop.

9. Jika download berhasil pada percobaan kedua atau ketiga:
   status = completed

10. Jika gagal semuanya:
   status = failed

Tambahkan konfigurasi sederhana seperti:

MAX_RETRIES = 3

Jika perlu, gunakan fungsi terpisah:

download_with_retry(...)

TEST:

Simulasikan kegagalan jika memungkinkan tanpa bergantung pada TikTok.

Buktikan:
attempt 1
attempt 2
attempt 3
failed

Dan kasus:
attempt 1 gagal
attempt 2 berhasil
completed

Setelah selesai tampilkan:
- file yang berubah
- penjelasan
- hasil test

Berhenti.
```

---

# PROMPT 04 — Progress Downloader

```text
Sekarang fokus hanya pada DOWNLOAD PROGRESS.

Jangan mengubah frontend.
Jangan membuat collector.
Jangan menambahkan concurrency.

Gunakan kemampuan progress hook dari yt-dlp.

TASK:

Tambahkan progress reporting yang sederhana.

Saya ingin terminal menampilkan informasi seperti:

Downloading:
45.2% | 4.2 MiB / 9.2 MiB | 2.1 MiB/s | ETA 00:03

Requirement:

1. Gunakan yt-dlp progress_hooks.
2. Jangan membuat output terminal menjadi ratusan baris.
3. Update progress pada satu baris jika memungkinkan.
4. Tangani:
   downloading
   finished
   error
5. Progress tidak boleh menyebabkan crash.
6. Jangan menyimpan progress ke SQLite dulu.
7. Jangan membuat UI progress dulu.

Jika ukuran file tidak diketahui, tampilkan informasi yang tersedia.

TEST:
- jalankan download satu video
- tunjukkan progress di terminal
- pastikan completed tetap tersimpan setelah selesai

Berhenti setelah task selesai.
```

---

# PROMPT 05 — Validasi File Download

```text
Sekarang fokus hanya pada VALIDASI HASIL DOWNLOAD.

Jangan mengubah frontend.
Jangan membuat automatic collector.
Jangan menambahkan concurrency.

Masalah:
yt-dlp bisa saja menghasilkan file yang tidak valid, incomplete, atau format yang tidak sesuai ekspektasi.

TASK:

Setelah download selesai:

1. Pastikan file benar-benar ada.
2. Pastikan ukuran file > 0.
3. Ambil filename aktual dari yt-dlp.
4. Simpan filename ke SQLite.
5. Jika file tidak ditemukan:
   status = failed
6. Simpan error yang jelas.
7. Jangan menandai completed jika file tidak valid secara dasar.

Jangan melakukan video transcoding.

Jangan menggunakan ffmpeg untuk memproses ulang video kecuali memang diperlukan oleh yt-dlp.

TEST:
- valid file → completed
- file tidak ada → failed

Berhenti.
```

---

# PROMPT 06 — Queue API

Sekarang kita mulai menghubungkan backend dengan queue.

```text
Sekarang fokus pada QUEUE API.

Jangan membuat automatic TikTok collector dulu.

Backend Python saat ini memiliki:

GET /api/health
GET /api/videos

Tambahkan endpoint queue sederhana.

Requirement:

GET /api/queue

Response:

{
  "total": 10,
  "pending": 5,
  "downloading": 1,
  "completed": 3,
  "failed": 1
}

Tambahkan juga:

GET /api/queue/videos

Response berupa daftar record queue dengan informasi minimal:

id
url
video_id
filename
status
error

Jangan expose data sensitif.

Jangan membuat authentication.

Jangan membuat frontend untuk endpoint ini dulu.

Pastikan endpoint read-only.

Test menggunakan curl.

Contoh:

curl http://localhost:8000/api/queue

curl http://localhost:8000/api/queue/videos

Setelah selesai:
- file yang berubah
- contoh response
- command test

Berhenti.
```

---

# PROMPT 07 — Backend Streaming Hardening

HTTP Range sudah kita buat. Sekarang rapikan.

```text
Sekarang fokus pada VIDEO STREAMING BACKEND.

Range Request sudah bekerja dan tidak boleh dirusak.

Target:

GET /videos/<filename>

harus mendukung:

- normal GET
- Range request
- 206 Partial Content
- Content-Range
- Content-Length
- Accept-Ranges
- MIME type
- invalid range → 416

TASK:

Audit implementasi streaming sekarang.

Perbaiki jika diperlukan:

1. Path traversal protection.
2. MIME type berdasarkan extension.
3. Range parsing.
4. Suffix range:
   bytes=-500000
5. Open-ended range:
   bytes=500000-
6. Invalid range → 416.
7. Jangan menggunakan read_bytes() untuk file video.
8. Streaming dilakukan chunk-by-chunk.

Jangan mengubah React.

TEST dengan curl:

Range pertama:
bytes=0-1048575

Range tengah.

Range terakhir.

Invalid range.

Pastikan response sesuai.

Berhenti.
```

---

# PROMPT 08 — React Loading/Error

```text
Sekarang fokus hanya pada FRONTEND VIEWER STATE.

Jangan mengubah downloader.
Jangan membuat collector.
Jangan mengubah database.

React viewer saat ini sudah bisa menampilkan video.

Tambahkan:

1. Loading state.
2. Error state.
3. Empty state.
4. Video loading indicator sederhana.
5. Jika video gagal dimainkan, tampilkan pesan kecil pada video tersebut.
6. Jangan membuat UI terlalu kompleks.

Pertahankan:
- black background
- vertical feed
- snap
- autoplay
- pause
- fullscreen

Jangan menambahkan fitur sosial.

Acceptance criteria:
- API loading terlihat
- API error terlihat
- queue kosong menghasilkan empty state
- video error tidak membuat seluruh aplikasi crash

Berhenti.
```

---

# PROMPT 09 — Viewer Navigation

```text
Sekarang fokus pada NAVIGASI VIEWER.

Tambahkan navigasi yang lebih konsisten.

Requirement:

1. ArrowDown → video berikutnya.
2. ArrowUp → video sebelumnya.
3. Mouse wheel → natural scrolling.
4. Tombol Next.
5. Tombol Previous.
6. Jangan membuat scroll loop dari video terakhir ke pertama.
7. Previous pada video pertama tidak melakukan apa-apa.
8. Next pada video terakhir tidak melakukan apa-apa.
9. Navigasi harus menggunakan scrollIntoView atau mekanisme yang stabil.
10. Jangan menggunakan window.scrollBy berdasarkan innerHeight jika pendekatan itu menyebabkan posisi meleset.

Pertahankan CSS snap.

Jangan menyentuh backend.

Test:
- 3 video
- next
- previous
- keyboard
- mouse wheel

Berhenti.
```

---

# PROMPT 10 — Active Video

```text
Sekarang fokus pada ACTIVE VIDEO MANAGEMENT.

Tujuan:
hanya video yang sedang terlihat yang autoplay.

Requirement:

1. Gunakan IntersectionObserver.
2. Threshold sekitar 0.6–0.8.
3. Video aktif → play.
4. Video tidak aktif → pause.
5. Hanya satu video boleh autoplay pada satu waktu.
6. Jangan mencoba autoplay dengan suara.
7. Tetap muted.
8. playsInline.
9. Jika play() ditolak browser, jangan crash.
10. Jangan mengganggu manual pause secara permanen.

Jika user pause video aktif, jangan langsung autoplay terus-menerus hanya karena state berubah.

Buat state management sesederhana mungkin.

Test dengan 3–5 video.

Berhenti.
```

---

# PROMPT 11 — Preload Video Terdekat

```text
Sekarang fokus hanya pada PRELOADING.

Jangan membuat virtualized list dulu.

Masalah:
Jika ada banyak video, kita tidak ingin browser aktif memulai download semua video sekaligus.

Implementasikan strategi sederhana:

- active video → preload/loads normally
- video berikutnya → boleh preload
- video sebelumnya → boleh preload
- video jauh → jangan dipaksa preload

Jika menggunakan HTML video preload, gunakan strategi yang sesuai.

Jangan melakukan fetch manual seluruh file.

Jangan membuat cache system sendiri.

Tujuan:
video berikutnya terasa lebih cepat saat scrolling.

Pastikan:
- tidak download semua 480 video sekaligus
- tidak menyebabkan memory leak
- observer dibersihkan

Test dengan browser Network tab.

Berhenti.
```

---

# PROMPT 12 — Viewer UI Cleanup

```text
Sekarang fokus pada UI viewer.

Buat UI sederhana seperti offline short-video viewer.

Pertahankan:
- black background
- fullscreen video
- vertical snap

Tambahkan/rapikan:
- posisi video counter
- Play/Pause
- Fullscreen
- Next
- Previous
- loading indicator
- error indicator

Requirement:
- responsive desktop
- mouse friendly
- keyboard friendly
- tombol tidak menghalangi video terlalu banyak
- tidak perlu clone TikTok
- tidak perlu Like
- tidak perlu Comment
- tidak perlu Share
- tidak perlu Follow

Jangan mengubah backend.

Berhenti setelah UI selesai.
```

---

# PROMPT 13 — Feed Collector Foundation

Ini mulai bagian yang sensitif.

```text
Sekarang mulai membuat FONDASI AUTOMATIC FEED COLLECTOR.

PENTING:

Collector hanya boleh mengumpulkan URL video yang tersedia secara normal dari halaman/feed yang dapat diakses oleh user.

Jangan:
- bypass CAPTCHA
- bypass login challenge
- bypass security control
- bypass rate limit
- mencuri cookie/session
- mengambil credential
- melakukan stealth evasion
- melakukan exploit
- menggunakan teknik untuk menghindari anti-bot system

Jika TikTok memerlukan login/challenge/CAPTCHA, collector harus berhenti dan melaporkan kondisi tersebut.

TASK:

Buat arsitektur collector yang terpisah dari downloader.

File:

backend/feed_collector.py

Responsibility:

Feed Collector:
- menemukan URL
- deduplicate
- memasukkan URL ke SQLite

Downloader:
- membaca SQLite
- download video

Collector TIDAK boleh menjalankan yt-dlp secara langsung.

Buat interface/fungsi:

collect_urls(...)
add_collected_url(...)

Target maksimal:
480 video.

Tambahkan logging sederhana.

Jangan implementasikan browser automation dulu.

Untuk tahap ini:
- buat struktur class/function
- integrasikan dengan database
- test dengan daftar URL dummy

Berhenti.
```

---

# PROMPT 14 — Browser Feed Collector

Ini prompt yang paling mungkin membutuhkan penyesuaian berdasarkan hasil agent.

```text
Sekarang fokus pada IMPLEMENTASI BROWSER FEED COLLECTOR.

Gunakan browser automation hanya untuk membuka feed yang dapat diakses secara normal oleh user.

Jangan bypass:
- CAPTCHA
- login challenge
- anti-bot
- rate limits
- security controls

Jika muncul challenge atau CAPTCHA:
- hentikan collector
- tampilkan pesan
- jangan mencoba melewatinya

Tujuan:

Browser
↓
Feed
↓
scroll normal
↓
observasi video/post yang tersedia
↓
ambil URL yang memang tersedia pada halaman
↓
deduplicate
↓
SQLite
↓
maksimal 480

Requirement:

1. Collector berjalan sebagai proses terpisah.
2. Jangan mencampur collector dengan downloader.
3. Collector berhenti jika queue mencapai 480.
4. URL duplikat diabaikan.
5. Scroll dilakukan dengan interval yang wajar.
6. Tambahkan delay sederhana agar tidak melakukan request berlebihan.
7. Log:
   discovered
   duplicate
   added
   queue full
   stopped
8. Jika URL tidak dapat ditemukan secara normal, jangan mencoba bypass mekanisme keamanan.

Gunakan library browser automation yang sesuai jika belum ada.

Sebelum menambahkan dependency:
- jelaskan dependency yang dibutuhkan
- tambahkan hanya yang diperlukan

Test terlebih dahulu pada jumlah kecil:
MAX_COLLECT = 5

Jangan langsung test 480.

Berhenti setelah collector 5 URL bekerja.
```

---

# PROMPT 15 — Collector → Queue Integration

```text
Sekarang integrasikan feed collector dengan SQLite queue.

Flow final:

Feed Collector
      ↓
discover URL
      ↓
add_video()
      ↓
SQLite
      ↓
pending
      ↓
Downloader

Requirement:

1. Collector tidak melakukan download.
2. Downloader tidak melakukan scraping.
3. SQLite menjadi source of truth.
4. URL UNIQUE.
5. Maksimum total queue 480.
6. Jika URL sudah ada → skip.
7. Jika queue penuh → collector berhenti.
8. Collector dapat dijalankan kembali.
9. Collector tidak menghapus completed.
10. Collector tidak membuat duplicate record.

Tambahkan konfigurasi:

MAX_VIDEOS = 480

Test:
- collector menemukan 5 URL
- queue menjadi 5
- jalankan collector lagi
- tidak ada duplicate
- downloader dapat memproses pending

Berhenti.
```

---

# PROMPT 16 — End-to-End Pipeline 480

Sekarang kita test seluruh sistem.

```text
Sekarang fokus pada END-TO-END PIPELINE.

Jangan menambahkan fitur baru.

Pipeline yang harus bekerja:

Feed
 ↓
Feed Collector
 ↓
SQLite
 ↓
pending
 ↓
Downloader
 ↓
yt-dlp
 ↓
videos/
 ↓
completed
 ↓
Python API
 ↓
React
 ↓
Offline Viewer

TASK:

Buat test/integration workflow untuk skenario:

1. Collector menemukan URL.
2. URL masuk SQLite.
3. Duplicate diabaikan.
4. Queue memiliki status pending.
5. Downloader mengambil pending.
6. Status menjadi downloading.
7. yt-dlp download.
8. File divalidasi.
9. Status menjadi completed.
10. Filename tersimpan.
11. API melihat video lokal.
12. React dapat menampilkan video.

Jangan benar-benar mendownload 480 video dalam test otomatis.

Gunakan test kecil 3–5 video.

Tambahkan pengecekan bahwa total queue tidak dapat melewati 480.

Berhenti setelah pipeline stabil.
```

---

# PROMPT 17 — Offline Mode / Local Experience

```text
Sekarang fokus pada OFFLINE EXPERIENCE.

Tujuan:
Setelah video selesai didownload, user dapat mematikan internet dan tetap menggunakan viewer.

Requirement:

1. React hanya bergantung pada:
   localhost backend
2. Video berasal dari local videos/.
3. Jangan ada request external untuk playback.
4. API videos berasal dari local backend.
5. Viewer tetap bekerja ketika internet mati.
6. Jika internet mati tetapi localhost hidup → viewer tetap bekerja.
7. Jika backend mati → tampilkan pesan backend offline.
8. Jangan menambahkan cloud.
9. Jangan menambahkan authentication.

Tambahkan dokumentasi README:

ONLINE:
- jalankan collector
- jalankan downloader

OFFLINE:
- matikan internet
- jalankan backend
- jalankan frontend
- buka viewer

Jelaskan dependency mana yang hanya diperlukan saat downloading.

Berhenti.
```

---

# PROMPT 18 — Final Audit & Cleanup

Ini prompt terakhir.

```text
Sekarang lakukan FINAL AUDIT project `tiktok-offline`.

Jangan menambahkan fitur baru.

Periksa seluruh project:

Backend:
- main.py
- database.py
- queue_manager.py
- downloader.py
- feed_collector.py

Frontend:
- App.jsx
- VideoItem.jsx
- package.json
- konfigurasi Vite/Tailwind

Database:
- schema
- status
- uniqueness
- recovery

Downloader:
- retry
- progress
- recovery
- validation
- completed
- failed

Collector:
- max 480
- duplicate protection
- queue integration
- tidak melakukan bypass security controls

Viewer:
- vertical scroll
- snap
- autoplay
- pause
- fullscreen
- keyboard
- mouse wheel
- next/previous
- preload terdekat
- loading
- error state

Backend streaming:
- Range Request
- 206
- 416
- Content-Range
- Content-Length
- Accept-Ranges
- path traversal protection
- streaming chunk

OFFLINE:
- video playback lokal
- tidak bergantung pada internet

TASK:

1. Cari bug nyata.
2. Perbaiki bug nyata.
3. Jangan melakukan rewrite besar.
4. Jangan menambahkan dependency tanpa alasan.
5. Jangan menghapus fitur yang bekerja.
6. Bersihkan kode duplikat.
7. Tambahkan error handling yang diperlukan.
8. Pastikan project dapat dijalankan dari README.
9. Update README dengan command yang benar.

Buat checklist final:

[ ] Backend
[ ] SQLite
[ ] Downloader
[ ] Retry
[ ] Recovery
[ ] Progress
[ ] Validation
[ ] Collector
[ ] Queue 480
[ ] Video streaming
[ ] React viewer
[ ] Autoplay
[ ] Navigation
[ ] Fullscreen
[ ] Preload
[ ] Offline mode

Kemudian jalankan test yang realistis.

Jangan mengklaim sesuatu bekerja jika belum diuji.

Tampilkan:
- file yang berubah
- test yang dijalankan
- hasil test
- masalah yang masih tersisa

Berhenti setelah final audit.
```

---

## Urutan besarnya

Supaya kamu tidak kehilangan arah saat menjalankan prompt satu per satu:

```text
PROMPT 01
Audit
  ↓
PROMPT 02
Recovery
  ↓
PROMPT 03
Retry
  ↓
PROMPT 04
Progress
  ↓
PROMPT 05
Validation
  ↓
PROMPT 06
Queue API
  ↓
PROMPT 07
Streaming hardening
  ↓
PROMPT 08
Frontend states
  ↓
PROMPT 09
Navigation
  ↓
PROMPT 10
Active video
  ↓
PROMPT 11
Preload
  ↓
PROMPT 12
UI
  ↓
PROMPT 13
Collector foundation
  ↓
PROMPT 14
Browser collector
  ↓
PROMPT 15
Collector → SQLite
  ↓
PROMPT 16
End-to-end
  ↓
PROMPT 17
Offline mode
  ↓
PROMPT 18
Final audit
```

**18 prompt** menurut saya cukup ideal: tidak terlalu sedikit sehingga Antigravity harus mengerjakan terlalu banyak hal sekaligus, tetapi juga tidak terlalu banyak sampai project terasa terpecah-pecah.

Satu aturan penting saat menjalankannya: **jangan kirim prompt berikutnya sebelum Antigravity selesai dengan prompt sebelumnya dan test/acceptance criteria-nya lolos.** Kalau suatu prompt menghasilkan error, berhenti di prompt tersebut dan perbaiki dulu—jangan lompat ke prompt berikutnya.
