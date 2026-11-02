[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 31: Job Market Scraping & Skill Demand Analysis

**Status: Dikerjakan di branch `project-31-build` (menunggu review sebelum digabung ke `main`). Scraper, jadwal mingguan, dan dashboard publik belum dijalankan; Q10 dan Q11 belum bisa dijawab.**

Halaman rancangan dan Report: https://bagusbernadi.github.io/Project-31-Job-Market-Skill-Demand-Analysis/

| | |
|---|---|
| Kategori | Data analyst (pasar kerja, web scraping) |
| Tingkat | Menengah |
| Data | Lowongan Data Analyst Jobstreet Indonesia, satu kali ambil (versi 1, Oktober 2026): [DataCenter](https://github.com/bagusbernadi/DataCenter/tree/main/jobstreet-job-postings); sumber resmi: [id.jobstreet.com](https://id.jobstreet.com/). Lisensi belum diverifikasi |
| Tools | Python (pandas, Playwright, SciPy, statsmodels), SQL (DuckDB), regex + kamus skill, Jupyter, Streamlit + Plotly, GitHub Actions, GitHub |

## 1. Problem

Skill dan kisaran salary apa yang paling banyak diminta pada lowongan Data Analyst di Indonesia, di kota dan industri mana, dan bagaimana trennya dari minggu ke minggu? Dipecah menjadi 14 pertanyaan (9 prioritas utama); jawabannya ada di tab Report pada halaman project.

## 2. Data

- 51 lowongan dan deskripsinya dari arsip DataCenter; 3 iklan ganda dibuang sehingga 48 lowongan unik dianalisis.
- 4 tabel di DuckDB: `job_postings_raw`, `job_postings`, `job_skills` (165 baris), `dim_skill` (15 skill), dengan constraint yang diuji.
- Data 2.560 postingan project lama tidak ditemukan; industri perusahaan tidak tersedia (bidang kerja Jobstreet dipakai sebagai pengganti).

## 3. Analysis

- Skill teratas: Excel 62%, SQL 46%, Power BI 44%, Tableau 35%, Python 31% (dari 48 lowongan; interval kepercayaan lebar).
- Pasangan terbanyak: Power BI dan SQL (15 lowongan).
- Jakarta memegang 64,6% lowongan (31 dari 48). Remote atau hybrid: 4,2%.
- Salary dicantumkan 9 lowongan (18,8%); median Rp 5,75 sampai 7,50 juta per bulan, terlalu sedikit untuk membandingkan skill atau kota.
- Skill extraction: precision 100% dan recall 97% pada 20 lowongan berlabel (label dari Claude, bukan manusia). Cek silang SQL vs pandas: 31/31 PASS.
- Hipotesis: 1 terbukti, 4 sebagian, 0 tidak terbukti.

## 4. Recommendation

Prioritaskan Excel dan SQL, lalu Power BI. Jangan memakai angka salary di sini sebagai patokan negosiasi. Ulangi analisis setelah scraping mingguan berjalan beberapa minggu.

## 5. Impact

Estimated: dengan Excel, SQL, dan Python (asumsi skill dimiliki), 35,4% lowongan bisa dilamar tanpa kekurangan skill; menambah Google Sheets atau Power BI menaikkannya menjadi 43,8%. Angka dari 48 lowongan, bukan statistik pasar.

## Batasan

- Hanya 48 lowongan dari satu platform dan satu kali ambil; belum ada tren mingguan.
- Lisensi data belum diverifikasi; robots.txt dan ketentuan layanan belum diperiksa.
- Scraper (`scrape_jobs.py`) dan `weekly_scrape.yml` ditulis tetapi belum pernah dijalankan. Dashboard belum di-deploy.
- Validasi skill extraction memakai 20 lowongan, bukan 100, dengan label dari Claude.
- Level dari judul, bidang kerja sebagai pengganti industri, dan skill dimiliki adalah asumsi.

## Menjalankan

```
pip install -r project/requirements.txt
export DATACENTER_ZIP=/path/ke/jobstreet-job-postings.zip
cd project/code/1-data-preparation/python && for s in 01 02 03 04; do python ${s}_*.py; done
cd ../../2-analysis/python && for s in 05 06 07 08 09; do python ${s}_*.py; done
cd ../../3-presentation/python && for s in 10 11 12; do python ${s}_*.py; done
streamlit run ../streamlit/app.py
python design-and-report/src/build_report.py   # dari root repo
```

## Struktur repository

```
index.html                 Pengalihan ke design-and-report/
design-and-report/         Halaman Design dan Report (src/ berisi generator)
project/
  code/1-data-preparation  Pemuatan, cleaning, skill extraction, database, scraper (python, sql)
  code/2-analysis          Query, cek silang, validasi skill, uji hipotesis, skill match
  code/3-presentation      Dashboard data, notebook, README, Streamlit
  results/                 CSV hasil per tahap, notebook
  docs/                    Definisi, kamus data, keputusan cleaning, etika scraping
  data/                    reference/ (kamus skill); raw dan clean tidak di-commit
.github/workflows/         weekly_scrape.yml (belum dijalankan)
```
