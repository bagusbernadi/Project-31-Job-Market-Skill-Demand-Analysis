"""Membuat dan menjalankan results/3-presentation/analysis.ipynb (Q1 sampai Q14) dari CSV hasil. Notebook dieksekusi tanpa error sebelum disimpan."""
import sys
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import RES_PRESENT, ROOT  # noqa: E402

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [md("# Project 31: Job Market Skill Demand (Q1 sampai Q14)\nSemua angka dibaca dari CSV di `project/results/`. Data: 48 lowongan unik Jobstreet, satu kali ambil (Oktober 2026). Sampel kecil."),
         code("import pandas as pd, matplotlib.pyplot as plt\nfrom pathlib import Path\nR = Path('..') / '2-analysis'\nP = Path('..') / '1-data-preparation'\nrd = lambda p, n: pd.read_csv(p / n)\npd.options.display.float_format = '{:,.3f}'.format"),
         md("## Data dan cleaning (Q14)"), code("display(rd(P, 'data_quality_summary.csv'), rd(P, 'cleaning_log.csv')[['rule','description','rows_found']], rd(R, 'duplicate_sensitivity.csv'))"),
         md("## Q1, Q2 Skill dan kombinasinya"), code("s = rd(R, 'skill_share.csv'); ci = rd(R, 'share_ci.csv')\ndisplay(s.merge(ci[['item','ci_low','ci_high']], left_on='skill', right_on='item', how='left').drop(columns='item'))\ns.sort_values('share').plot.barh(x='skill', y='share', legend=False, figsize=(6,5)); plt.xlabel('Porsi lowongan'); plt.show()\ndisplay(rd(R, 'skill_cooc.csv').head(10))"),
         md("## Q3 Level"), code("display(rd(R, 'level_summary.csv'), rd(R, 'skill_by_level.csv'))"),
         md("## Q4, Q5, Q6 Salary dan cakupan"), code("display(rd(R, 'salary_by_skill.csv'), rd(R, 'salary_coverage.csv'))"),
         md("## Q5, Q7, Q8 Kota dan bidang kerja (pengganti industri)"), code("display(rd(R, 'city_summary.csv'), rd(R, 'industry_summary.csv'))"),
         md("## Q9 Remote atau hybrid"), code("display(rd(R, 'remote_share.csv'))"),
         md("## Q10, Q11 Tren (belum bisa dijawab: satu kali ambil, tidak ada data lama)"), code("display(rd(R, 'weekly_jobs.csv'), rd(R, 'old_study_compare.csv'))"),
         md("## Q12 Skill match (estimated)"), code("display(rd(R, 'skill_match.csv'), rd(R, 'skill_match_scenarios.csv'), rd(R, 'skill_next.csv'))"),
         md("## Q13 Validasi skill extraction"), code("display(rd(R, 'skill_eval.csv'), rd(R, 'skill_eval_errors.csv'))"),
         md("## Hipotesis Design"), code("display(rd(R, 'hypotheses.csv'))")]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
out = RES_PRESENT / "analysis.ipynb"
NotebookClient(nb, timeout=120, resources={"metadata": {"path": str(RES_PRESENT)}}).execute()
for c in nb.cells:                      # buang metadata waktu agar hasil stabil antar-jalan
    c.get("metadata", {}).pop("execution", None)
nbf.write(nb, out)
print("notebook ok:", out.relative_to(ROOT), len(nb.cells), "sel")
