[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 31: Job Market Scraping & Skill Demand Analysis

**Status: Design (rancangan).**

**Tujuan:** Membangun pipeline scraping mingguan yang mengumpulkan lowongan Data Analyst di Indonesia untuk menemukan skill, kota, industri, dan kisaran salary yang paling banyak diminta, sehingga prioritas belajar dan target lamaran bisa ditentukan berdasarkan data.

Halaman rancangan: https://bagusbernadi.github.io/Project-31-Job-Market-Skill-Demand-Analysis/

| | |
|---|---|
| Kategori | Pasar kerja / karier |
| Tingkat | Sulit |
| Data | Lowongan Jobstreet hasil scraping sendiri (data mentah tidak dipublikasikan) |
| Tools | Python (Playwright, requests, pandas), regex, DuckDB + SQL, GitHub Actions, Streamlit + Plotly |

## 1. Problem
Skill (SQL, Python, Excel, BI) dan kisaran salary apa yang paling banyak diminta pada lowongan Data Analyst di Indonesia, di kota/industri mana, dan bagaimana trennya dari minggu ke minggu?

## 2. Data
- Sumber data: [here](https://github.com/bagusbernadi/Web_scraping_and_Job_Analyze) (Versi: 2.560 postingan dari project lama, struktur dan periode ditelusuri ulang lewat reverse engineering; Tanggal akses: dicatat saat Tahap A)
- Sumber data lanjutan: [here](https://id.jobstreet.com/) (Versi: scraping mingguan, satu batch per minggu; Tanggal akses: dicatat otomatis di kolom `scraped_at`)
- Ukuran (perkiraan, belum diverifikasi): 2.560 postingan + ±150–300 postingan baru per minggu selama ±12 minggu.
- Scraping mengikuti robots.txt dan ketentuan situs. Data mentah tidak dipublikasikan, hanya tabel agregat.

## 3. Analysis
Belum dikerjakan. Rencana langkah ada di bagian Work Plan pada halaman rancangan.

## 4. Recommendation
Belum dikerjakan.

## 5. Impact
Belum dikerjakan. Angka dampak nanti diberi label `estimated` / `simulated`.

## Batasan yang sudah diketahui
- Salary bias: sebagian besar lowongan tidak mencantumkan salary.
- Satu platform (Jobstreet) belum tentu mewakili seluruh pasar kerja.
- Skill yang disebut di deskripsi belum tentu syarat wajib.
- Angka skill match adalah estimasi.

## Struktur repository
```
index.html          # halaman rancangan (GitHub Pages)
README.md
scraper/            # (rencana) scraper Playwright
scripts/            # (rencana) cleaning, skill extraction, load
config/skills.csv   # (rencana) kamus skill
sql/                # (rencana) query analitik
dashboard/          # (rencana) aplikasi Streamlit
.github/workflows/  # (rencana) jadwal scraping mingguan
```
