"""Membuat design-and-report/index.html (Report Project versi 2) dari page_v1.html dan CSV hasil.

- Pane Design diambil apa adanya dari page_v1.html (dicek identik).
- Semua angka di Report berasal dari project/results/*.csv lewat helper I/D/P (report_lib.py) dan diaudit di akhir.
Jalankan dari mana saja:  python design-and-report/src/build_report.py
"""
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "project" / "code"))
sys.path.insert(0, str(HERE))
from common import DB_PATH, RES_ANALYSIS, RES_PREP, RES_PRESENT, SAMPLE_N, SCRAPED_AT, result  # noqa: E402
from report_lib import (BLUE, D, GREY, HI, I, NO, OK, P, PART, SOFT, audit, bars, cs, esc, hbars, legend, pill, qa, table)  # noqa: E402

R = lambda n: pd.read_csv(result(n))
PRIO = {1: "Utama", 2: "Pendukung", 3: "Pendukung", 4: "Utama", 5: "Utama", 6: "Utama", 7: "Utama", 8: "Utama", 9: "Tambahan", 10: "Utama", 11: "Pendukung", 12: "Utama",
        13: "Utama", 14: "Pendukung"}
QT = {1: "Skill apa yang paling sering diminta di lowongan Data Analyst?",
      2: "Kombinasi skill apa yang paling sering muncul bersamaan?",
      3: "Apakah skill yang diminta berbeda untuk level junior dan senior?",
      4: "Berapa kisaran salary untuk lowongan yang meminta skill tertentu?",
      5: "Berapa kisaran salary di tiap kota dan industri?",
      6: "Berapa persen lowongan yang mencantumkan salary, dan seberapa bias angka salary karenanya?",
      7: "Kota mana yang paling banyak membuka lowongan Data Analyst?",
      8: "Industri mana yang paling banyak mencari Data Analyst?",
      9: "Berapa persen lowongan yang menawarkan kerja remote atau hybrid?",
      10: "Bagaimana tren jumlah lowongan dan permintaan skill dari minggu ke minggu?",
      11: "Skill mana yang naik atau turun dibanding data 2.560 postingan dari project lama?",
      12: "Berapa persen lowongan yang bisa dilamar dengan skill yang dimiliki saat ini, dan skill apa yang paling menambah peluang jika dipelajari?",
      13: "Seberapa akurat pengambilan skill dari job description dibanding label manual?",
      14: "Berapa banyak lowongan yang ganda atau diposting ulang, dan apakah hitungan berubah setelah dibersihkan?"}
WARN = set()      # pertanyaan yang dijawab dengan catatan atau belum bisa dijawab (dipakai chip, ringkasan, dan tabel evaluasi)
NOANS = {10, 11}  # belum bisa dijawab dengan data yang ada


def Q(n, ans, warn=False):
    if warn or n in NOANS:
        WARN.add(n)
    st = "Belum bisa dijawab" if n in NOANS else ("Terjawab dengan catatan" if warn else "Terjawab")
    return qa(f"Q{n}", QT[n], PRIO[n], ans, st, warn or n in NOANS)


mk = lambda *a: "".join(a)
pv = lambda p: "&lt; 0,001" if p < 0.001 else D(p, 3)
MONTH = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "Mei", "06": "Jun", "07": "Jul", "08": "Agu", "09": "Sep", "10": "Okt", "11": "Nov", "12": "Des"}
TGL = lambda s: f"{int(str(s)[8:10])} {MONTH[str(s)[5:7]]}"
jt = lambda x: D(float(x) / 1e6, 2)          # rupiah -> juta

# ---------------------------------------------------------------- data
dl, cl, dqs, ctest, cons, trow = R("download_log.csv"), R("cleaning_log.csv"), R("data_quality_summary.csv").set_index("item").value, R("constraint_tests.csv"), R("consistency_checks.csv"), R("table_rows.csv").set_index("table").rows
ss, ci, cooc, sbl, lsum = R("skill_share.csv"), R("share_ci.csv").set_index("item"), R("skill_cooc.csv"), R("skill_by_level.csv"), R("level_summary.csv").set_index("level")
sbs, scov, ssum, city, ind = R("salary_by_skill.csv"), R("salary_coverage.csv"), R("salary_summary.csv").iloc[0], R("city_summary.csv"), R("industry_summary.csv")
rem, wj, old, sm, smsc, nxt = R("remote_share.csv").iloc[0], R("weekly_jobs.csv"), R("old_study_compare.csv"), R("skill_match.csv"), R("skill_match_scenarios.csv"), R("skill_next.csv")
ev, evr, hyp, dsens, ddup, cx = R("skill_eval.csv"), R("skill_eval_errors.csv"), R("hypotheses.csv").set_index("no"), R("duplicate_sensitivity.csv"), R("duplicates_removed.csv"), R("crosscheck.csv")
dash = pd.read_csv(RES_PRESENT / "dash_rows.csv")
con = duckdb.connect(str(DB_PATH), read_only=True)
sample = con.execute("SELECT posted_date, city, level, industry, salary_min, salary_max, remote_hybrid FROM job_postings ORDER BY posted_date DESC, job_id LIMIT 6").fetchall()
con.close()

n = int(dqs["Lowongan unik dianalisis"])
n_raw, n_dup, n_sal = int(dqs["Lowongan setelah digabung dengan deskripsi"]), int(dqs["Duplikat dibuang"]), int(dqs["Salary tercantum"])
SK = ss.set_index("skill")
top3 = list(ss.skill[:3])
tools = [c for c in dash.columns if c in set(ss.skill) and c != "Dashboard"]
req_n = dash[tools].sum(axis=1)
n_noskill = int((req_n == 0).sum())
evt = ev.iloc[-1]
evs = ev.set_index("skill")
lc = lsum
nj, nsn = int(lc.loc["Junior", "jobs"]), int(lc.loc["Senior", "jobs"])
city_top = city.iloc[0]
jak = city.set_index("city").loc["Jakarta"]
cx_n, cx_ok = len(cx), int((cx.status == "PASS").sum())
excel, sql, pbi, tab, py = (SK.loc[k] for k in ("Excel", "SQL", "Power BI", "Tableau", "Python"))
wk_late = int(wj[wj.week_start >= "2026-09-14"].jobs.sum())
npr = {k: sum(1 for v in PRIO.values() if v == k) for k in ("Utama", "Pendukung", "Tambahan")}
oc = old.status.value_counts()
m0, m1, m2 = sm.set_index("boleh_kurang").loc[0], sm.set_index("boleh_kurang").loc[1], sm.set_index("boleh_kurang").loc[2]
nx1, nx2 = nxt.iloc[0], nxt.iloc[1]
scs = smsc.set_index("skenario")

assert n == 48 and n_raw == 51 and n_sal == 9 and cx_ok == cx_n and (ctest.outcome == "ditolak").all() and (cons.violations == 0).all()
assert (hyp.verdict.tolist() == ["Sebagian", "Terbukti", "Sebagian", "Sebagian", "Sebagian"]), hyp.verdict.tolist()
assert abs(excel.share - 0.625) < 1e-6 and abs(float(rem.share) - 2 / 48) < 1e-6

# ---------------------------------------------------------------- 1. data
kp = lambda c, v, l, d: f'<div class="card kpi" style="--h:var(--{c}H)"><span class="v">{v}</span><span class="l">{l}</span><span class="d">{d}</span></div>'
rp1 = mk(
    '<div class="kpis">',
    kp("navy", I(n), "lowongan unik", f"Dari {I(n_raw)} lowongan mentah; {I(n_dup)} iklan ganda dibuang. Satu kali ambil, versi 1."),
    kp("amber", I(trow["job_skills"]), "baris job_skills", f"Satu baris = satu skill di satu lowongan, dari kamus {I(trow['dim_skill'])} skill."),
    kp("teal", I(n_sal), "lowongan bersalary", f"{P(n_sal / n, 1)} dari {I(n)} lowongan mencantumkan salary per bulan."),
    kp("plum", I(dqs["Perusahaan unik"]), "perusahaan", f"Terbanyak ada di {city_top.city} ({I(city_top.jobs)} lowongan)."),
    kp("rose", I(dqs["Kota/wilayah unik"]), "kota atau wilayah", "Setelah normalisasi lokasi. Industri perusahaan tidak tersedia."),
    kp("sky", I(len(cl)), "aturan cleaning", f"{I(cl.rows_found.sum())} temuan; semuanya ditangani atau dicatat."),
    '</div><h3>1.1 Data mentah</h3>')
rp1 += mk('<div class="callout a"><p><b>Data project ini bukan scraping mingguan.</b> Berkas yang dipakai adalah satu kali ambil (versi 1, tanggal akses ',
          esc(SCRAPED_AT), f') dari arsip DataCenter: {I(n_raw)} lowongan dan {I(dl.rows.iloc[1])} deskripsi. Angka 2.560 postingan pada rancangan tidak ditemukan (lihat 3).</p></div>')
rp1 += '<div class="card"><h4>Cuplikan job_postings (6 lowongan terbaru, tanpa judul dan perusahaan)</h4>' + table(
    ["posted_date", "city", "level", "industry (bidang)", "salary_min", "salary_max", "remote_hybrid"],
    [[str(r[0]), r[1], r[2], r[3], I(r[4]) if pd.notna(r[4]) else "–", I(r[5]) if pd.notna(r[5]) else "–", "ya" if r[6] else "tidak"] for r in sample]) + \
    '<p>Contoh baris tabel bersih. Hasil cleaning sama setiap dijalankan ulang (tidak ada unsur acak).</p></div>'
