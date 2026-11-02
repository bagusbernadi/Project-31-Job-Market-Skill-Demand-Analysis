"""Scraper lowongan Jobstreet Indonesia (upgrade dari scrape_list2.py + scrape_detail2.py di repo data-analyst-job-scraper).
Perubahan: satu skrip untuk daftar + detail, batch bertanggal (kolom scraped_at), cek robots.txt di awal, jeda acak, coba ulang, log per batch.
TIDAK DIJALANKAN di sesi pembuatan (jaringan sandbox memblokir situs). Dijalankan lewat .github/workflows/weekly_scrape.yml atau manual:
    python project/code/1-data-preparation/python/scraper/scrape_jobs.py --max-pages 5
Hasil: project/data/raw/batch_YYYY-MM-DD/{jobs_target_all.csv, jobs_detail.csv, scrape_log.csv} (tidak di-commit)."""
import argparse
import datetime as dt
import json
import random
import re
import sys
import time
import urllib.robotparser
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from common import RAW_DIR  # noqa: E402

BASE = "https://id.jobstreet.com"
KEYWORDS = ["data-analyst", "business-intelligence-analyst", "analis-data"]
USER_AGENT = "portfolio-job-market-study (kontak: lihat profil GitHub bagusbernadi)"
HAS_DATA, HAS_ROLE, EXCLUDE = r"data|business intelligence|\bBI\b|analytics|insight", r"analyst|analytic|analis|intelligence|\bBI\b", r"engineer|master data|library|support officer|scientist"


def allowed(path):
    rp = urllib.robotparser.RobotFileParser(BASE + "/robots.txt")
    rp.read()
    return rp.can_fetch(USER_AGENT, BASE + path)


def extract_jobs(html):
    marker = "window.SEEK_REDUX_DATA = "
    start = html.find(marker)
    if start == -1:
        return []
    data, _ = json.JSONDecoder().raw_decode(html, start + len(marker))
    jobs = {}

    def walk(o):
        if isinstance(o, dict):
            if "companyName" in o and "listingDate" in o and "id" in o:
                jobs[o["id"]] = o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    rows = []
    for j in jobs.values():
        loc, cls, wt = (j.get("locations") or [{}])[0], (j.get("classifications") or [{}])[0], j.get("workTypes")
        rows.append(dict(id=str(j["id"]), title=j.get("title"), company=j.get("companyName"), location=loc.get("label"), salary=j.get("salaryLabel"),
                         category=cls.get("subclassification", {}).get("description"), work_type=", ".join(wt) if isinstance(wt, list) else wt,
                         listing_date=j.get("listingDate"), teaser=j.get("teaser")))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=5)
    ap.add_argument("--delay", type=float, nargs=2, default=(6, 12), help="jeda acak antar permintaan (detik)")
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    day = dt.date.today().isoformat()
    out = RAW_DIR / f"batch_{day}"
    out.mkdir(parents=True, exist_ok=True)
    log = []
    for p in ("/id/data-analyst-jobs", "/id/job/1"):
        if not allowed(p):
            sys.exit(f"robots.txt melarang {p}; batch dibatalkan")
    seen = {}
    with sync_playwright() as pw:
        page = pw.chromium.launch(headless=True).new_page()

        def get(url, tag):
            for t in range(a.retries + 1):
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(4000)
                    log.append(dict(url=url, tag=tag, attempt=t + 1, status="ok", at=dt.datetime.now().isoformat(timespec="seconds")))
                    return True
                except Exception as e:                                   # coba ulang dengan jeda lebih panjang
                    log.append(dict(url=url, tag=tag, attempt=t + 1, status=type(e).__name__, at=dt.datetime.now().isoformat(timespec="seconds")))
                    time.sleep(random.uniform(*a.delay) * (t + 2))
            return False

        for kw in KEYWORDS:
            for n in range(1, a.max_pages + 1):
                url = f"{BASE}/id/{kw}-jobs" + (f"?page={n}" if n > 1 else "")
                if not get(url, "list"):
                    break
                rows = extract_jobs(page.content())
                new = [r for r in rows if r["id"] not in seen]
                seen.update({r["id"]: r for r in new})
                if not rows or not new:
                    break
                time.sleep(random.uniform(*a.delay))
        df = pd.DataFrame(list(seen.values()))
        t = df["title"].fillna("")
        target = df[t.str.contains(HAS_DATA, case=False, regex=True) & t.str.contains(HAS_ROLE, case=False, regex=True) & ~t.str.contains(EXCLUDE, case=False, regex=True)].copy()
        target["scraped_at"] = day
        target.to_csv(out / "jobs_target_all.csv", index=False, encoding="utf-8-sig")
        det = []
        for r in target.itertuples():
            if not get(f"{BASE}/id/job/{r.id}", "detail"):
                break
            el = page.query_selector('[data-automation="jobAdDetails"]')
            if el is None:
                log.append(dict(url=r.id, tag="detail", attempt=1, status="selector_tidak_ketemu", at=dt.datetime.now().isoformat(timespec="seconds")))
                break
            det.append(dict(id=r.id, description=el.inner_text(), scraped_at=day))
            time.sleep(random.uniform(*a.delay))
        pd.DataFrame(det).to_csv(out / "jobs_detail.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(log).to_csv(out / "scrape_log.csv", index=False)
    print(f"batch {day}: {len(target)} lowongan target, {len(det)} deskripsi, {sum(l['status'] != 'ok' for l in log)} permintaan gagal")


if __name__ == "__main__":
    main()
