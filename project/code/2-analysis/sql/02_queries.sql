-- Query analitik (DuckDB). Setiap blok "-- name: x" menghasilkan results/2-analysis/x.csv
-- name: skill_share
WITH n AS (SELECT count(*) AS total FROM job_postings)
SELECT s.skill, s.category, count(DISTINCT j.job_id) AS jobs, n.total, count(DISTINCT j.job_id) * 1.0 / n.total AS share
FROM dim_skill s CROSS JOIN n LEFT JOIN job_skills j ON j.skill = s.skill
GROUP BY s.skill, s.category, n.total ORDER BY jobs DESC, s.skill;
-- name: skill_cooc
SELECT a.skill AS skill_a, b.skill AS skill_b, count(*) AS jobs
FROM job_skills a JOIN job_skills b ON a.job_id = b.job_id AND a.skill < b.skill
WHERE a.skill <> 'Dashboard' AND b.skill <> 'Dashboard'
GROUP BY 1, 2 ORDER BY jobs DESC, skill_a, skill_b;
-- name: skill_by_level
WITH lv AS (SELECT level, count(*) AS n_level FROM job_postings GROUP BY level)
SELECT p.level, lv.n_level, js.skill, count(*) AS jobs, count(*) * 1.0 / lv.n_level AS share
FROM job_postings p JOIN lv USING (level) JOIN job_skills js ON js.job_id = p.job_id
WHERE js.skill IN ('Excel', 'SQL', 'Python', 'Power BI', 'Tableau')
GROUP BY p.level, lv.n_level, js.skill ORDER BY p.level, jobs DESC, js.skill;
-- name: salary_by_skill
SELECT js.skill, count(*) AS n_salary, median(p.salary_min) AS median_min, median(p.salary_max) AS median_max, min(p.salary_min) AS lowest_min, max(p.salary_max) AS highest_max
FROM job_postings p JOIN job_skills js ON js.job_id = p.job_id WHERE p.salary_min IS NOT NULL
GROUP BY js.skill ORDER BY n_salary DESC, js.skill;
-- name: city_summary
SELECT city, count(*) AS jobs, count(*) * 1.0 / (SELECT count(*) FROM job_postings) AS share, count(salary_min) AS n_salary, median(salary_min) AS median_min, median(salary_max) AS median_max
FROM job_postings GROUP BY city ORDER BY jobs DESC, city;
-- name: industry_summary
SELECT industry, count(*) AS jobs, count(*) * 1.0 / (SELECT count(*) FROM job_postings) AS share, count(salary_min) AS n_salary, median(salary_min) AS median_min, median(salary_max) AS median_max
FROM job_postings GROUP BY industry ORDER BY jobs DESC, industry;
-- name: salary_coverage
WITH u AS (SELECT 'Semua' AS dimension, 'Semua lowongan' AS val, salary_min FROM job_postings
           UNION ALL SELECT 'Kota', city, salary_min FROM job_postings
           UNION ALL SELECT 'Level', level, salary_min FROM job_postings
           UNION ALL SELECT 'Tipe kerja', work_type, salary_min FROM job_postings)
SELECT dimension, val, count(*) AS jobs, count(salary_min) AS with_salary, count(salary_min) * 1.0 / count(*) AS coverage
FROM u GROUP BY dimension, val ORDER BY dimension, jobs DESC, val;
-- name: remote_share
SELECT count(*) AS jobs, sum(CASE WHEN remote_hybrid THEN 1 ELSE 0 END) AS remote_hybrid_jobs, avg(CASE WHEN remote_hybrid THEN 1.0 ELSE 0.0 END) AS share FROM job_postings;
-- name: weekly_jobs
SELECT week_start, count(*) AS jobs, sum(count(*)) OVER (ORDER BY week_start) AS cumulative_jobs,
       count(*) - lag(count(*)) OVER (ORDER BY week_start) AS change_vs_prev
FROM job_postings GROUP BY week_start ORDER BY week_start;
-- name: weekly_skill
WITH wk AS (SELECT week_start, count(*) AS n_week FROM job_postings GROUP BY week_start),
     ws AS (SELECT p.week_start, js.skill, count(*) AS jobs FROM job_postings p JOIN job_skills js ON js.job_id = p.job_id
            WHERE js.skill IN ('Excel', 'SQL', 'Python', 'Power BI', 'Tableau') GROUP BY p.week_start, js.skill)
SELECT ws.week_start, ws.skill, wk.n_week, ws.jobs, ws.jobs * 1.0 / wk.n_week AS share,
       lag(ws.jobs * 1.0 / wk.n_week) OVER (PARTITION BY ws.skill ORDER BY ws.week_start) AS share_prev
FROM ws JOIN wk USING (week_start) ORDER BY ws.skill, ws.week_start;