rp1 += '<div class="card"><h4>Tabel 1.1. Masalah data mentah dan keputusan (Q14)</h4>' + table(
    ["Aturan", "Masalah", "Ditemukan", "Keputusan"], [[r.rule, cs(r.description), I(r.rows_found), cs(r.decision)] for r in cl.itertuples()]) + \
    f'<p>Pembahasan Q14 (duplikat dan pengaruhnya pada hitungan) ada di <a href="#sec28">2.8</a>. Baris mentah: {I(dl.rows.iloc[0])} lowongan dan {I(dl.rows.iloc[1])} deskripsi; bersih: {I(n)} lowongan unik.</p></div>'
rp1 += '<h3>1.2 Tabel di database (<code>jobs.duckdb</code>)</h3><div class="card"><h4>Tabel 1.2a. Isi database</h4>' + table(
    ["Tabel", "Baris", "Isi"],
    [["job_postings_raw", I(trow["job_postings_raw"]), "Lowongan apa adanya (judul, perusahaan, lokasi dan salary teks, deskripsi)."],
     ["job_postings", I(trow["job_postings"]), "Satu lowongan unik yang sudah dibersihkan. Kunci utama job_id."],
     ["job_skills", I(trow["job_skills"]), "Satu skill di satu lowongan, dengan match_type. Kunci asing ke job_postings dan dim_skill."],
     ["dim_skill", I(trow["dim_skill"]), "Kamus skill dan sinonim."]]) + \
    '<h4>Tabel 1.2b. Uji aturan pengecekan (constraint)</h4>' + table(
    ["Baris salah yang dicoba dimasukkan", "Hasil"], [[r.test, OK("Ditolak") if r.outcome == "ditolak" else NO("Diterima")] for r in ctest.itertuples()]) + \
    f'<p>Keenam jenis data salah ditolak database. Setelah dimuat, {I(len(cons))} pemeriksaan konsistensi antar tabel menghasilkan 0 pelanggaran.</p></div>'
FILES = {"download_log": ("Sidik jari dan versi berkas mentah", "Data"), "cleaning_log": ("Log cleaning per aturan", "Q14"), "data_quality_summary": ("Ringkasan kualitas data", "Q6, Q14"),
         "constraint_tests": ("Uji constraint database", "Data"), "consistency_checks": ("Pemeriksaan konsistensi antar tabel", "Data"), "table_rows": ("Jumlah baris per tabel", "Data"),
         "skill_share": ("Porsi lowongan per skill", "Q1"), "share_ci": ("Interval Wilson 95% porsi skill, salary, remote", "Q1, Q6, Q9"), "skill_cooc": ("Pasangan skill yang muncul bersama", "Q2"),
         "skill_by_level": ("Skill per level jabatan", "Q3"), "level_summary": ("Jumlah lowongan per level dan Python", "Q3"), "level_counts": ("Ukuran kelompok senior dan junior (H4)", "Q3"),
         "salary_by_skill": ("Median dan rentang salary per skill", "Q4"), "salary_summary": ("Ringkasan salary seluruh lowongan bersalary", "Q4, Q6"),
         "salary_coverage": ("Cakupan salary per kota, level, tipe kerja", "Q6"), "city_summary": ("Lowongan dan salary per kota", "Q5, Q7"),
         "industry_summary": ("Lowongan dan salary per bidang kerja (pengganti industri)", "Q5, Q8"), "remote_share": ("Porsi lowongan remote atau hybrid", "Q9"),
         "weekly_jobs": ("Lowongan per minggu tayang", "Q10"), "weekly_skill": ("Porsi skill per minggu tayang", "Q10"), "old_study_compare": ("Hasil dibanding studi awal (data sama)", "Q11"),
         "skill_match": ("Skill match dengan toleransi 0, 1, 2 skill", "Q12"), "skill_match_scenarios": ("Skill match per kumpulan skill", "Q12"), "skill_next": ("Skill berikutnya yang paling menambah peluang", "Q12"),
         "skill_eval": ("Precision dan recall skill extraction", "Q13"), "skill_eval_errors": ("Kesalahan skill extraction pada sampel", "Q13"),
         "duplicate_sensitivity": ("Porsi skill sebelum dan sesudah duplikat dibuang", "Q14"), "duplicates_removed": ("Daftar lowongan duplikat yang dibuang", "Q14"),
         "hypotheses": ("Lima hipotesis Design dan hasilnya", "Hipotesis"), "crosscheck": ("SQL vs pandas", "Q14, validasi")}
resfiles = sorted(p for d in (RES_PREP, RES_ANALYSIS) for p in d.glob("*.csv"))
miss = [p.stem for p in resfiles if p.stem not in FILES]
assert not miss, f"CSV hasil belum didokumentasikan di FILES: {miss}"
rp1 += '<div class="card"><h4>Tabel 1.2c. Data hasil analisis (<code>project/results/</code>)</h4>' + table(
    ["File", "Isi", "Baris", "Menjawab"], [[f"<code>{p.stem}.csv</code>", FILES[p.stem][0], I(len(pd.read_csv(p))), FILES[p.stem][1]] for p in resfiles]) + \
    f'<p>{I(len(resfiles))} file CSV, ditambah {I(len(list(RES_PRESENT.glob("dash_*.csv"))))} CSV data dashboard.</p></div>'
rp1 += '<h3>1.3 Angka kunci (KPI)</h3><div class="card"><h4>Tabel 1.3. Lima KPI (definisi di <code>project/docs/definitions.md</code>)</h4>' + table(
    ["KPI", "Rumus ringkas", "Hasil", "Jumlah data"],
    [["Skill share", "lowongan yang menyebut skill ÷ lowongan unik", f"{top3[0]} {P(SK.loc[top3[0]].share)}, {top3[1]} {P(SK.loc[top3[1]].share)}, {top3[2]} {P(SK.loc[top3[2]].share)}", f"{I(n)} lowongan"],
     ["Median salary", "median salary_min dan salary_max per bulan", f"Rp {jt(ssum.median_min)} sampai {jt(ssum.median_max)} juta", f"{I(ssum.n_salary)} lowongan bersalary"],
     ["Cakupan salary", "lowongan bersalary ÷ lowongan unik", P(n_sal / n), f"{I(n_sal)} dari {I(n)}"],
     ["Skill match (estimated)", "lowongan dengan semua skill tool dimiliki ÷ lowongan unik", f"{P(m0.share)} (Excel, SQL, Python)", f"{I(m0.bisa_dilamar)} dari {I(n)}"],
     ["Volume mingguan", "lowongan baru per minggu scraping", "Belum bisa dihitung (satu kali ambil)", f"{I(len(wj))} minggu tayang, bukan minggu scraping"]]) + \
    f'<p>Salary hanya mewakili {I(n_sal)} lowongan yang mencantumkannya, jadi angka median bersifat kasar.</p></div>'

# ---------------------------------------------------------------- 2. business questions
cityhi = {c: (BLUE if c == "Jakarta" else GREY) for c in city.city}
s21 = mk('<h3 id="sec21">2.1 Skill yang diminta <span class="qlist">Q1, Q2</span></h3><div class="card">',
         Q(1, f"Teratas: {top3[0]} ({P(SK.loc[top3[0]].share)}, {I(SK.loc[top3[0]].jobs)} dari {I(n)} lowongan), {top3[1]} ({P(SK.loc[top3[1]].share)}) yang berupa konsep, lalu SQL ({P(sql.share)}), "
              f"Power BI ({P(pbi.share)}), Tableau ({P(tab.share)}), dan Python ({P(py.share)}). Interval kepercayaan lebar karena sampel kecil: Excel {P(ci.loc['Excel'].ci_low)} sampai {P(ci.loc['Excel'].ci_high)} (Tabel 2.1b)."),
         Q(2, f"Pasangan terbanyak: {cooc.skill_a[0]} dan {cooc.skill_b[0]} ({I(cooc.jobs[0])} lowongan), {cooc.skill_a[1]} dan {cooc.skill_b[1]} ({I(cooc.jobs[1])}), serta {cooc.skill_a[2]} dan {cooc.skill_b[2]} ({I(cooc.jobs[2])}). "
              f"Tiga pasangan itu masing-masing muncul pada sekitar sepertiga lowongan ({P(cooc.jobs[0] / n, 0)})."),
         '<h4>Grafik 2.1a. Porsi lowongan yang menyebut tiap skill</h4>',
         hbars([(r.skill, r.share, BLUE if r.skill in tools else SOFT, f"{r.skill}: {I(r.jobs)} dari {I(n)} lowongan ({P(r.share)})") for r in ss.itertuples() if r.jobs > 0], lambda v: P(v, 1), "Porsi skill", 0.8),
         legend([(BLUE, "Skill atau tool"), (SOFT, "Konsep (Dashboard)")]),
         '<h4>Tabel 2.1b. Porsi skill dengan interval Wilson 95%</h4>',
         table(["Skill", "Kategori", "Lowongan", "Porsi", "CI 95%"],
               [[r.skill, r.category, I(r.jobs), P(r.share), f"{P(ci.loc[r.skill].ci_low)} s.d. {P(ci.loc[r.skill].ci_high)}"] for r in ss.itertuples() if r.jobs > 0]),
         '<h4>Tabel 2.1c. Sepuluh pasangan skill teratas (tanpa Dashboard)</h4>',
         table(["Skill A", "Skill B", "Lowongan", "Porsi"], [[r.skill_a, r.skill_b, I(r.jobs), P(r.jobs / n)] for r in cooc.head(10).itertuples()]),
         '<p>Satu lowongan dihitung satu kali per skill. "Spreadsheet" dihitung sebagai Excel; "MS Office" tidak. Hasil sama dengan studi awal (lihat 2.6).</p></div>')
