"""Langkah 4: cleaning dan normalisasi. Membaca data mentah, menulis data bersih (data/clean) dan log ke results/1-data-preparation.
Aturan dan keputusan: project/docs/cleaning_decisions.md"""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import (BATCH_ID, CLEAN_DIR, LEVEL_JUNIOR, LEVEL_SENIOR, RAW_DIR, REMOTE_PAT, RES_PREP, SCRAPED_AT, norm_city)  # noqa: E402

t = pd.read_csv(RAW_DIR / "jobs_target_all.csv", dtype={"id": str})
d = pd.read_csv(RAW_DIR / "jobs_detail.csv", dtype={"id": str})
log = []


def rule(code, text, found, decision):
    log.append(dict(rule=code, description=text, rows_found=int(found), decision=decision))


# C1 id ganda di tiap berkas
rule("C1", "Job ID ganda di jobs_target_all.csv atau jobs_detail.csv", t.id.duplicated().sum() + d.id.duplicated().sum(), "Tidak ada; dicek, tidak ada tindakan")
# C2 deskripsi tanpa lowongan (id ada di detail, tidak ada di daftar)
extra = ~d.id.isin(t.id)
rule("C2", "Deskripsi tanpa baris di daftar lowongan", extra.sum(), "Dibuang (tidak ada judul, kota, atau tanggal)")
# C3 lowongan tanpa deskripsi
nodesc = ~t.id.isin(d.id)
rule("C3", "Lowongan tanpa deskripsi", nodesc.sum(), "Dibuang bila ada (skill tidak bisa diambil)")
df = t[~nodesc].merge(d[~extra].drop_duplicates("id"), on="id", how="inner")
n_merged = len(df)

# C4 teks: ganti spasi khusus, rapikan spasi
for c in ("title", "company", "location", "salary", "category", "work_type", "description", "teaser"):
    df[c] = df[c].astype("string").str.replace("\xa0", " ", regex=False).str.replace(r"[ \t]+", " ", regex=True).str.strip()
rule("C4", "Spasi khusus (NBSP) dan spasi ganda pada teks", t.salary.astype("string").str.contains("\xa0", na=False).sum(),
     "Diganti spasi biasa pada semua kolom teks")

# C5 salary: parse ke angka per bulan
def parse_salary(s):
    if pd.isna(s) or "month" not in str(s).lower():
        return (None, None)
    n = [int(x.replace(".", "")) for x in re.findall(r"\d[\d.]*", str(s))]
    return (min(n), max(n)) if n else (None, None)


sal = df.salary.apply(parse_salary)
df["salary_min"], df["salary_max"] = [x[0] for x in sal], [x[1] for x in sal]
rule("C5", "Salary ditulis sebagai teks bebas ('Rp 7.000.000 – Rp 10.500.000 per month')", df.salary.notna().sum(),
     f"Diparse ke salary_min dan salary_max (per bulan); {int(df.salary_min.notna().sum())} berhasil, sisanya kosong (tidak dicantumkan)")
assert df.salary.notna().sum() == df.salary_min.notna().sum(), "ada salary yang tidak terparse"

# C6 tanggal
df["posted_date"] = pd.to_datetime(df.listing_date, utc=True).dt.tz_convert("Asia/Jakarta").dt.date.astype(str)
df["week_start"] = (pd.to_datetime(df.posted_date) - pd.to_timedelta(pd.to_datetime(df.posted_date).dt.weekday, unit="D")).dt.date.astype(str)
rule("C6", "listing_date berformat UTC (ISO 8601)", len(df), "Diubah ke tanggal WIB (posted_date) dan awal minggu Senin (week_start)")

# C7 lokasi, level, remote, industri
df["city"] = df.location.apply(norm_city)
df["province"] = df.location.astype("string").str.split(",").str[-1].str.strip()
tl = df.title.str.lower()
df["level"] = "Tidak disebut"
df.loc[tl.str.contains(LEVEL_JUNIOR, regex=True), "level"] = "Junior"
df.loc[tl.str.contains(LEVEL_SENIOR, regex=True), "level"] = "Senior"
df["title_norm"] = df.title.str.replace(r"\bsr\.?\b", "Senior", flags=re.I, regex=True).str.replace(r"\bjr\.?\b", "Junior", flags=re.I, regex=True)
df["industry"] = df.category            # Jobstreet tidak memberi industri perusahaan; klasifikasi bidang kerja dipakai sebagai pengganti
df["remote_hybrid"] = (df.title + " " + df.description).str.contains(REMOTE_PAT, case=False, regex=True)
rule("C7", "Nama kota tidak seragam (kecamatan, provinsi, 'Indonesia')", (df.location != df.city).sum(), "Dinormalisasi ke kota/wilayah seragam (kolom city); kolom industry diisi klasifikasi bidang Jobstreet (bukan industri perusahaan)")

# C8 duplikat: deskripsi identik (iklan sama diposting ulang) dan judul+perusahaan sama
df = df.sort_values(["posted_date", "id"]).reset_index(drop=True)
dup_desc = df.duplicated("description", keep="first")
rule("C8", "Deskripsi identik (iklan sama diposting ulang atau dobel)", dup_desc.sum(), "Dibuang, yang paling awal dipertahankan")
dup_tc = df[~dup_desc].duplicated(["title_norm", "company"], keep=False)
rule("C9", "Judul dan perusahaan sama tetapi deskripsi berbeda", dup_tc.sum(), "Dipertahankan (bisa posisi berbeda); hanya dicatat")
df["is_duplicate"] = dup_desc
df["first_seen"] = df["last_seen"] = SCRAPED_AT
df["scraped_at"], df["batch_id"], df["source"] = SCRAPED_AT, BATCH_ID, "datacenter-v1"
df["url"] = "https://id.jobstreet.com/id/job/" + df.id
df = df.rename(columns={"id": "job_id"})

keep = ["job_id", "scraped_at", "batch_id", "source", "title", "title_norm", "company", "location", "city", "province", "level", "industry", "work_type", "salary", "salary_min",
        "salary_max", "posted_date", "week_start", "remote_hybrid", "first_seen", "last_seen", "is_duplicate", "description", "url"]
df[keep].to_csv(CLEAN_DIR / "job_postings_all.csv", index=False)
clean = df[~df.is_duplicate][keep]
clean.to_csv(CLEAN_DIR / "job_postings.csv", index=False)

pd.DataFrame(log).to_csv(RES_PREP / "cleaning_log.csv", index=False)
dq = pd.DataFrame([dict(item="Baris jobs_target_all.csv (mentah)", value=len(t)), dict(item="Baris jobs_detail.csv (mentah)", value=len(d)),
                   dict(item="Lowongan setelah digabung dengan deskripsi", value=n_merged), dict(item="Duplikat dibuang", value=int(dup_desc.sum())),
                   dict(item="Lowongan unik dianalisis", value=len(clean)), dict(item="Salary tercantum", value=int(clean.salary_min.notna().sum())),
                   dict(item="Salary kosong", value=int(clean.salary_min.isna().sum())), dict(item="Kota/wilayah unik", value=clean.city.nunique()),
                   dict(item="Perusahaan unik", value=clean.company.nunique())])
dq.to_csv(RES_PREP / "data_quality_summary.csv", index=False)
print(dq.to_string(index=False)); print(pd.DataFrame(log)[["rule", "rows_found", "decision"]].to_string(index=False))
