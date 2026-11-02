# Catatan etika scraping dan kebijakan data (langkah 2)

- Konten lowongan adalah milik Jobstreet dan perusahaan pemasang. Ketentuan layanan Jobstreet **belum dicek** dan robots.txt **belum diperiksa dari sesi ini** (jaringan sandbox memblokir situs). `scrape_jobs.py` membaca robots.txt di awal tiap batch dan berhenti bila halaman dilarang; hasilnya belum pernah dilihat.
- Jeda acak 6 sampai 12 detik antar permintaan, coba ulang dengan jeda lebih panjang, berhenti bila selector tidak ditemukan, maksimal 5 halaman per keyword.
- Data mentah (judul, perusahaan, deskripsi) tidak di-commit. Disimpan privat di repo DataCenter sebagai arsip pribadi.
- Yang dipublikasikan: tabel agregat dan `dash_rows.csv` (atribut turunan: minggu, kota, level, bidang, salary, flag skill; tanpa job_id, judul, perusahaan, atau teks).
- Lisensi data: tidak ada. Bila pemilik menilai atribut turunan itu terlalu dekat dengan konten asli, hapus `dash_rows.csv` dan dashboard memakai tabel agregat saja.