sb = sbl.set_index(["level", "skill"])
s22 = mk('<h3 id="sec22">2.2 Level jabatan <span class="qlist">Q3</span></h3><div class="card">',
         Q(3, f"Belum bisa dijawab dengan tegas. Level hanya bisa dibaca dari judul: {I(nsn)} lowongan Senior, {I(nj)} Junior, dan {I(lc.loc['Tidak disebut', 'jobs'])} tidak menyebut level. "
              f"Senior meminta Power BI, SQL, dan Tableau masing-masing {P(sb.loc[('Senior', 'SQL')].share, 0)}, Excel dan Python {P(sb.loc[('Senior', 'Excel')].share, 0)}; yang tidak menyebut level lebih banyak meminta Excel "
              f"({P(sb.loc[('Tidak disebut', 'Excel')].share, 0)}). Hanya {I(nj)} lowongan junior, sehingga perbandingan junior dan senior tidak bisa dibuat. Definisi level adalah asumsi sendiri (Tabel 2.2a).", warn=True),
         '<h4>Tabel 2.2a. Porsi lima skill per level (dari judul)</h4>',
         table(["Level", "Lowongan", "Excel", "SQL", "Python", "Power BI", "Tableau"],
               [[lv, I(lc.loc[lv, "jobs"])] + [(P(sb.loc[(lv, s)].share, 0) if (lv, s) in sb.index else "0%") for s in ("Excel", "SQL", "Python", "Power BI", "Tableau")] for lv in ("Senior", "Tidak disebut", "Junior")]),
         '<p>Senior = judul memuat senior, sr, head, lead, supervisor, manager, atau principal. Junior = junior, jr, fresh, intern, trainee, entry. Kelompok di bawah 5 lowongan tidak dibandingkan (Q3 dan hipotesis 4).</p></div>')
sbs3 = sbs[sbs.n_salary >= 1]
s23 = mk('<h3 id="sec23">2.3 Salary dan cakupannya <span class="qlist">Q4, Q6</span></h3><div class="card">',
         Q(4, f"Median salary seluruh {I(ssum.n_salary)} lowongan bersalary: batas bawah Rp {jt(ssum.median_min)} juta dan batas atas Rp {jt(ssum.median_max)} juta per bulan (rentang Rp {jt(ssum.lowest_min)} sampai {jt(ssum.highest_max)} juta). "
              f"Per skill, Excel punya {I(sbs.set_index('skill').loc['Excel'].n_salary)} lowongan bersalary (median Rp {jt(sbs.set_index('skill').loc['Excel'].median_min)} sampai {jt(sbs.set_index('skill').loc['Excel'].median_max)} juta), "
              f"SQL dan Power BI masing-masing {I(sbs.set_index('skill').loc['SQL'].n_salary)}. Skill lain hanya 1 sampai 3 lowongan, sehingga perbedaan antar skill tidak bisa disimpulkan.", warn=True),
         Q(6, f"Hanya {I(n_sal)} dari {I(n)} lowongan ({P(n_sal / n)}) mencantumkan salary, CI 95% {P(ci.loc['(cakupan salary)'].ci_low)} sampai {P(ci.loc['(cakupan salary)'].ci_high)}. Cakupan paling rendah di Jakarta "
              f"({I(scov.set_index('val').loc['Jakarta'].with_salary)} dari {I(jak.jobs)}, {P(scov.set_index('val').loc['Jakarta'].coverage)}) dan level Senior ({I(scov.set_index('val').loc['Senior'].with_salary)} dari {I(nsn)}). "
              f"Angka salary karenanya condong ke lowongan yang mau mencantumkannya, dan arah bias tidak bisa dipastikan."),
         '<h4>Tabel 2.3a. Salary per skill (hanya lowongan bersalary)</h4>',
         table(["Skill", "Lowongan bersalary", "Median min (Rp juta)", "Median maks (Rp juta)", "Terendah (Rp juta)", "Tertinggi (Rp juta)"],
               [[r.skill, I(r.n_salary), jt(r.median_min), jt(r.median_max), jt(r.lowest_min), jt(r.highest_max)] for r in sbs3.itertuples()]),
         '<h4>Tabel 2.3b. Cakupan salary per kota, level, dan tipe kerja</h4>',
         table(["Kelompok", "Nilai", "Lowongan", "Bersalary", "Cakupan"], [[r.dimension, r.val, I(r.jobs), I(r.with_salary), P(r.coverage, 0)] for r in scov.itertuples()]),
         '<p>Median dihitung dari salary per bulan (Rp), ditampilkan dalam juta. Salary dengan satuan lain tidak ditemukan pada data.</p></div>')
indn = ind.head(6)
s24 = mk('<h3 id="sec24">2.4 Kota dan industri <span class="qlist">Q5, Q7, Q8</span></h3><div class="card">',
         Q(5, f"Median salary per kota hanya bisa dihitung untuk kota dengan salary: Jakarta Rp {jt(jak.median_min)} sampai {jt(jak.median_max)} juta ({I(jak.n_salary)} lowongan), Surabaya Rp {jt(city.set_index('city').loc['Surabaya'].median_min)} "
              f"sampai {jt(city.set_index('city').loc['Surabaya'].median_max)} juta ({I(city.set_index('city').loc['Surabaya'].n_salary)} lowongan). Jobstreet tidak memberi industri perusahaan, jadi bidang kerja dipakai sebagai pengganti "
              f"(Tabel 2.4c). Tiap kelompok hanya 0 sampai {I(city.n_salary.max())} lowongan bersalary, jadi angkanya tidak bisa dibandingkan antar kota atau bidang.", warn=True),
         Q(7, f"{city_top.city} paling banyak: {I(city_top.jobs)} dari {I(n)} lowongan ({P(city_top.share)}), disusul {city.city[1]} ({I(city.jobs[1])}) dan {city.city[2]} ({I(city.jobs[2])}). Kecamatan di Jakarta digabung ke Jakarta."),
         Q(8, f"Berdasarkan bidang kerja Jobstreet (bukan industri perusahaan): {ind.industry[0]} ({I(ind.jobs[0])} lowongan, {P(ind.share[0])}) dan {ind.industry[1]} ({I(ind.jobs[1])}, {P(ind.share[1])}) paling banyak. "
              f"Jumlah ini menggambarkan jenis pekerjaan, bukan sektor bisnis perusahaan.", warn=True),
         '<h4>Grafik 2.4a. Lowongan per kota</h4>',
         hbars([(r.city, r.jobs, cityhi[r.city], f"{r.city}: {I(r.jobs)} lowongan ({P(r.share)}), {I(r.n_salary)} bersalary") for r in city.itertuples()], lambda v: I(v), "Lowongan per kota", 36),
         '<h4>Tabel 2.4b. Kota: lowongan dan salary</h4>',
         table(["Kota", "Lowongan", "Porsi", "Bersalary", "Median min (Rp juta)", "Median maks (Rp juta)"],
               [[r.city, I(r.jobs), P(r.share), I(r.n_salary), jt(r.median_min) if pd.notna(r.median_min) else "–", jt(r.median_max) if pd.notna(r.median_max) else "–"] for r in city.itertuples()]),
         '<h4>Tabel 2.4c. Enam bidang kerja Jobstreet terbanyak (pengganti industri)</h4>',
         table(["Bidang kerja", "Lowongan", "Porsi", "Bersalary", "Median min (Rp juta)", "Median maks (Rp juta)"],
               [[r.industry, I(r.jobs), P(r.share), I(r.n_salary), jt(r.median_min) if pd.notna(r.median_min) else "–", jt(r.median_max) if pd.notna(r.median_max) else "–"] for r in indn.itertuples()]),
         f'<p>Total {I(len(ind))} bidang kerja; sembilan di antaranya hanya 1 sampai 3 lowongan.</p></div>')
s25 = mk('<h3 id="sec25">2.5 Remote dan hybrid <span class="qlist">Q9</span></h3><div class="card">',
         Q(9, f"{I(rem.remote_hybrid_jobs)} dari {I(rem.jobs)} lowongan ({P(rem.share)}; CI 95% {P(ci.loc['(remote atau hybrid)'].ci_low)} sampai {P(ci.loc['(remote atau hybrid)'].ci_high)}) menyebut remote, hybrid, atau WFH di judul atau deskripsi. "
              f"Kejadiannya sangat sedikit, dan satu kata kunci bisa muncul dalam kalimat larangan (mis. remote tidak tersedia), sehingga angka ini hanya perkiraan kasar.", warn=True), '</div>')
