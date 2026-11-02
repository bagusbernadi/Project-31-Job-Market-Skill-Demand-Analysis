-- Empat tabel project (DuckDB). Data mentah terpisah dari data bersih.
CREATE TABLE job_postings_raw (
  job_id VARCHAR, scraped_at DATE, batch_id VARCHAR, title VARCHAR, company VARCHAR, location_raw VARCHAR,
  salary_raw VARCHAR, description VARCHAR, url VARCHAR
);
CREATE TABLE dim_skill (
  skill VARCHAR PRIMARY KEY, category VARCHAR NOT NULL, synonyms VARCHAR
);
CREATE TABLE job_postings (
  job_id VARCHAR PRIMARY KEY, batch_id VARCHAR NOT NULL, title_norm VARCHAR NOT NULL, company VARCHAR NOT NULL,
  city VARCHAR NOT NULL, level VARCHAR NOT NULL CHECK (level IN ('Junior','Senior','Tidak disebut')),
  industry VARCHAR, work_type VARCHAR, salary_min BIGINT, salary_max BIGINT, remote_hybrid BOOLEAN NOT NULL,
  posted_date DATE NOT NULL, week_start DATE NOT NULL, first_seen DATE NOT NULL, last_seen DATE NOT NULL,
  CHECK (salary_min IS NULL OR salary_max >= salary_min)
);
CREATE TABLE job_skills (
  job_id VARCHAR NOT NULL REFERENCES job_postings(job_id), skill VARCHAR NOT NULL REFERENCES dim_skill(skill),
  match_type VARCHAR NOT NULL CHECK (match_type IN ('kata kunci','sinonim')), PRIMARY KEY (job_id, skill)
);
