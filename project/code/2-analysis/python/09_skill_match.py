"""Langkah 9: skill match (Q12). Skill dianggap dimiliki: data/reference/my_skills.csv (asumsi, bisa diganti). Hasil berlabel estimated."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CLEAN_DIR, MY_SKILLS_CSV, NON_TOOL, RES_ANALYSIS  # noqa: E402
from kpi_pandas import load  # noqa: E402

jobs, js = load(CLEAN_DIR)
req = js[~js.skill.isin(NON_TOOL)].groupby("job_id").skill.apply(set).reindex(jobs.job_id).apply(lambda x: x if isinstance(x, set) else set())
n = len(req)
owned = set(pd.read_csv(MY_SKILLS_CSV).skill)
missing = req.apply(lambda r: len(r - owned))
rows = [(k, int((missing <= k).sum()), n, (missing <= k).mean()) for k in (0, 1, 2)]
pd.DataFrame(rows, columns=["boleh_kurang", "bisa_dilamar", "total", "share"]).round(8).to_csv(RES_ANALYSIS / "skill_match.csv", index=False)
# skill berikutnya yang paling menambah peluang (k = 0)
base = int((missing == 0).sum())
nxt = []
for s in sorted(set(js.skill) - owned - NON_TOOL):
    gain = int(req.apply(lambda r: len(r - owned - {s}) == 0).sum()) - base
    nxt.append((s, gain, gain / n, (base + gain) / n))
pd.DataFrame(nxt, columns=["skill", "tambahan_lowongan", "tambahan_share", "share_setelah"]).sort_values(["tambahan_lowongan", "skill"], ascending=[False, True]).round(8).to_csv(RES_ANALYSIS / "skill_next.csv", index=False)
# skenario kumpulan skill
sc = []
for name, S in (("Excel", {"Excel"}), ("Excel + SQL", {"Excel", "SQL"}), ("Excel + SQL + Python", {"Excel", "SQL", "Python"}), ("Excel + SQL + Python + Power BI", {"Excel", "SQL", "Python", "Power BI"})):
    m = req.apply(lambda r: len(r - S))
    sc.append((name, int((m == 0).sum()), n, (m == 0).mean()))
pd.DataFrame(sc, columns=["skenario", "bisa_dilamar", "total", "share"]).round(8).to_csv(RES_ANALYSIS / "skill_match_scenarios.csv", index=False)
print(pd.read_csv(RES_ANALYSIS / "skill_match.csv").to_string(index=False)); print(pd.read_csv(RES_ANALYSIS / "skill_next.csv").head(6).to_string(index=False)); print(pd.read_csv(RES_ANALYSIS / "skill_match_scenarios.csv").to_string(index=False)); print("lowongan tanpa skill tool tertulis:", int((req.apply(len) == 0).sum()))
