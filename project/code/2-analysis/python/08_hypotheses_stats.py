"""Langkah 8: interval kepercayaan (Wilson), lima hipotesis Design (bunyi persis seperti rancangan), perbandingan level, dan sensitivitas duplikat (Q14).
Aturan verdict (project/docs/definitions.md): Terbukti = estimasi titik memenuhi dan uji satu sisi p < 0,05; Sebagian = estimasi titik memenuhi tetapi p >= 0,05,
sebagian komponen terpenuhi, atau kelompok terlalu kecil untuk diuji; Tidak terbukti = estimasi titik tidak memenuhi."""
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest, fisher_exact
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ALPHA, CLEAN_DIR, MIN_GROUP, RES_ANALYSIS  # noqa: E402
from kpi_pandas import load  # noqa: E402

jobs, js = load(CLEAN_DIR)
n = len(jobs)
has = lambda s: set(js[js.skill == s].job_id)
cnt = lambda s: len(has(s))

# CI Wilson 95% untuk porsi skill dan cakupan salary
rows = []
for s, c in js.groupby("skill").job_id.nunique().sort_values(ascending=False).items():
    lo, hi = proportion_confint(c, n, alpha=ALPHA, method="wilson")
    rows.append((s, c, n, c / n, lo, hi))
lo, hi = proportion_confint(int(jobs.salary_min.notna().sum()), n, alpha=ALPHA, method="wilson")
rows.append(("(cakupan salary)", int(jobs.salary_min.notna().sum()), n, jobs.salary_min.notna().mean(), lo, hi))
lo, hi = proportion_confint(int(jobs.remote_hybrid.sum()), n, alpha=ALPHA, method="wilson")
rows.append(("(remote atau hybrid)", int(jobs.remote_hybrid.sum()), n, jobs.remote_hybrid.mean(), lo, hi))
pd.DataFrame(rows, columns=["item", "jobs", "total", "share", "ci_low", "ci_high"]).round(8).to_csv(RES_ANALYSIS / "share_ci.csv", index=False)

sal = jobs[jobs.salary_min.notna()]
pd.DataFrame([dict(n_salary=len(sal), median_min=sal.salary_min.median(), median_max=sal.salary_max.median(), lowest_min=sal.salary_min.min(), highest_max=sal.salary_max.max())]).to_csv(RES_ANALYSIS / "salary_summary.csv", index=False)

H = []
# H1: SQL dan Excel > 60%
comp = {s: (cnt(s), binomtest(cnt(s), n, 0.6, alternative="greater").pvalue) for s in ("SQL", "Excel")}
pt_ok = [comp[s][0] / n > 0.6 for s in comp]
v1 = "Terbukti" if all(pt_ok) and all(p < ALPHA for _, p in comp.values()) else ("Tidak terbukti" if not any(pt_ok) else "Sebagian")
H.append((1, "SQL dan Excel muncul di lebih dari 60% lowongan.", f"SQL {comp['SQL'][0]}/{n}; Excel {comp['Excel'][0]}/{n}", max(p for _, p in comp.values()), v1))
# H2: Jakarta > 50%
cj = int((jobs.city == "Jakarta").sum()); p2 = binomtest(cj, n, 0.5, alternative="greater").pvalue
H.append((2, "Jakarta menyumbang lebih dari separuh lowongan.", f"Jakarta {cj}/{n}", p2, "Terbukti" if cj / n > 0.5 and p2 < ALPHA else ("Sebagian" if cj / n > 0.5 else "Tidak terbukti")))
# H3: salary < 30%
cs_ = int(jobs.salary_min.notna().sum()); p3 = binomtest(cs_, n, 0.3, alternative="less").pvalue
H.append((3, "Kurang dari 30% lowongan mencantumkan salary.", f"Salary tercantum {cs_}/{n}", p3, "Terbukti" if cs_ / n < 0.3 and p3 < ALPHA else ("Sebagian" if cs_ / n < 0.3 else "Tidak terbukti")))
# H4: Python lebih sering di senior dibanding junior
py = has("Python")
sen, jun = jobs[jobs.level == "Senior"].job_id, jobs[jobs.level == "Junior"].job_id
a, b = int(sen.isin(py).sum()), int(jun.isin(py).sum())
rows4 = dict(n_senior=len(sen), n_junior=len(jun), py_senior=a, py_junior=b)
if min(len(sen), len(jun)) < MIN_GROUP:
    H.append((4, "Python lebih sering diminta di level senior dibanding junior.", f"Senior {a}/{len(sen)}, Junior {b}/{len(jun)}; kelompok < {MIN_GROUP} lowongan", float("nan"), "Sebagian"))
else:
    p4 = fisher_exact([[a, len(sen) - a], [b, len(jun) - b]], alternative="greater")[1]
    H.append((4, "Python lebih sering diminta di level senior dibanding junior.", f"Senior {a}/{len(sen)}, Junior {b}/{len(jun)}", p4,
              "Terbukti" if a / len(sen) > b / len(jun) and p4 < ALPHA else ("Sebagian" if a / len(sen) > b / len(jun) else "Tidak terbukti")))
# H5: Power BI > Tableau (uji McNemar eksak, berpasangan pada lowongan yang sama)
pb, tb = has("Power BI"), has("Tableau")
only_p, only_t = len(pb - tb), len(tb - pb)
p5 = binomtest(only_p, only_p + only_t, 0.5, alternative="greater").pvalue if only_p + only_t else 1.0
H.append((5, "Power BI lebih sering diminta dibanding Tableau.", f"Power BI {len(pb)}/{n}, Tableau {len(tb)}/{n}; hanya Power BI {only_p}, hanya Tableau {only_t}", p5,
          "Terbukti" if len(pb) > len(tb) and p5 < ALPHA else ("Sebagian" if len(pb) > len(tb) else "Tidak terbukti")))
hyp = pd.DataFrame(H, columns=["no", "hypothesis", "evidence", "p_value", "verdict"])
hyp.round(8).to_csv(RES_ANALYSIS / "hypotheses.csv", index=False)
pd.DataFrame([rows4]).to_csv(RES_ANALYSIS / "level_counts.csv", index=False)
lc = jobs.level.value_counts().rename_axis("level").reset_index(name="jobs"); lc["with_python"] = lc.level.map(jobs.assign(py=jobs.job_id.isin(py)).groupby("level").py.sum())
lc.to_csv(RES_ANALYSIS / "level_summary.csv", index=False)

# Q14: sensitivitas duplikat. Hitungan skill sebelum (51) dan sesudah (48) membuang deskripsi identik
alln = pd.read_csv(CLEAN_DIR / "job_postings_all.csv", dtype={"job_id": str}); jall = pd.read_csv(CLEAN_DIR / "job_skills_all.csv", dtype={"job_id": str})
sens = []
for s in ("Excel", "SQL", "Power BI", "Tableau", "Python", "Looker Studio"):
    r, c = jall[jall.skill == s].job_id.nunique(), cnt(s)
    sens.append((s, r, len(alln), r / len(alln), c, n, c / n, c / n - r / len(alln)))
pd.DataFrame(sens, columns=["skill", "jobs_raw", "n_raw", "share_raw", "jobs_clean", "n_clean", "share_clean", "diff"]).round(8).to_csv(RES_ANALYSIS / "duplicate_sensitivity.csv", index=False)
dups = alln[alln.is_duplicate][["job_id", "title_norm", "company", "posted_date"]]
dups.to_csv(RES_ANALYSIS / "duplicates_removed.csv", index=False)
print(hyp.to_string(index=False)); print(pd.DataFrame(sens).to_string(index=False)); print(rows4)
