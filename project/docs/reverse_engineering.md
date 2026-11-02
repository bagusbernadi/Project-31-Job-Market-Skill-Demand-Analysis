# Reverse engineering project scraping lama (langkah 1)

Sumber: repo `bagusbernadi/data-analyst-job-scraper` (studi awal, Oktober 2026). Repo `Web_scraping_and_Job_Analyze` tidak bisa dibuka dari sesi pembuatan, jadi tidak ikut ditelusuri.

| File lama | Fungsi | Dipakai ulang di project ini |
|---|---|---|
| `scrape_list2.py` | Playwright membuka hasil pencarian Jobstreet (3 keyword, maks. 10 halaman) dan membaca `window.SEEK_REDUX_DATA` | Ya, fungsi `extract_jobs` dipertahankan di `scrape_jobs.py` |
| `scrape_detail2.py` | Menyaring judul (regex) lalu membuka halaman lowongan dan membaca `[data-automation="jobAdDetails"]` | Ya, filter judul dan selector dipertahankan |
| `check_filter.py` | Mengecek judul yang terbuang filter | Tidak (cek manual cukup) |
| `analysis.py` | Frekuensi skill (regex), pengalaman, gaji, kota, grafik | Skill dan gaji diganti kamus CSV dan database; dicocokkan ulang lewat `old_study_compare.csv` |
| `skill_freq.csv` | Hasil agregat studi awal | Disalin ke `project/data/reference/old_study_skill_freq.csv` sebagai pembanding |

Yang ditemukan:
- Alur: 3 keyword, 319 lowongan unik, disaring judul menjadi 51 lowongan target, deskripsi diambil, iklan dengan deskripsi identik dibuang sehingga 48 lowongan dianalisis.
- Satu kali jalan, satu waktu (Oktober 2026), tanpa kolom tanggal scraping. Tidak ada batch lain.
- Cara kerja lama: `headless=False`, tidak ada log, tidak ada pengecekan robots.txt, berhenti saat selector tidak ketemu.
- **Angka "2.560 postingan" pada daftar portofolio dan rancangan tidak ditemukan** di repo lama maupun di DataCenter. Data yang ada adalah 51 lowongan (53 deskripsi). Asal angka 2.560 perlu dikonfirmasi pemilik.
- Periode tayang (posted_date, WIB): 25 Maret sampai 16 Oktober 2026; 44 dari 48 lowongan unik tayang sejak 14 September 2026 (dihitung dari data).
