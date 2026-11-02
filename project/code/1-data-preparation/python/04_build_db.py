"""Langkah 5 (bagian 2): bangun jobs.duckdb (4 tabel), uji constraint, dan catat jumlah baris. Database dibuat ulang dari nol."""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import BATCH_ID, CLEAN_DIR, DB_PATH, RAW_DIR, RES_PREP, SCRAPED_AT, SKILLS_CSV, SQL_PREP  # noqa: E402

DB_PATH.unlink(missing_ok=True)
con = duckdb.connect(str(DB_PATH))
con.execute((SQL_PREP / "01_schema.sql").read_text(encoding="utf-8"))
raw = pd.read_csv(RAW_DIR / "jobs_target_all.csv", dtype={"id": str}).merge(pd.read_csv(RAW_DIR / "jobs_detail.csv", dtype={"id": str}), on="id", how="inner")
raw = raw.rename(columns={"id": "job_id", "location": "location_raw", "salary": "salary_raw"})
raw["scraped_at"], raw["batch_id"], raw["url"] = SCRAPED_AT, BATCH_ID, "https://id.jobstreet.com/id/job/" + raw.job_id
con.register("raw_df", raw[["job_id", "scraped_at", "batch_id", "title", "company", "location_raw", "salary_raw", "description", "url"]])
con.execute("INSERT INTO job_postings_raw SELECT job_id, CAST(scraped_at AS DATE), batch_id, title, company, location_raw, salary_raw, description, url FROM raw_df")
sk = pd.read_csv(SKILLS_CSV)
sk["synonyms"] = sk.synonym_regex.fillna("")
con.register("sk_df", sk[["skill", "category", "synonyms"]])
con.execute("INSERT INTO dim_skill SELECT * FROM sk_df")
jp = pd.read_csv(CLEAN_DIR / "job_postings.csv", dtype={"job_id": str})
con.register("jp_df", jp)
con.execute("""INSERT INTO job_postings SELECT job_id, batch_id, title_norm, company, city, level, industry, work_type, CAST(salary_min AS BIGINT), CAST(salary_max AS BIGINT),
               remote_hybrid, CAST(posted_date AS DATE), CAST(week_start AS DATE), CAST(first_seen AS DATE), CAST(last_seen AS DATE) FROM jp_df""")
js = pd.read_csv(CLEAN_DIR / "job_skills.csv", dtype={"job_id": str})
con.register("js_df", js)
con.execute("INSERT INTO job_skills SELECT job_id, skill, match_type FROM js_df")

# uji constraint: baris salah harus ditolak
one = "(SELECT job_id FROM job_postings LIMIT 1)"
tests = [("job_id ganda di job_postings", f"INSERT INTO job_postings SELECT * REPLACE ('{BATCH_ID}' AS batch_id) FROM job_postings LIMIT 1"),
         ("job_skills dengan job_id yang tidak ada", "INSERT INTO job_skills VALUES ('0000', 'SQL', 'kata kunci')"),
         ("job_skills dengan skill yang tidak ada di dim_skill", f"INSERT INTO job_skills VALUES ({one}, 'Cobol', 'kata kunci')"),
         ("level di luar daftar", "INSERT INTO job_postings SELECT * REPLACE ('9999' AS job_id, 'Manajer' AS level) FROM job_postings LIMIT 1"),
         ("salary_min lebih besar dari salary_max", "INSERT INTO job_postings SELECT * REPLACE ('9998' AS job_id, 10 AS salary_min, 5 AS salary_max) FROM job_postings LIMIT 1"),
         ("match_type di luar daftar", f"INSERT INTO job_skills VALUES ({one}, 'SQL', 'tebakan')")]
res = []
for name, q in tests:
    try:
        con.execute(q)
        res.append((name, "diterima"))
    except Exception as e:
        res.append((name, "ditolak"))
pd.DataFrame(res, columns=["test", "outcome"]).to_csv(RES_PREP / "constraint_tests.csv", index=False)

# konsistensi antar tabel
cons = [("job_skills tanpa lowongan", "SELECT count(*) FROM job_skills s LEFT JOIN job_postings p USING(job_id) WHERE p.job_id IS NULL"),
        ("lowongan tanpa baris di job_postings_raw", "SELECT count(*) FROM job_postings p LEFT JOIN job_postings_raw r USING(job_id) WHERE r.job_id IS NULL"),
        ("lowongan dengan salary_min tetapi salary_max kosong", "SELECT count(*) FROM job_postings WHERE (salary_min IS NULL) <> (salary_max IS NULL)"),
        ("posted_date setelah scraped_at", "SELECT count(*) FROM job_postings p JOIN job_postings_raw r USING(job_id) WHERE p.posted_date > r.scraped_at"),
        ("week_start bukan hari Senin", "SELECT count(*) FROM job_postings WHERE dayofweek(week_start) <> 1")]
pd.DataFrame([(n, con.execute(q).fetchone()[0]) for n, q in cons], columns=["check", "violations"]).to_csv(RES_PREP / "consistency_checks.csv", index=False)
rows = pd.DataFrame([(t, con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]) for t in ("job_postings_raw", "job_postings", "job_skills", "dim_skill")], columns=["table", "rows"])
rows.to_csv(RES_PREP / "table_rows.csv", index=False)
print(rows.to_string(index=False)); print(pd.DataFrame(res, columns=["test", "outcome"]).to_string(index=False))
con.close()
