"""Langkah 11 (data dashboard): atribut turunan per lowongan tanpa job_id, judul, perusahaan, atau teks. Dipakai Streamlit dan notebook."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import CLEAN_DIR, RES_PRESENT, SKILLS_CSV  # noqa: E402

jobs = pd.read_csv(CLEAN_DIR / "job_postings.csv", dtype={"job_id": str})
js = pd.read_csv(CLEAN_DIR / "job_skills.csv", dtype={"job_id": str})
flags = pd.crosstab(js.job_id, js.skill).reindex(index=jobs.job_id, columns=pd.read_csv(SKILLS_CSV).skill, fill_value=0).clip(upper=1).reset_index(drop=True)
d = pd.concat([jobs[["week_start", "city", "level", "industry", "work_type", "salary_min", "salary_max", "remote_hybrid"]].reset_index(drop=True), flags], axis=1)
d = d.sort_values(["week_start", "city", "industry"]).reset_index(drop=True)
d.to_csv(RES_PRESENT / "dash_rows.csv", index=False)
print(d.shape, "kolom skill:", list(flags.columns))
