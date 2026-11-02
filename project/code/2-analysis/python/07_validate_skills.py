"""Langkah 6: validasi skill extraction. Bandingkan hasil kamus dengan label sampel (data/reference/skill_labels_sample.csv).
Label dibuat oleh Claude (bukan manusia) dari 3.000 karakter pertama deskripsi, tanpa melihat keluaran kamus. Kamus tidak diubah setelah evaluasi."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "1-data-preparation" / "python"))
from common import CLEAN_DIR, LABELS_CSV, RES_ANALYSIS, SAMPLE_N, SEED, SKILLS_CSV  # noqa: E402

CUT = 3000
mod = __import__("03_extract_skills")
jobs = pd.read_csv(CLEAN_DIR / "job_postings.csv", dtype={"job_id": str})
lab = pd.read_csv(LABELS_CSV, dtype={"job_id": str}).set_index("job_id")
assert set(lab.index) == set(jobs.sample(SAMPLE_N, random_state=SEED).job_id), "label tidak sama dengan sampel acak"
skills = pd.read_csv(SKILLS_CSV)
sub = jobs[jobs.job_id.isin(lab.index)].copy()
sub["description"] = sub.description.str[:CUT]
pred = mod.extract(sub, skills)
pm = pd.crosstab(pred.job_id, pred.skill).reindex(index=lab.index, columns=lab.columns, fill_value=0).clip(upper=1)
tp, fp, fn = (pm & lab).sum(), (pm & (1 - lab)).sum(), ((1 - pm) & lab).sum()
ev = pd.DataFrame(dict(skill=lab.columns, labeled=lab.sum().values, extracted=pm.sum().values, tp=tp.values, fp=fp.values, fn=fn.values))
ev["precision"] = (ev.tp / (ev.tp + ev.fp)).where(ev.tp + ev.fp > 0)
ev["recall"] = (ev.tp / (ev.tp + ev.fn)).where(ev.tp + ev.fn > 0)
tot = dict(skill="SEMUA (micro)", labeled=ev.labeled.sum(), extracted=ev.extracted.sum(), tp=ev.tp.sum(), fp=ev.fp.sum(), fn=ev.fn.sum())
tot["precision"], tot["recall"] = tot["tp"] / (tot["tp"] + tot["fp"]), tot["tp"] / (tot["tp"] + tot["fn"])
pd.concat([ev, pd.DataFrame([tot])]).round(6).to_csv(RES_ANALYSIS / "skill_eval.csv", index=False)
err = []
for j in lab.index:
    for s in lab.columns:
        if pm.loc[j, s] != lab.loc[j, s]:
            err.append((j, s, "FP (kamus menemukan, label tidak)" if pm.loc[j, s] else "FN (label ada, kamus tidak menemukan)"))
pd.DataFrame(err, columns=["job_id", "skill", "type"]).to_csv(RES_ANALYSIS / "skill_eval_errors.csv", index=False)
print(pd.concat([ev, pd.DataFrame([tot])]).round(3).to_string(index=False)); print(pd.DataFrame(err, columns=["job_id", "skill", "type"]).to_string(index=False))
