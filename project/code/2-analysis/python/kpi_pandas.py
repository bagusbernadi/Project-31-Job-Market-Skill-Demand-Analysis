"""Hitungan pandas yang menyamai query SQL (02_queries.sql), dipakai untuk cek silang dan analisis."""
import itertools

import pandas as pd

FOUR = ["Excel", "SQL", "Python", "Power BI", "Tableau"]


def load(clean_dir):
    jobs = pd.read_csv(clean_dir / "job_postings.csv", dtype={"job_id": str})
    js = pd.read_csv(clean_dir / "job_skills.csv", dtype={"job_id": str})
    return jobs, js


def compute(jobs, js, skills):
    n = len(jobs)
    out = {}
    cnt = js.groupby("skill").job_id.nunique()
    ss = skills[["skill", "category"]].copy()
    ss["jobs"] = ss.skill.map(cnt).fillna(0).astype(int)
    ss["total"] = n
    ss["share"] = ss.jobs / n
    out["skill_share"] = ss.sort_values(["jobs", "skill"], ascending=[False, True]).reset_index(drop=True)
    sets = js[js.skill != "Dashboard"].groupby("job_id").skill.apply(lambda s: sorted(set(s)))
    pairs = pd.Series([p for lst in sets for p in itertools.combinations(lst, 2)]).value_counts()
    cooc = pd.DataFrame([(a, b, c) for (a, b), c in pairs.items()], columns=["skill_a", "skill_b", "jobs"])
    out["skill_cooc"] = cooc.sort_values(["jobs", "skill_a", "skill_b"], ascending=[False, True, True]).reset_index(drop=True)
    m = js[js.skill.isin(FOUR)].merge(jobs[["job_id", "level"]], on="job_id")
    nl = jobs.level.value_counts()
    sl = m.groupby(["level", "skill"]).size().reset_index(name="jobs")
    sl["n_level"] = sl.level.map(nl)
    sl["share"] = sl.jobs / sl.n_level
    out["skill_by_level"] = sl[["level", "n_level", "skill", "jobs", "share"]]
    sal = js.merge(jobs[jobs.salary_min.notna()][["job_id", "salary_min", "salary_max"]], on="job_id")
    sbs = sal.groupby("skill").agg(n_salary=("job_id", "count"), median_min=("salary_min", "median"), median_max=("salary_max", "median"),
                                    lowest_min=("salary_min", "min"), highest_max=("salary_max", "max")).reset_index()
    out["salary_by_skill"] = sbs
    for key, col in (("city_summary", "city"), ("industry_summary", "industry")):
        g = jobs.groupby(col).agg(jobs=("job_id", "count"), n_salary=("salary_min", "count"), median_min=("salary_min", "median"), median_max=("salary_max", "median")).reset_index()
        g["share"] = g.jobs / n
        out[key] = g[[col, "jobs", "share", "n_salary", "median_min", "median_max"]]
    rows = []
    for dim, col, label in (("Semua", None, "Semua lowongan"), ("Kota", "city", None), ("Level", "level", None), ("Tipe kerja", "work_type", None)):
        if col is None:
            rows.append((dim, label, n, int(jobs.salary_min.notna().sum())))
        else:
            for v, g in jobs.groupby(col):
                rows.append((dim, v, len(g), int(g.salary_min.notna().sum())))
    cov = pd.DataFrame(rows, columns=["dimension", "val", "jobs", "with_salary"])
    cov["coverage"] = cov.with_salary / cov.jobs
    out["salary_coverage"] = cov
    out["remote_share"] = pd.DataFrame([dict(jobs=n, remote_hybrid_jobs=int(jobs.remote_hybrid.sum()), share=jobs.remote_hybrid.mean())])
    wj = jobs.groupby("week_start").size().reset_index(name="jobs")
    out["weekly_jobs"] = wj
    ws = js[js.skill.isin(FOUR)].merge(jobs[["job_id", "week_start"]], on="job_id").groupby(["week_start", "skill"]).size().reset_index(name="jobs")
    ws["n_week"] = ws.week_start.map(wj.set_index("week_start").jobs)
    ws["share"] = ws.jobs / ws.n_week
    out["weekly_skill"] = ws
    return out
