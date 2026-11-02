# Kamus data (DuckDB `jobs.duckdb`, 4 tabel, dihubungkan lewat `job_id`)

**job_postings_raw** (1 baris = 1 lowongan apa adanya): job_id, scraped_at, batch_id, title, company, location_raw, salary_raw, description, url

**job_postings** (1 baris = 1 lowongan unik, bersih): job_id (PK), batch_id, title_norm, company, city, level (Junior/Senior/Tidak disebut), industry, work_type, salary_min, salary_max (Rp per bulan), remote_hybrid, posted_date, week_start, first_seen, last_seen

**job_skills** (1 baris = 1 skill di 1 lowongan): job_id (FK), skill (FK), match_type (kata kunci/sinonim)

**dim_skill** (kamus): skill (PK), category, synonyms (regex sinonim)

Constraint: PK, FK, CHECK level, CHECK salary_min <= salary_max, CHECK match_type. Diuji di `04_build_db.py` (hasil: `results/1-data-preparation/constraint_tests.csv`).
