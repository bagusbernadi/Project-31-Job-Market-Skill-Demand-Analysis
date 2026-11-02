"""Langkah 7: jalankan query SQL analitik dan simpan hasilnya sebagai CSV (results/2-analysis)."""
import re
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import DB_PATH, RES_ANALYSIS, SQL_ANALYSIS  # noqa: E402

con = duckdb.connect(str(DB_PATH), read_only=True)
blocks = re.split(r"^-- name: (\w+)\s*$", (SQL_ANALYSIS / "02_queries.sql").read_text(encoding="utf-8"), flags=re.M)[1:]
for name, q in zip(blocks[::2], blocks[1::2]):
    df = con.execute(q).df()
    for c in df.columns:
        if df[c].dtype.kind == "f":
            df[c] = df[c].round(8)
    df.to_csv(RES_ANALYSIS / f"{name}.csv", index=False)
    print(f"{name}: {len(df)} baris")