s26 = mk('<h3 id="sec26">2.6 Tren mingguan dan perbandingan data lama <span class="qlist">Q10, Q11</span></h3><div class="card">',
         Q(10, f"Belum bisa dijawab. Data hanya satu kali ambil, jadi tidak ada minggu scraping yang bisa dibandingkan. Yang tersedia adalah tanggal tayang: {I(wk_late)} dari {I(n)} lowongan tayang sejak minggu {TGL('2026-09-14')}, "
              f"sebelumnya hanya {I(n - wk_late)}. Pola itu terjadi karena lowongan lama sudah ditutup sebelum scraping, bukan karena permintaan naik. Tren skill per minggu tayang juga tidak dihitung karena tiap minggu hanya 1 sampai {I(wj.jobs.max())} lowongan."),
         Q(11, f"Belum bisa dijawab. Data 2.560 postingan project lama tidak ditemukan di repo lama maupun DataCenter. Satu-satunya pembanding adalah hasil studi awal, yang memakai 48 lowongan yang sama: "
               f"{I(oc.get('Sama', 0))} dari {I(oc.get('Sama', 0) + oc.get('Beda', 0))} skill yang ada di kamus menghasilkan jumlah identik (Tabel 2.6b), sehingga tidak ada skill yang naik atau turun."),
         '<h4>Grafik 2.6a. Lowongan per minggu tayang (bukan minggu scraping)</h4>',
         bars([(TGL(r.week_start), r.jobs, BLUE, f"Minggu {r.week_start}: {I(r.jobs)} lowongan") for r in wj.itertuples()], lambda v: I(v), "Lowongan per minggu tayang", rot=0, small=True),
         '<h4>Tabel 2.6b. Hasil project ini vs studi awal (data sama)</h4>',
         table(["Skill (studi awal)", "Lowongan studi awal", "Lowongan project ini", "Status"],
               [[r.old_skill, I(r.old_jobs), I(r.new_jobs) if pd.notna(r.new_jobs) else "–", OK("Sama") if r.status == "Sama" else (NO(r.status) if r.status == "Beda" else PART(r.status))] for r in old.itertuples()]),
         f'<p>{I(oc.get("Tidak ada di kamus baru", 0))} butir studi awal (keterampilan lunak dan Pandas/Numpy) tidak ada di kamus baru. Pandas dan NumPy menjadi sinonim Python. Perubahan minggu ke minggu (window function) ada di <code>weekly_skill.csv</code>.</p></div>')
s27 = mk('<h3 id="sec27">2.7 Skill match <span class="qlist">Q12</span></h3><div class="card">',
         Q(12, f"Dengan skill yang dianggap dimiliki (Excel, SQL, Python; asumsi), {I(m0.bisa_dilamar)} dari {I(n)} lowongan ({P(m0.share)}) bisa dilamar tanpa kekurangan skill, {I(m1.bisa_dilamar)} ({P(m1.share)}) bila boleh kurang 1 skill, "
               f"dan {I(m2.bisa_dilamar)} ({P(m2.share)}) bila boleh kurang 2. Skill berikutnya yang paling menambah peluang: {nx1.skill} dan {nx2.skill}, masing-masing menambah {I(nx1.tambahan_lowongan)} lowongan "
               f"(menjadi {P(nx1.share_setelah)}). Angka ini estimated; {I(n_noskill)} lowongan tidak menyebut skill tool sama sekali dan dihitung bisa dilamar.", warn=True),
         '<h4>Tabel 2.7a. Skill match menurut kumpulan skill dimiliki (estimated, tanpa toleransi)</h4>',
         table(["Skill dimiliki", "Lowongan bisa dilamar", "Porsi"], [[r.Index, I(r.bisa_dilamar), P(r.share)] for r in scs.itertuples()]),
         '<h4>Tabel 2.7b. Toleransi kekurangan skill (Excel, SQL, Python)</h4>',
         table(["Boleh kurang", "Lowongan bisa dilamar", "Porsi"], [[f"{I(r.boleh_kurang)} skill", I(r.bisa_dilamar), P(r.share)] for r in sm.itertuples()]),
         '<h4>Tabel 2.7c. Skill berikutnya yang paling menambah peluang (tanpa toleransi)</h4>',
         table(["Skill", "Tambahan lowongan", "Porsi setelah ditambah"], [[r.skill, I(r.tambahan_lowongan), P(r.share_setelah)] for r in nxt.head(5).itertuples()]),
         '<p>Skill dimiliki ada di <code>project/data/reference/my_skills.csv</code> dan bisa diganti. Dashboard sebagai konsep tidak dihitung. Syarat "wajib" atau "nilai tambah" tidak dibedakan, jadi angkanya cenderung terlalu rendah.</p></div>')
e2 = evs
s28 = mk('<h3 id="sec28">2.8 Validasi skill extraction dan duplikat <span class="qlist">Q13, Q14</span></h3><div class="card">',
         Q(13, f"Pada {I(SAMPLE_N)} lowongan sampel (bukan 100 seperti rancangan; hanya ada {I(n)} lowongan unik), kamus menemukan {I(evt.tp)} dari {I(evt.labeled)} skill berlabel: precision {P(evt.precision)} dan recall {P(evt.recall)}. "
               f"Dua skill terlewat: {evr.skill[0]} ('konsep statistik dasar' tidak ada di sinonim) dan {evr.skill[1]} (hanya ditulis 'AI/ML'). Label dibuat oleh Claude, bukan manusia, dan kamus tidak diubah setelah evaluasi.", warn=True),
         Q(14, f"{I(n_dup)} dari {I(n_raw)} lowongan adalah iklan ganda (deskripsi identik) dan dibuang. Hitungan berubah kecil: Excel {P(dsens.set_index('skill').loc['Excel'].share_raw)} menjadi {P(dsens.set_index('skill').loc['Excel'].share_clean)}, "
               f"SQL {P(dsens.set_index('skill').loc['SQL'].share_raw)} menjadi {P(dsens.set_index('skill').loc['SQL'].share_clean)}; selisih terbesar {D(dsens['diff'].abs().max() * 100, 1)} poin dan urutan skill teratas tidak berubah. "
               f"Pasangan judul dan perusahaan yang sama dengan deskripsi berbeda: {I(cl.set_index('rule').loc['C9'].rows_found)}."),
         '<h4>Tabel 2.8a. Precision dan recall per skill (sampel berlabel)</h4>',
         table(["Skill", "Berlabel", "Ditemukan kamus", "Benar", "Salah", "Terlewat", "Precision", "Recall"],
               [[r.skill, I(r.labeled), I(r.extracted), I(r.tp), I(r.fp), I(r.fn), P(r.precision, 0) if pd.notna(r.precision) else "–", P(r.recall, 0) if pd.notna(r.recall) else "–"] for r in ev.itertuples()]),
         '<h4>Tabel 2.8b. Hitungan skill sebelum dan sesudah duplikat dibuang</h4>',
         table(["Skill", "Lowongan (51)", "Porsi", "Lowongan (48)", "Porsi", "Selisih (poin)"],
               [[r.skill, I(r.jobs_raw), P(r.share_raw), I(r.jobs_clean), P(r.share_clean), D(r.diff * 100, 1)] for r in dsens.itertuples()]),
         f'<p>Teks sampel dipotong 3.000 karakter pertama. Cek silang SQL vs pandas: {I(cx_ok)} dari {I(cx_n)} pemeriksaan PASS. Kamus awal tidak disetel ulang pada sampel yang sama, supaya angka tidak terlalu optimistis.</p></div>')
hrows = [[I(i), cs(r.hypothesis), OK(r.verdict) if r.verdict == "Terbukti" else (NO(r.verdict) if r.verdict == "Tidak terbukti" else PART(r.verdict)),
          cs(r.evidence) + ("; p-value " + pv(r.p_value) if pd.notna(r.p_value) else "")] for i, r in hyp.iterrows()]
s29 = mk('<h3 id="sec29">2.9 Hipotesis pada Design Project</h3><div class="card"><h4>Tabel 2.9a. Lima hipotesis dan hasilnya</h4>',
         table(["No", "Hipotesis", "Hasil", "Bukti"], hrows),
         '<p>Aturan verdict: Terbukti bila estimasi titik memenuhi dan uji satu sisi p &lt; 0,05; Sebagian bila estimasi titik memenuhi tetapi p belum di bawah 0,05, hanya sebagian komponen terpenuhi, atau kelompok kurang dari 5 lowongan. '
         'Hipotesis 1 memakai p-value komponen terbesar (SQL).</p></div>')
