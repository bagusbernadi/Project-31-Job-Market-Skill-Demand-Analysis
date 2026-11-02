"""Langkah 5 (bagian 1): ambil skill dari job description dengan kamus (data/reference/skills.csv). Aturan sama untuk semua batch."""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import CLEAN_DIR, SKILLS_CSV  # noqa: E402


def extract(df, skills):
    """Kembalikan DataFrame (job_id, skill, match_type). match_type: 'kata kunci' bila kata utama cocok, 'sinonim' bila hanya sinonim."""
    out = []
    for r in df.itertuples():
        raw, low = str(r.description), str(r.description).lower()
        for s in skills.itertuples():
            txt, flag = (raw, 0) if s.case_sensitive == 1 else (low, 0)
            if re.search(s.keyword_regex, txt, flag):
                out.append((r.job_id, s.skill, "kata kunci"))
            elif isinstance(s.synonym_regex, str) and re.search(s.synonym_regex, txt, flag):
                out.append((r.job_id, s.skill, "sinonim"))
    return pd.DataFrame(out, columns=["job_id", "skill", "match_type"])


if __name__ == "__main__":
    jobs = pd.read_csv(CLEAN_DIR / "job_postings_all.csv", dtype={"job_id": str})
    skills = pd.read_csv(SKILLS_CSV)
    js = extract(jobs, skills)                                   # semua lowongan (termasuk duplikat), untuk uji sensitivitas Q14
    js.to_csv(CLEAN_DIR / "job_skills_all.csv", index=False)
    keep = set(jobs.loc[~jobs.is_duplicate, "job_id"])
    js[js.job_id.isin(keep)].to_csv(CLEAN_DIR / "job_skills.csv", index=False)
    print(f"{len(js[js.job_id.isin(keep)])} baris job_skills untuk {len(keep)} lowongan; {js.skill.nunique()} skill ditemukan")
