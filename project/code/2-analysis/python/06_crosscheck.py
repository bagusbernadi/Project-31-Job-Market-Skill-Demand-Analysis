"""Langkah 7 (cek silang): hasil SQL vs hitungan pandas, nilai per nilai, toleransi 1e-6. Juga cek silang dengan studi awal (skill_freq.csv, repo scraper lama)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CLEAN_DIR, RES_ANALYSIS, SKILLS_CSV  # noqa: E402
from kpi_pandas import compute, load  # noqa: E402

jobs, js = load(CLEAN_DIR)
pdres = compute(jobs, js, pd.read_csv(SKILLS_CSV))
KEYS = {"skill_share": ["skill"], "skill_cooc": ["skill_a", "skill_b"], "skill_by_level": ["level", "skill"], "salary_by_skill": ["skill"], "city_summary": ["city"],
        "industry_summary": ["industry"], "salary_coverage": ["dimension", "val"], "remote_share": [], "weekly_jobs": ["week_start"], "weekly_skill": ["week_start", "skill"]}
rows = []
for name, keys in KEYS.items():
    a = pd.read_csv(RES_ANALYSIS / f"{name}.csv")
    b = pdres[name].copy()
    vals = [c for c in b.columns if c not in keys and c in a.columns and c not in ("category", "total", "cumulative_jobs", "change_vs_prev", "share_prev")]
    if keys:
        for df in (a, b):
            for k in keys:
                df[k] = df[k].astype(str)
        m = a.merge(b, on=keys, how="outer", suffixes=("_sql", "_pd"), indicator=True)
        assert (m._merge == "both").all(), f"{name}: baris tidak sama\n{m[m._merge != 'both']}"
    else:
        m = pd.concat([a.add_suffix("_sql"), b.add_suffix("_pd")], axis=1)
    for v in vals:
        x, y = pd.to_numeric(m[f"{v}_sql"], errors="coerce"), pd.to_numeric(m[f"{v}_pd"], errors="coerce")
        ok = np.isclose(x.fillna(-1), y.fillna(-1), atol=1e-6)
        rows.append(dict(query=name, metric=v, rows_compared=len(m), mismatches=int((~ok).sum()), status="PASS" if ok.all() else "FAIL"))
cx = pd.DataFrame(rows)
cx.to_csv(RES_ANALYSIS / "crosscheck.csv", index=False)
print(cx.to_string(index=False))

# cek silang dengan studi awal: skill_freq.csv dari repo data-analyst-job-scraper (48 lowongan yang sama)
old_path = Path(__file__).resolve().parents[3] / "data" / "reference" / "old_study_skill_freq.csv"
if old_path.exists():
    old = pd.read_csv(old_path).rename(columns={"skill": "old_skill", "jumlah": "old_jobs", "persen": "old_pct"})
    new = pdres["skill_share"][["skill", "jobs", "share"]]
    mp = {"Statistik (skill)": "Statistik"}   # Pandas/Numpy di studi awal adalah sinonim Python di kamus baru, tidak dibandingkan satu per satu
    old["skill"] = old.old_skill.replace(mp)
    cmp_ = old.merge(new, on="skill", how="left").rename(columns={"jobs": "new_jobs"})
    cmp_["new_pct"] = (cmp_.share * 100).round(1)
    cmp_["selisih_jumlah"] = cmp_.new_jobs - cmp_.old_jobs
    cmp_["status"] = np.where(cmp_.new_jobs.isna(), "Tidak ada di kamus baru", np.where(cmp_.selisih_jumlah == 0, "Sama", "Beda"))
    cmp_[["old_skill", "skill", "old_jobs", "new_jobs", "old_pct", "new_pct", "selisih_jumlah", "status"]].to_csv(RES_ANALYSIS / "old_study_compare.csv", index=False)
    print(cmp_[["old_skill", "old_jobs", "new_jobs", "selisih_jumlah"]].to_string(index=False))
assert (cx.status == "PASS").all()