SEC = {1: "21", 2: "21", 3: "22", 4: "23", 5: "24", 6: "23", 7: "24", 8: "24", 9: "25", 10: "26", 11: "26", 12: "27", 13: "28", 14: "28"}
rp2_body = mk(s21, s22, s23, s24, s25, s26, s27, s28, s29)
qn_uniq = sorted(set(int(x) for x in re.findall(r'<span class="qn">Q(\d+)</span>', rp2_body)))
assert qn_uniq == list(range(1, 15)), qn_uniq
nw = len(WARN)
nnote = len(WARN - NOANS)
chips = mk('<div class="qchips">', "".join(f'<a class="qc{" w" if q in WARN else ""}" href="#sec{SEC[q]}" title="{esc(QT[q])}">Q{q}</a>' for q in range(1, 15)), '</div>')
rp2 = mk(f'<div class="card"><p><b>Jawaban singkat:</b> {I(len(QT) - len(NOANS))} dari {I(len(QT))} pertanyaan terjawab ({npr["Utama"]} Utama, {npr["Pendukung"]} Pendukung, {npr["Tambahan"]} Tambahan), '
         f'{I(nnote)} di antaranya dengan catatan (kuning): {", ".join(f"Q{q}" for q in sorted(WARN - NOANS))}. Q10 dan Q11 belum bisa dijawab karena data hanya satu kali ambil dan data lama tidak ada. '
         'Klik nomor pertanyaan untuk melompat ke pembahasannya. Pertanyaan utama project dijawab di bagian 7.</p>',
         chips, '<p class="report-note">Q hijau = terjawab, Q kuning = terjawab dengan catatan atau belum bisa dijawab. Pembahasan dikelompokkan per grafik atau tabel bukti (2.1 sampai 2.9).</p></div>', rp2_body)

# ---------------------------------------------------------------- 3-5. dataset, tools, alur
npy = len(list((REPO / "project/code").rglob("*.py")))
loc = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in (REPO / "project/code").rglob("*.py"))
nsql = len(list((REPO / "project/code").rglob("*.sql")))
hv = lambda i: OK("Terbukti") if hyp.loc[i].verdict == "Terbukti" else (NO("Tidak terbukti") if hyp.loc[i].verdict == "Tidak terbukti" else PART("Sebagian"))
rp3 = mk(f'<div class="card"><p><b>Jawaban singkat:</b> dataset lebih kecil dari rancangan. Rancangan memakai 2.560 postingan lama ditambah scraping mingguan ±12 minggu; yang tersedia adalah satu kali ambil ({I(n_raw)} lowongan, {I(n)} unik). '
         f'Empat tabel dan kamus skill sesuai rancangan, industri diganti bidang kerja, dan dari lima hipotesis satu terbukti dan empat sebagian. Lisensi data belum diverifikasi.</p></div>',
         table(["Aspek", "Rancangan", "Realisasi", "Verdict"], [
             ["Sumber", "Data 2.560 postingan project lama ditelusuri ulang, lalu scraping mingguan Jobstreet", f"Satu kali ambil dari <code>jobstreet-job-postings.zip</code> di DataCenter (versi 1, tanggal akses {esc(SCRAPED_AT)}); berkas lama 2.560 postingan tidak ditemukan", NO("Berubah")],
             ["Ukuran", "2.560 postingan ditambah ±150 sampai 300 per minggu, ±12 minggu", f"{I(n_raw)} lowongan dan {I(dl.rows.iloc[1])} deskripsi mentah; {I(n)} unik. Periode tayang 25 Mar sampai 16 Okt 2026", NO("Berubah")],
             ["Lisensi dan sitasi", "Tidak ada lisensi terbuka, ketentuan layanan belum dicek", "Belum diverifikasi. Konten milik Jobstreet dan perusahaan; hanya arsip pribadi dan hasil agregat yang dipublikasikan", PART("Sebagian")],
             ["Tabel", "job_postings_raw, job_postings, job_skills, dim_skill", f"Keempatnya ({I(trow['job_postings_raw'])}, {I(trow['job_postings'])}, {I(trow['job_skills'])}, {I(trow['dim_skill'])} baris) dengan constraint dan kunci asing", OK("Sesuai")],
             ["Kolom data mentah", "job_id, scraped_at, title, company, location_raw, salary_raw, description, url", "Sama, ditambah batch_id; url dibuat dari job_id; scraped_at diisi tanggal akses versi (bukan per halaman)", PART("Sesuai + penyesuaian")],
             ["Kolom industry", "Industri perusahaan", "Jobstreet tidak memberi industri; klasifikasi bidang kerja dipakai sebagai pengganti", NO("Berubah")],
             ["Kamus skill", "Usulan 10 skill", f"{I(trow['dim_skill'])} skill (tambahan Google Sheets sudah ada, BigQuery, ETL, VBA/Macro, Dashboard, Machine Learning)", PART("Sesuai + tambahan")],
             ["Hipotesis 1 (SQL dan Excel di atas 60%)", "Kedua skill lebih dari 60%", cs(hyp.loc[1].evidence) + f"; hanya Excel di atas 60%", hv(1)],
             ["Hipotesis 2 (Jakarta lebih dari separuh)", "Lebih dari 50%", cs(hyp.loc[2].evidence) + f" ({P(jak.share)}), p-value {pv(hyp.loc[2].p_value)}", hv(2)],
             ["Hipotesis 3 (salary kurang dari 30%)", "Kurang dari 30%", cs(hyp.loc[3].evidence) + f" ({P(n_sal / n)}), p-value {pv(hyp.loc[3].p_value)}; titik di bawah 30% tetapi belum signifikan", hv(3)],
             ["Hipotesis 4 (Python lebih sering di senior)", "Senior lebih sering dari junior", cs(hyp.loc[4].evidence), hv(4)],
             ["Hipotesis 5 (Power BI lebih sering dari Tableau)", "Power BI lebih sering", cs(hyp.loc[5].evidence) + f", p-value {pv(hyp.loc[5].p_value)}", hv(5)]]))
rp4 = mk('<div class="card"><p><b>Jawaban singkat:</b> Python, regex dengan kamus, DuckDB + SQL, dan Streamlit + Plotly dipakai. Scraper Playwright dan jadwal GitHub Actions ditulis tetapi belum pernah dijalankan; '
         'dashboard diuji lokal dan belum di-deploy. SciPy dan statsmodels ditambahkan untuk uji dan interval kepercayaan.</p></div>',
         table(["Tool", "Rancangan", "Realisasi", "Verdict"], [
             ["Python (Playwright, requests, pandas)", "Scraping dan cleaning", f"pandas dipakai penuh ({I(npy)} skrip dan modul, {I(loc)} baris). Playwright ada di <code>scrape_jobs.py</code> tetapi tidak dijalankan di sesi ini (situs diblokir sandbox). requests tidak dipakai", PART("Sebagian")],
             ["Regex + kamus skill", "Mengambil skill dari deskripsi, tanpa LLM", "<code>skills.csv</code> dan <code>03_extract_skills.py</code>; aturan sama untuk semua batch", OK("Sesuai")],
             ["DuckDB + SQL", "Database, CTE, window function", f"jobs.duckdb 4 tabel; {I(nsql)} file SQL; window function <code>lag</code> dan <code>sum over</code> pada query mingguan", OK("Sesuai")],
             ["GitHub Actions", "Scraping terjadwal tiap minggu", "<code>weekly_scrape.yml</code> ditulis, belum pernah berjalan", PART("Sebagian")],
             ["Streamlit + Plotly", "Dashboard 4 halaman, link publik", "<code>app.py</code> 4 halaman dengan filter minggu, kota, level, bidang; diuji dengan <code>AppTest</code>; belum di-deploy", PART("Sebagian")],
             ["GitHub + Markdown", "Kode, kamus, agregat, README", "Struktur dan README siap; berada di branch <code>project-31-build</code>, belum digabung ke <code>main</code>", PART("Sebagian")],
             ["SciPy + statsmodels", "Tidak ada di rancangan", "Interval Wilson dan uji binomial, Fisher, dan McNemar eksak untuk hipotesis", PART("Tambahan")],
             ["Jupyter", "Notebook analisis (daftar dokumen)", "<code>analysis.ipynb</code> dibuat otomatis dan dieksekusi tanpa error", OK("Sesuai")]]))
steps = [("1", "Reverse engineering project lama", "<code>project/docs/reverse_engineering.md</code>", PART("Sebagian"), "Hanya repo scraper lama yang bisa dibuka; repo Web_scraping_and_Job_Analyze tidak bisa; berkas 2.560 postingan tidak ditemukan."),
         ("2", "Cek aturan situs dan skema", "<code>project/docs/scraping_ethics.md</code>, <code>data_dictionary.md</code>", PART("Sebagian"), "Skema selesai. robots.txt dan ketentuan layanan belum diperiksa (situs diblokir sandbox)."),
         ("3", "Upgrade scraper", "<code>scraper/scrape_jobs.py</code>", PART("Sebagian"), "Skrip ditulis (jeda, coba ulang, robots.txt, log) tetapi tidak dijalankan; data mentah dari DataCenter."),
         ("4", "Cleaning dan normalisasi", "<code>02_clean.py</code>, <code>cleaning_decisions.md</code>", OK("Sesuai"), f"{I(len(cl))} aturan; salary, kota, level, remote, duplikat."),
         ("5", "Skill extraction dan load", "<code>03_extract_skills.py</code>, <code>04_build_db.py</code>, <code>01_schema.sql</code>", OK("Sesuai"), "Ditambah uji constraint dan pemeriksaan konsistensi."),
         ("6", "Validasi skill extraction", "<code>07_validate_skills.py</code>, <code>skill_labels_sample.csv</code>", PART("Sesuai + penyesuaian"), f"{I(SAMPLE_N)} lowongan sampel (bukan 100) dengan label dari Claude, bukan manusia."),
         ("7", "Query SQL analitik", "<code>02_queries.sql</code>, <code>05_run_queries.py</code>, <code>06_crosscheck.py</code>", PART("Sesuai + tambahan"), "Ditambah cek silang pandas dan pembanding studi awal."),
         ("8", "Analisis skill, salary, kota, industri", "<code>05_run_queries.py</code>, <code>08_hypotheses_stats.py</code>", PART("Sesuai + penyesuaian"), "Industri diganti bidang kerja; ditambah interval dan uji hipotesis."),
         ("9", "Skill match", "<code>09_skill_match.py</code>", PART("Sesuai + tambahan"), "Skill dimiliki adalah asumsi (Excel, SQL, Python); ditambah toleransi dan skenario."),
         ("10", "Jadwal mingguan dan tren", "<code>weekly_scrape.yml</code>", NO("Belum dikerjakan"), "Workflow ditulis, belum berjalan. Q10 dan Q11 belum bisa dijawab."),
         ("11", "Membuat dashboard", "<code>streamlit/app.py</code>, <code>10_build_dashboard_data.py</code>", PART("Sebagian"), "Belum di-deploy; filter minggu memakai minggu tayang."),
         ("12", "README dan finalisasi", "<code>README.md</code>, halaman ini", PART("Sebagian"), "Siap; digabung ke main setelah ditinjau.")]
