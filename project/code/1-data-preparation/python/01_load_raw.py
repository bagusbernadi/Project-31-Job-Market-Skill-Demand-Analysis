"""Langkah 3 (pemuatan): ambil data mentah versi 1 dari arsip DataCenter ke project/data/raw/ dan catat sidik jari berkas.
Jalankan: python project/code/1-data-preparation/python/01_load_raw.py   (opsional: DATACENTER_ZIP=/path/zip)"""
import hashlib
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import BATCH_ID, DATACENTER_ZIP, RAW_DIR, RES_PREP, SCRAPED_AT, SOURCE_VERSION  # noqa: E402

assert DATACENTER_ZIP.exists(), f"zip tidak ditemukan: {DATACENTER_ZIP} (atur DATACENTER_ZIP)"
rows = []
with zipfile.ZipFile(DATACENTER_ZIP) as z:
    assert z.testzip() is None
    for name in ("jobs_target_all.csv", "jobs_detail.csv"):
        data = z.read(name)
        (RAW_DIR / name).write_bytes(data)
        n = len(pd.read_csv(RAW_DIR / name))
        rows.append(dict(file=name, bytes=len(data), rows=n, sha256=hashlib.sha256(data).hexdigest(), batch_id=BATCH_ID,
                         version=SOURCE_VERSION, access_date=SCRAPED_AT))
pd.DataFrame(rows).to_csv(RES_PREP / "download_log.csv", index=False)
print(pd.DataFrame(rows)[["file", "bytes", "rows"]].to_string(index=False))
