# Definisi dan aturan (asumsi diberi label)

| Istilah | Definisi |
|---|---|
| Lowongan unik | Lowongan setelah deskripsi identik dibuang (yang paling awal dipertahankan). Data versi 1: 51 lowongan, 48 unik |
| Skill share | Lowongan yang menyebut skill ÷ lowongan unik. Satu lowongan dihitung satu kali per skill |
| Skill | Item di `data/reference/skills.csv` (15 skill). `kata kunci` = kata utama cocok; `sinonim` = hanya sinonim cocok. "spreadsheet" dihitung Excel; "MS Office" tidak |
| Dashboard (skill) | Konsep, bukan tool. Dihitung di Q1 tetapi tidak di skill match dan co-occurrence |
| Kota | Hasil normalisasi `location` (aturan di `common.py`, `CITY_RULES`). Kecamatan di Jakarta menjadi Jakarta |
| Industri (asumsi) | Jobstreet tidak memberi industri perusahaan. Kolom `industry` diisi klasifikasi bidang kerja Jobstreet (`category`) |
| Level (asumsi) | Dari judul: Senior (senior, sr, head, lead, supervisor, manager, principal), Junior (junior, jr, fresh, intern, trainee, entry), sisanya "Tidak disebut". "Staff" tidak dianggap junior |
| Remote atau hybrid | Judul atau deskripsi memuat remote, hybrid, WFH, atau work from home. Kata "remote" pada kalimat larangan ("remote tidak tersedia") tetap terhitung (batasan) |
| Cakupan salary | Lowongan dengan salary per bulan ÷ semua lowongan |
| Minggu | Awal minggu (Senin) dari `posted_date` (tanggal tayang, WIB), bukan minggu scraping |
| Skill match | Lowongan yang semua skill tool-nya (tanpa Dashboard) dimiliki, dengan toleransi k skill kurang. Lowongan tanpa skill tertulis dianggap bisa dilamar |
| Skill dimiliki (asumsi) | `data/reference/my_skills.csv`: Excel, SQL, Python. Bisa diganti |
| Verdict hipotesis | Terbukti: estimasi titik memenuhi dan uji satu sisi p < 0,05. Sebagian: estimasi titik memenuhi tetapi p >= 0,05, sebagian komponen terpenuhi, atau kelompok < 5 lowongan. Tidak terbukti: estimasi titik tidak memenuhi |
| CI | Interval Wilson 95% untuk proporsi |
