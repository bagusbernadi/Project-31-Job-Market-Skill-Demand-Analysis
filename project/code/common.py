"""Pengaturan bersama untuk semua skrip. Semua jalur relatif terhadap folder project/."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # folder project/
DATA = ROOT / "data"
RAW_DIR = DATA / "raw"                                 # data mentah dari DataCenter (tidak di-commit)
CLEAN_DIR = DATA / "clean"                             # data bersih (tidak di-commit)
REF_DIR = DATA / "reference"
SKILLS_CSV = REF_DIR / "skills.csv"                    # kamus skill (dim_skill)
MY_SKILLS_CSV = REF_DIR / "my_skills.csv"              # skill yang dianggap dimiliki (asumsi, Q12)
LABELS_CSV = REF_DIR / "skill_labels_sample.csv"       # label sampel untuk validasi (Q13)
DB_PATH = ROOT / "jobs.duckdb"
CODE = ROOT / "code"
SQL_PREP = CODE / "1-data-preparation" / "sql"
SQL_ANALYSIS = CODE / "2-analysis" / "sql"
RES_PREP = ROOT / "results" / "1-data-preparation"
RES_ANALYSIS = ROOT / "results" / "2-analysis"
RES_PRESENT = ROOT / "results" / "3-presentation"
DOCS_DIR = ROOT / "docs"
for _d in (RAW_DIR, CLEAN_DIR, RES_PREP, RES_ANALYSIS, RES_PRESENT):
    _d.mkdir(parents=True, exist_ok=True)

# Sumber data: arsip DataCenter (repo private). Ubah lewat variabel lingkungan bila lokasinya berbeda.
DATACENTER_ZIP = Path(os.environ.get("DATACENTER_ZIP", "/home/claude/datacenter/jobstreet-job-postings/jobstreet-job-postings.zip"))
SOURCE_VERSION = "1 (scraper data-analyst-job-scraper)"
SCRAPED_AT = "2026-10-18"                              # tanggal akses versi 1 (dikonfirmasi pemilik, tercatat di DataCenter)
BATCH_ID = "v1"
SEED = 31260302
ALPHA = 0.05
SAMPLE_N = 20                                          # jumlah lowongan sampel berlabel (rancangan: 100, hanya ada 48 lowongan unik)

# Normalisasi lokasi: pola -> kota
CITY_RULES = [(r"jakarta|kemayoran|cilincing|kebayoran", "Jakarta"), (r"tangerang", "Tangerang"), (r"surabaya", "Surabaya"), (r"medan", "Medan"),
              (r"bandung", "Bandung"), (r"yogyakarta", "Yogyakarta"), (r"bali", "Bali"), (r"tegal", "Tegal"), (r"semarang", "Semarang"), (r"malang", "Malang")]
LEVEL_SENIOR = r"\b(?:senior|sr\.?|head|lead|supervisor|manager|principal)\b"
LEVEL_JUNIOR = r"\b(?:junior|jr\.?|fresh|intern|trainee|entry)\b"
REMOTE_PAT = r"\bremote\b|\bhybrid\b|\bwfh\b|work from home"
NON_TOOL = {"Dashboard"}                               # konsep, bukan tool: tidak dihitung dalam skill match (Q12)
MIN_GROUP = 5                                          # jumlah lowongan minimum per kelompok agar perbandingan dianggap layak


def result(name):
    """Cari CSV hasil di folder hasil per tahap."""
    for d in (RES_PREP, RES_ANALYSIS, RES_PRESENT):
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def norm_city(loc):
    s = str(loc or "").lower()
    for pat, city in CITY_RULES:
        if re.search(pat, s):
            return city
    return "Tidak spesifik" if s in ("", "indonesia", "nan") else str(loc).split(",")[0].strip()
