"""Membuat README.md di root repo; semua angka dibaca dari CSV hasil."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import ROOT, SAMPLE_N, result  # noqa: E402

R = lambda n: pd.read_csv(result(n))
f = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")
pc = lambda v, d=1: f(v * 100, d) + "%"
n = lambda v: f"{int(round(v)):,}".replace(",", ".")

dq = R("data_quality_summary.csv").set_index("item").value
ss, ci, cooc, city, ssum = R("skill_share.csv"), R("share_ci.csv").set_index("item"), R("skill_cooc.csv"), R("city_summary.csv"), R("salary_summary.csv").iloc[0]
sm, nxt, hyp, cx, ev = R("skill_match.csv").set_index("boleh_kurang"), R("skill_next.csv"), R("hypotheses.csv"), R("crosscheck.csv"), R("skill_eval.csv").iloc[-1]
rem = R("remote_share.csv").iloc[0]
S = ss.set_index("skill")
tot, nraw, ndup, nsal = int(dq["Lowongan unik dianalisis"]), int(dq["Lowongan setelah digabung dengan deskripsi"]), int(dq["Duplikat dibuang"]), int(dq["Salary tercantum"])
top = ss[ss.skill != "Dashboard"].head(5)
tops = ", ".join(f"{r.skill} {pc(r.share, 0)}" for r in top.itertuples())
c0 = city.iloc[0]
cxok = int((cx.status == "PASS").sum())
nh = hyp.verdict.value_counts()

md = f"""[← Back to portfolio](https://bagusbernadi.github.io/)

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

- {n(nraw)} lowongan dan deskripsinya dari arsip DataCenter; {n(ndup)} iklan ganda dibuang sehingga {n(tot)} lowongan unik dianalisis.
- 4 tabel di DuckDB: `job_postings_raw`, `job_postings`, `job_skills` ({n(R('table_rows.csv').set_index('table').rows['job_skills'])} baris), `dim_skill` ({n(len(ss))} skill), dengan constraint yang diuji.
- Data 2.560 postingan project lama tidak ditemukan; industri perusahaan tidak tersedia (bidang kerja Jobstreet dipakai sebagai pengganti).

## 3. Analysis

- Skill teratas: {tops} (dari {n(tot)} lowongan; interval kepercayaan lebar).
- Pasangan terbanyak: {cooc.skill_a[0]} dan {cooc.skill_b[0]} ({n(cooc.jobs[0])} lowongan).
- {c0.city} memegang {pc(c0.share)} lowongan ({n(c0.jobs)} dari {n(tot)}). Remote atau hybrid: {pc(rem.share)}.
- Salary dicantumkan {n(nsal)} lowongan ({pc(nsal / tot)}); median Rp {f(ssum.median_min / 1e6, 2)} sampai {f(ssum.median_max / 1e6, 2)} juta per bulan, terlalu sedikit untuk membandingkan skill atau kota.
- Skill extraction: precision {pc(ev.precision, 0)} dan recall {pc(ev.recall, 0)} pada {SAMPLE_N} lowongan berlabel (label dari Claude, bukan manusia). Cek silang SQL vs pandas: {cxok}/{len(cx)} PASS.
- Hipotesis: {n(nh.get('Terbukti', 0))} terbukti, {n(nh.get('Sebagian', 0))} sebagian, {n(nh.get('Tidak terbukti', 0))} tidak terbukti.

## 4. Recommendation

Prioritaskan Excel dan SQL, lalu Power BI. Jangan memakai angka salary di sini sebagai patokan negosiasi. Ulangi analisis setelah scraping mingguan berjalan beberapa minggu.

## 5. Impact

Estimated: dengan Excel, SQL, dan Python (asumsi skill dimiliki), {pc(sm.loc[0].share)} lowongan bisa dilamar tanpa kekurangan skill; menambah {nxt.skill[0]} atau {nxt.skill[1]} menaikkannya menjadi {pc(nxt.share_setelah[0])}. Angka dari {n(tot)} lowongan, bukan statistik pasar.

## Batasan

- Hanya {n(tot)} lowongan dari satu platform dan satu kali ambil; belum ada tren mingguan.
- Lisensi data belum diverifikasi; robots.txt dan ketentuan layanan belum diperiksa.
- Scraper (`scrape_jobs.py`) dan `weekly_scrape.yml` ditulis tetapi belum pernah dijalankan. Dashboard belum di-deploy.
- Validasi skill extraction memakai {SAMPLE_N} lowongan, bukan 100, dengan label dari Claude.
- Level dari judul, bidang kerja sebagai pengganti industri, dan skill dimiliki adalah asumsi.

## Menjalankan

```
pip install -r project/requirements.txt
export DATACENTER_ZIP=/path/ke/jobstreet-job-postings.zip
cd project/code/1-data-preparation/python && for s in 01 02 03 04; do python ${{s}}_*.py; done
cd ../../2-analysis/python && for s in 05 06 07 08 09; do python ${{s}}_*.py; done
cd ../../3-presentation/python && for s in 10 11 12; do python ${{s}}_*.py; done
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
"""
(ROOT.parent / "README.md").write_text(md, encoding="utf-8")
print("README.md ditulis")