CODE_REL = "project/code/"
PREP = CODE_REL + "1-data-preparation/python/"
renames = [("docs/reverse_engineering.md", "project/docs/reverse_engineering.md"), ("docs/scraping_ethics.md", "project/docs/scraping_ethics.md"), ("docs/data_dictionary.md", "project/docs/data_dictionary.md"),
           ("scraper/scrape_jobs.py", PREP + "scraper/scrape_jobs.py"), ("data/raw/", "project/data/raw/ (tidak di-commit)"), ("scripts/clean.py", PREP + "02_clean.py"),
           ("config/skills.csv", "project/data/reference/skills.csv"), ("scripts/load_db.py", PREP + "03_extract_skills.py, " + PREP + "04_build_db.py"), ("jobs.duckdb", "project/jobs.duckdb (tidak di-commit)"),
           ("outputs/skill_eval.csv", "project/results/2-analysis/skill_eval.csv"), ("sql/", CODE_REL + "1-data-preparation/sql/01_schema.sql, " + CODE_REL + "2-analysis/sql/02_queries.sql"),
           ("notebooks/analysis.ipynb", "project/results/3-presentation/analysis.ipynb"), ("outputs/aggregates/*.csv", "project/results/2-analysis/skill_share.csv"),
           (".github/workflows/weekly_scrape.yml", ".github/workflows/weekly_scrape.yml"), ("dashboard/app.py", CODE_REL + "3-presentation/streamlit/app.py"), ("requirements.txt", "project/requirements.txt"),
           ("outputs/skill_onesheet.pdf", "(tidak dibuat)"),
           ("(tidak ada)", ", ".join(("common.py", "01_load_raw.py", "05_run_queries.py", "06_crosscheck.py", "07_validate_skills.py", "08_hypotheses_stats.py", "09_skill_match.py", "kpi_pandas.py",
                                       "10_build_dashboard_data.py", "11_build_notebook.py", "12_build_readme.py")))]
for a, b in renames:
    for part in b.split(", "):
        part = part.split(" (")[0]
        if "*" in part or "/" not in part or "tidak di-commit" in b or part in ("common.py",) or "." not in part.split("/")[-1]:
            continue
        assert (REPO / part).exists(), part
allpy = {p.name for p in (REPO / CODE_REL).rglob("*.py")}
assert {"common.py", "01_load_raw.py", "05_run_queries.py", "06_crosscheck.py", "07_validate_skills.py", "08_hypotheses_stats.py", "09_skill_match.py", "kpi_pandas.py", "10_build_dashboard_data.py",
        "11_build_notebook.py", "12_build_readme.py"} <= allpy, "skrip pada daftar rename belum ada"
rp5 = mk('<div class="card"><p><b>Jawaban singkat:</b> 12 langkah rancangan, tetapi hanya sebagian yang dijalankan seperti rancangan. Cleaning, database, query, dan skill match selesai; scraper, jadwal mingguan, dan dashboard publik belum, '
         'dan langkah 1 dan 2 terhambat akses ke situs dan repo lama.</p></div>',
         table(["Langkah", "Rancangan", "Realisasi", "Verdict", "Catatan"], [[a, b, c, d, e] for a, b, c, d, e in steps]),
         '<div class="card"><h4>Penyesuaian dan improvisasi yang tidak ada di rancangan</h4><ul class="tight">',
         '<li>Data berasal dari satu berkas arsip (DataCenter versi 1), bukan dari 2.560 postingan lama dan batch mingguan. Keputusan ini diambil bersama pemilik karena data lain tidak tersedia.</li>',
         '<li>Industri diganti bidang kerja Jobstreet; level dibaca dari judul; skill dimiliki untuk skill match diasumsikan (Excel, SQL, Python). Semua ada di <code>project/docs/definitions.md</code>.</li>',
         f'<li>Validasi skill extraction memakai {I(SAMPLE_N)} lowongan dengan label dari Claude. Label dibuat tanpa melihat keluaran kamus, dan kamus tidak disetel ulang.</li>',
         f'<li>Cek silang SQL vs pandas ({I(cx_n)} pemeriksaan) dan pembanding hasil studi awal ditambahkan di luar rancangan.</li>',
         '<li>Interval Wilson 95% dan uji eksak ditambahkan karena sampel kecil.</li>',
         '<li>Atribut turunan per lowongan (tanpa job_id, judul, perusahaan, teks) disimpan di <code>dash_rows.csv</code> untuk filter dashboard.</li></ul></div>',
         '<div class="card"><h4>Perubahan nama dan lokasi file terhadap rancangan</h4>',
         table(["Rancangan", "Realisasi"], [[f"<code>{a}</code>" if a != "(tidak ada)" else "(tidak ada di rancangan)", ", ".join(f"<code>{x}</code>" if not x.startswith("(") else x for x in b.split(", "))] for a, b in renames]) + '</div>')

# ---------------------------------------------------------------- 6. output
chk = lambda rel: (REPO / rel).exists()
outs = [("Dashboard pasar kerja", "Utama", PART("Sebagian"), "<code>streamlit/app.py</code> (4 halaman, 4 filter) diuji lokal dengan AppTest. Link publik belum ada"),
        ("Scraper terjadwal", "Utama", PART("Sebagian"), "<code>scrape_jobs.py</code> dan <code>weekly_scrape.yml</code> ditulis; belum pernah dijalankan, jadi belum ada log batch"),
        ("Database & query SQL", "Utama", OK("Tercapai"), f"<code>jobs.duckdb</code> (dibuat ulang, tidak di-commit), 4 tabel, dan {I(nsql)} file SQL dengan <code>lag</code> dan <code>sum over</code>"),
        ("Kamus skill & aturan normalisasi", "Utama", OK("Tercapai"), "<code>skills.csv</code>, <code>definitions.md</code>, <code>cleaning_decisions.md</code>, dan hasil evaluasi di <code>skill_eval.csv</code>"),
        ("Notebook analisis", "Utama", OK("Tercapai"), "<code>analysis.ipynb</code> dieksekusi tanpa error; Q10 dan Q11 ditulis sebagai belum bisa dijawab"),
        ("Laporan temuan & rekomendasi", "Utama", OK("Tercapai"), "<code>README.md</code> dan halaman ini"),
        ("Tabel agregat publik", "Utama", OK("Tercapai"), f"{I(len(resfiles))} CSV di <code>project/results/</code>, tanpa judul, perusahaan, atau teks lowongan"),
        ("One-sheet skill prioritas", "Opsional", NO("Tidak dibuat"), "Opsional, tidak dibuat")]
nU = [o for o in outs if o[1] == "Utama"]
cnt = lambda s: sum(1 for o in nU if s in o[2])
docs = [("docs/reverse_engineering.md", "Peta kode project lama", "project/docs/reverse_engineering.md"), ("docs/scraping_ethics.md", "Etika scraping", "project/docs/scraping_ethics.md"),
        ("docs/data_dictionary.md", "Kamus data", "project/docs/data_dictionary.md"), ("scraper/scrape_jobs.py", "Skrip scraper", PREP + "scraper/scrape_jobs.py"),
        ("data/raw/", "Data mentah (tidak di-commit)", "project/data/raw"), ("scripts/clean.py", "Cleaning", PREP + "02_clean.py"), ("config/skills.csv", "Kamus skill", "project/data/reference/skills.csv"),
        ("scripts/load_db.py", "Skill extraction dan load", PREP + "04_build_db.py"), ("jobs.duckdb", "File database (tidak di-commit)", "project/jobs.duckdb"),
        ("outputs/skill_eval.csv", "Precision dan recall", "project/results/2-analysis/skill_eval.csv"), ("sql/", "Query dan view", "project/code/2-analysis/sql/02_queries.sql"),
        ("notebooks/analysis.ipynb", "Notebook", "project/results/3-presentation/analysis.ipynb"), ("outputs/aggregates/*.csv", "Tabel agregat", "project/results/2-analysis/skill_share.csv"),
        (".github/workflows/weekly_scrape.yml", "Jadwal scraping", ".github/workflows/weekly_scrape.yml"), ("dashboard/app.py", "Dashboard Streamlit", "project/code/3-presentation/streamlit/app.py"),
        ("requirements.txt", "Paket Python", "project/requirements.txt"), ("README.md", "Laporan temuan", "README.md"), ("index.html", "Pengalihan ke design-and-report/", "index.html"),
        ("outputs/skill_onesheet.pdf", "One-sheet", "outputs/skill_onesheet.pdf")]
