# Keputusan cleaning (log angka: `results/1-data-preparation/cleaning_log.csv`)

| Aturan | Masalah | Keputusan |
|---|---|---|
| C1 | Job ID ganda | Dicek, tidak ada |
| C2 | Deskripsi tanpa baris di daftar lowongan | Dibuang (tidak ada judul, kota, tanggal) |
| C3 | Lowongan tanpa deskripsi | Dibuang bila ada |
| C4 | Spasi khusus (NBSP) dan spasi ganda | Diganti spasi biasa |
| C5 | Salary berupa teks bebas | Diparse ke min dan max per bulan; selain "per month" dibiarkan kosong |
| C6 | listing_date UTC | Diubah ke tanggal WIB dan awal minggu Senin |
| C7 | Kota, level, industri, remote | Dinormalisasi memakai aturan di `common.py` (lihat definitions.md) |
| C8 | Deskripsi identik | Dibuang, yang paling awal dipertahankan |
| C9 | Judul dan perusahaan sama, deskripsi berbeda | Dipertahankan, hanya dicatat |

Data mentah tidak diubah (`project/data/raw/`, tidak di-commit). Aturan bisa diperbaiki lalu seluruh pipeline dijalankan ulang.