stat_doc = lambda rel: PART("Tidak di-commit") if ("duckdb" in rel or rel.endswith("raw")) else (OK("Ada") if chk(rel) else NO("Belum ada"))
rp6 = mk(f'<div class="card"><p><b>Jawaban singkat:</b> {I(cnt("Tercapai"))} dari {I(len(nU))} output Utama tercapai penuh dan {I(cnt("Sebagian"))} sebagian (dashboard belum punya link publik; scraper belum pernah dijalankan). '
         'One-sheet (Opsional) tidak dibuat.</p></div>',
         table(["Output", "Label", "Status", "Bukti"], [[f"<b>{a}</b>", b, c, d] for a, b, c, d in outs]),
         '<div class="card"><h4>Daftar dokumen pada rancangan vs repositori</h4>',
         table(["Dokumen (rancangan)", "Isi", "Lokasi sekarang", "Status"], [[f"<code>{a}</code>", b, f"<code>{c}</code>", stat_doc(c)] for a, b, c in docs]),
         '<p>Data mentah dan <code>jobs.duckdb</code> tidak di-commit karena bisa dibuat ulang oleh skrip. Dokumen yang statusnya Belum ada memang tidak dibuat.</p></div>')

# ---------------------------------------------------------------- 7. kesimpulan
utama = [q for q, v in PRIO.items() if v == "Utama"]
ans_utama = [q for q in utama if q not in NOANS]
crit = [("1. Kesembilan pertanyaan Utama terjawab dengan angka", PART("Sebagian"), f"{I(len(ans_utama))} dari {I(len(utama))} terjawab; Q10 (tren mingguan) belum bisa dijawab (bagian 2)"),
        ("2. Skill extraction mencapai precision dan recall minimal 90% pada 100 lowongan berlabel manual", PART("Sebagian"),
         f"Precision {P(evt.precision, 0)}, recall {P(evt.recall, 0)}, tetapi pada {I(SAMPLE_N)} lowongan dengan label dari Claude (bukan 100 lowongan berlabel manusia)"),
        ("3. Scraper mingguan berjalan minimal 4 minggu berturut-turut dan aturan situs dipatuhi", NO("Belum tercapai"), "Scraper dan jadwal ditulis, belum pernah dijalankan; robots.txt belum diperiksa"),
        ("4. Angka SQL sama dengan pandas dan kelima hipotesis tercatat", OK("Tercapai"), f"{I(cx_ok)} dari {I(cx_n)} pemeriksaan PASS; lima hipotesis tercatat (1 terbukti, 4 sebagian)"),
        ("5. Orang awam menyebut 3 skill teratas dan kota teratas dalam kurang dari 1 menit", PART("Belum diuji"), "Halaman Ringkasan dashboard memuat keduanya, tetapi belum diuji ke pembaca sebenarnya"),
        ("6. Checklist standar (pertanyaan bisnis, cleaning, SQL, dashboard ter-deploy, README)", PART("Sebagian"), "Semua ada kecuali dashboard ter-deploy")]
ncr = sum(1 for c in crit if ">Tercapai<" in c[1])
rp7 = mk(
    '<div class="card"><h4>7.1 Hasil analisis: jawaban atas pertanyaan utama</h4>',
    '<p><i>Skill dan kisaran salary apa yang paling banyak diminta pada lowongan Data Analyst di Indonesia, di kota dan industri mana, dan bagaimana trennya dari minggu ke minggu?</i></p><ul class="tight">',
    f'<li><b>Skill:</b> Excel ({P(excel.share)}), SQL ({P(sql.share)}), Power BI ({P(pbi.share)}), Tableau ({P(tab.share)}), dan Python ({P(py.share)}) pada {I(n)} lowongan unik Jobstreet (satu kali ambil, Oktober 2026). Interval kepercayaan lebar, misalnya Excel {P(ci.loc["Excel"].ci_low, 0)} sampai {P(ci.loc["Excel"].ci_high, 0)}.</li>',
    f'<li><b>Salary:</b> hanya {I(n_sal)} lowongan ({P(n_sal / n)}) mencantumkan salary; median Rp {jt(ssum.median_min)} sampai {jt(ssum.median_max)} juta per bulan. Terlalu sedikit untuk membandingkan skill atau kota.</li>',
    f'<li><b>Kota dan industri:</b> {city_top.city} memegang {P(city_top.share)} lowongan ({I(city_top.jobs)} dari {I(n)}); bidang kerja terbanyak {ind.industry[0]} ({P(ind.share[0])}). Industri perusahaan tidak tersedia.</li>',
    '<li><b>Tren:</b> belum bisa dijawab; data hanya satu kali ambil dan data lama tidak ditemukan.</li></ul></div>',
    '<div class="card"><h4>7.2 Impact</h4><ul class="tight">',
    f'<li><b>Nilai praktis (estimated):</b> dengan Excel, SQL, dan Python, {P(m0.share)} lowongan bisa dilamar tanpa kekurangan skill. Menambah {nx1.skill} atau {nx2.skill} menaikkannya menjadi {P(nx1.share_setelah)}. Angka ini dari 48 lowongan dan asumsi skill dimiliki, bukan statistik pasar.</li>',
    '<li><b>Nilai analitis:</b> skill diambil dari teks dengan kamus yang bisa diperiksa, salary diparse, duplikat dibuang, dan setiap porsi disertai interval. Hasil studi awal berhasil direproduksi di database.</li>',
    '<li><b>Nilai portofolio:</b> pipeline dari data mentah ke database, SQL dengan window function, validasi skill extraction, uji hipotesis, notebook, dan dashboard; batasan data dicatat jujur.</li>',
    '<li><b>Belum terukur:</b> perubahan permintaan dari minggu ke minggu dan keputusan melamar yang benar-benar diambil dari temuan ini.</li></ul></div>')
rp7 += ('<div class="card"><h4>7.3 Success criteria</h4>' + table(["Kriteria (Design Project, bagian 8)", "Status", "Bukti"], [[a, b, c] for a, b, c in crit])
        + f'<p><b>Hasil:</b> {I(ncr)} dari {I(len(crit))} kriteria tercapai, {I(len(crit) - ncr)} sebagian atau belum tercapai.</p></div>')
rp7 += mk('<div class="card"><h4>7.4 Rekomendasi</h4><ul class="tight">',
          f'<li>Prioritaskan Excel dan SQL: keduanya paling sering diminta ({P(excel.share, 0)} dan {P(sql.share, 0)}). Setelah itu Power BI, yang menambah {I(nx1.tambahan_lowongan)} lowongan yang bisa dilamar pada simulasi skill match.</li>',
          f'<li>Power BI lebih sering disebut daripada Tableau ({I(pbi.jobs)} dibanding {I(tab.jobs)} lowongan), tetapi selisih itu belum signifikan (p-value {pv(hyp.loc[5].p_value)}); belajar salah satu sudah cukup sebagai awal.</li>',
          f'<li>Fokuskan lamaran di {city_top.city} ({P(city_top.share, 0)} lowongan), dan jangan menjadikan angka salary di sini sebagai patokan negosiasi: hanya {I(n_sal)} lowongan yang mencantumkannya.</li>',
          '<li>Gunakan hasil ini sebagai gambaran awal, lalu ulangi setelah scraping mingguan berjalan beberapa minggu.</li></ul></div>')
rp7 += mk('<div class="card"><h4>7.5 Saran perbaikan</h4><ul class="tight">',
          '<li>Jalankan <code>scrape_jobs.py</code> dari komputer sendiri setelah memeriksa robots.txt dan ketentuan Jobstreet, lalu aktifkan <code>weekly_scrape.yml</code> minimal 4 minggu supaya Q10 dan Q11 bisa dijawab.</li>',
          '<li>Cari berkas 2.560 postingan project lama dan unggah ke DataCenter sebagai versi baru.</li>',
          f'<li>Minta orang lain memberi label pada 100 lowongan (bukan {I(SAMPLE_N)} dari Claude), lalu perbaiki kamus: tambahkan sinonim untuk "konsep statistik" dan "AI/ML".</li>',
          '<li>Ambil industri perusahaan dari halaman perusahaan atau sumber lain supaya Q5 dan Q8 menjawab industri sebenarnya.</li>',
          '<li>Deploy dashboard ke Streamlit Community Cloud dan uji ke satu pembaca awam.</li></ul></div>')
rp7 += mk('<div class="card"><h4>7.6 Batasan</h4><ul class="tight">',
          f'<li>Data hanya {I(n)} lowongan unik dari satu platform dan satu kali ambil. Interval kepercayaan lebar; selisih kecil antar skill tidak bisa dibedakan dari kebetulan.</li>',
          '<li>Lisensi data belum diverifikasi: konten milik Jobstreet dan perusahaan, ketentuan layanan belum dicek. <code>dash_rows.csv</code> berisi atribut turunan tanpa teks; hapus bila dianggap terlalu dekat dengan konten asli.</li>',
          '<li>Q10 dan Q11 belum bisa dijawab. Scraper dan jadwal mingguan belum pernah dijalankan, robots.txt belum diperiksa, dan dashboard belum di-deploy; kriteria 3 belum tercapai dan 5 belum diuji.</li>',
          f'<li>Validasi skill extraction memakai {I(SAMPLE_N)} lowongan dengan label dari Claude, bukan 100 lowongan berlabel manusia. Precision {P(evt.precision, 0)} dan recall {P(evt.recall, 0)} berlaku untuk sampel ini saja.</li>',
          '<li>Batas dan asumsi buatan sendiri: level dari judul, bidang kerja sebagai pengganti industri, skill dimiliki (Excel, SQL, Python), "spreadsheet" dihitung Excel, dan kata kunci remote.</li>',
          f'<li>Skill yang disebut belum tentu wajib. Salary hanya {I(n_sal)} lowongan dan condong ke yang mencantumkannya. Hipotesis 4 tidak bisa diuji (hanya {I(nj)} lowongan junior).</li></ul></div>')

evq = [("1", "rp1", "Data yang didapat", PART("Sebagian"), f"{I(n_raw)} lowongan (satu kali ambil), {I(n)} unik; {I(trow['job_skills'])} baris skill; data lama 2.560 tidak ada"),
       ("2", "rp2", "Business question terjawab?", PART(f"{len(QT) - len(NOANS)} dari {len(QT)}"), f"{I(len(QT) - len(NOANS))} terjawab ({npr['Utama']} Utama, {npr['Pendukung']} Pendukung, {npr['Tambahan']} Tambahan), {I(nnote)} dengan catatan; Q10 dan Q11 belum bisa"),
       ("3", "rp3", "Dataset sesuai?", NO("Berubah"), "Data jauh lebih kecil dari rancangan; empat tabel sesuai, industri diganti bidang kerja"),
       ("4", "rp4", "Tools sesuai?", PART("Sebagian"), "Python, DuckDB, dan kamus dipakai; scraper, jadwal, dan deploy belum berjalan"),
       ("5", "rp5", "Alur sesuai?", PART("Sebagian"), f"{I(len(steps))} langkah; {I(sum(1 for s in steps if 'Sesuai' in s[3] and 'Sebagian' not in s[3]))} sesuai penuh, langkah 10 belum dikerjakan"),
       ("6", "rp6", "Output tercapai?", PART(f"{cnt('Tercapai')} penuh, {cnt('Sebagian')} sebagian"), f"{cnt('Tercapai')} dari {len(nU)} output Utama penuh"),
       ("7", "rp7", "Kesimpulan", OK("Tersedia"), f"Hasil analisis, Impact, {len(crit)} kriteria sukses, rekomendasi, saran perbaikan, batasan")]
evq_html = '<div class="scroll"><table class="evq"><tr><th>No</th><th>Pertanyaan evaluasi</th><th>Verdict</th><th>Ringkasan</th></tr>' + "".join(
    f'<tr><td><span class="en">{n_}</span></td><td><a href="#{h}">{t}</a></td><td>{v}</td><td>{s}</td></tr>' for n_, h, t, v, s in evq) + "</table></div>"
H = lambda i, t, sm, body: f'\n<h2 id="rp{i}">{i}. {t}<small>{sm}</small></h2>\n{body}\n'
report = mk(
    '<div class="pane" id="report" data-tab="report" hidden>\n',
    f'<div class="callout g"><h4>Report Project versi 2: evaluasi hasil terhadap Design Project</h4><p>Halaman ini disusun sebagai 7 jawaban atas pertanyaan evaluasi. Tabel dan grafik dibuat otomatis dari hasil query SQL (DuckDB) dan uji statistik. '
    f'Hasil SQL dicek silang dengan pandas ({I(cx_ok)} dari {I(cx_n)} pemeriksaan). Angka pada teks diaudit terhadap file di <code>project/results/</code>: @@AUDIT@@ angka diperiksa tanpa selisih. '
    'Data hanya satu kali ambil dari Jobstreet (bukan scraping mingguan), sehingga hasilnya gambaran awal dan bukan statistik pasar kerja. Rancangan lengkap ada di tab <a href="#design">Design Project</a>.</p></div>\n',
    evq_html,
    H(1, "Data yang berhasil didapatkan", "Isi data mentah, tabel di database, dan data hasil analisis", rp1),
    H(2, "Apakah business question terjawab?", f"{len(QT)} pertanyaan pada Design Project, dijawab dengan data", rp2),
    H(3, "Apakah dataset sesuai dengan Design Project?", "Perbandingan rancangan dengan realisasi", rp3),
    H(4, "Apakah tools yang digunakan sesuai?", "Perbandingan rancangan dengan eksekusi", rp4),
    H(5, "Apakah alur pengerjaan sesuai dengan Design Project?", f"{len(steps)} langkah rancangan vs yang dijalankan", rp5),
    H(6, "Apakah project output tercapai?", "Output pada Design Project, bagian 7", rp6),
    H(7, "Kesimpulan", "Hasil analisis, Impact, success criteria, rekomendasi, saran perbaikan, dan batasan", rp7),
    '</div>\n')

# ---------------------------------------------------------------- audit angka
STATIC = {str(i) for i in range(0, 32)} | {"40", "48", "60", "80", "100", "0,05", "95", "2.560", "3.000", "150", "300", "2026", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
          "0,001", "1E-9", "15", "90"}
STATIC |= {f"{a}.{b}" for a in range(1, 10) for b in range(1, 10)}
n_tok, bad = audit(report, STATIC)
manual = [("seluruh CSV hasil terdokumentasi", not miss), ("crosscheck pandas semua PASS", cx_ok == cx_n), ("semua uji constraint ditolak", (ctest.outcome == "ditolak").all()),
          ("semua pemeriksaan konsistensi 0 pelanggaran", (cons.violations == 0).all()), ("lowongan unik = mentah - duplikat", n == n_raw - n_dup),
          ("jumlah pertanyaan = 14 (9 Utama, 4 Pendukung, 1 Tambahan)", len(QT) == 14 and npr == {"Utama": 9, "Pendukung": 4, "Tambahan": 1}),
          ("Q yang belum bisa dijawab hanya Q10 dan Q11", NOANS == {10, 11}), ("catatan (kuning) tepat Q3, Q4, Q5, Q8, Q9, Q10, Q11, Q12, Q13", WARN == {3, 4, 5, 8, 9, 10, 11, 12, 13}),
          ("jumlah pertanyaan unik pada bagian 2 = 14", qn_uniq == list(range(1, 15))), ("langkah rancangan = 12", len(steps) == 12),
          ("kota teratas = Jakarta", city_top.city == "Jakarta" and int(city_top.jobs) == 31), ("studi awal: semua skill yang dibandingkan sama", oc.get("Beda", 0) == 0),
          ("jumlah lowongan sampel = SAMPLE_N", int(R("skill_eval_errors.csv").shape[0]) <= int(evt.labeled)), ("pasangan skill teratas tanpa Dashboard", "Dashboard" not in set(cooc.skill_a) | set(cooc.skill_b)),
          ("lowongan per minggu = lowongan unik", int(wj.jobs.sum()) == n), ("salary tercantum = salary_summary", int(ssum.n_salary) == n_sal)]
assert all(v for _, v in manual), [k for k, v in manual if not v]
if bad:
    print("TOKEN TIDAK TERDAFTAR:", bad)
    sys.exit(1)
report = report.replace("@@AUDIT@@", I(n_tok) + f" (ditambah {I(len(manual))} klaim manual)")

# ---------------------------------------------------------------- rakit halaman
v1 = (HERE / "page_v1.html").read_text(encoding="utf-8")
a = v1.index('<div class="pane" id="report"')
b = v1.index("</main>")
design_pane = v1[v1.index('<div class="pane" id="design"'):a]
nav_old = re.search(r'<nav aria-label="Project navigation">.*?</nav>', v1, re.S).group(0)
btn = lambda t: re.search(rf'<button type="button" class="tab[^"]*" data-t="{t}".*?</button>', nav_old, re.S).group(0)
design_links = re.search(r'<div class="links" data-tab="design">.*?</div>', nav_old, re.S).group(0)
report_links = ('<div class="links" data-tab="report" hidden>' + "".join(f'<a href="#rp{i}">{t}</a>' for i, t in
               enumerate(["Data", "Business Questions", "Dataset", "Tools", "Alur Kerja", "Project Output", "Kesimpulan"], 1)) + "</div>")
nav_new = f'<nav aria-label="Project navigation">{btn("design")}{btn("report")}{design_links}{report_links}</nav>'
css = (HERE / "report.css").read_text(encoding="utf-8")
html = v1[:a] + report + v1[b:]
html = html.replace(nav_old, nav_new)
i = html.rindex("</style>")
html = html[:i] + css + html[i:]
out = REPO / "design-and-report" / "index.html"
out.write_text(html, encoding="utf-8")
assert design_pane == html[html.index('<div class="pane" id="design"'):html.index('<div class="pane" id="report"')], "pane Design berubah"
print(f"index.html {len(html) / 1024:.0f} KB; {n_tok} angka diaudit; {len(manual)} klaim manual; pane Design identik")
