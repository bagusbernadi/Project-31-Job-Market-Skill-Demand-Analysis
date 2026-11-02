"""Dashboard 4 halaman (Ringkasan, Skill, Salary & Lokasi, Skill Match). Data: results/3-presentation/dash_rows.csv dan CSV hasil.
Jalankan dari folder project/:  streamlit run code/3-presentation/streamlit/app.py"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
SKILLS = ["Excel", "Google Sheets", "SQL", "BigQuery", "Python", "R", "VBA/Macro", "Power BI", "Tableau", "Looker Studio", "Dashboard", "ETL", "Spark", "Statistik", "Machine Learning"]
NON_TOOL = {"Dashboard"}


@st.cache_data
def load():
    d = pd.read_csv(RES / "3-presentation" / "dash_rows.csv")
    return d, pd.read_csv(RES / "2-analysis" / "skill_match_scenarios.csv"), pd.read_csv(RES / "2-analysis" / "skill_next.csv")


d, scen, nxt = load()
st.set_page_config(page_title="Pasar kerja Data Analyst", layout="wide")
st.title("Project 31: Job Market & Skill Demand")
st.caption("Data: 48 lowongan unik Jobstreet (satu kali ambil, Oktober 2026). Sampel kecil, bukan statistik pasar kerja.")
with st.sidebar:
    page = st.radio("Halaman", ["Ringkasan", "Skill", "Salary & Lokasi", "Skill Match"])
    weeks = sorted(d.week_start.unique())
    w = st.select_slider("Minggu tayang (dari - sampai)", options=weeks, value=(weeks[0], weeks[-1]))
    kota = st.multiselect("Kota", sorted(d.city.unique()))
    level = st.multiselect("Level", sorted(d.level.unique()))
    ind = st.multiselect("Bidang kerja (pengganti industri)", sorted(d.industry.unique()))
f = d[(d.week_start >= w[0]) & (d.week_start <= w[1])]
if kota:
    f = f[f.city.isin(kota)]
if level:
    f = f[f.level.isin(level)]
if ind:
    f = f[f.industry.isin(ind)]
n = len(f)
if n == 0:
    st.warning("Tidak ada lowongan untuk filter ini.")
    st.stop()
share = (f[SKILLS].sum() / n).sort_values(ascending=False)

if page == "Ringkasan":
    c = st.columns(4)
    c[0].metric("Lowongan", n)
    c[1].metric("3 skill teratas", ", ".join(share.index[:3]))
    top_city = f.city.value_counts()
    c[2].metric("Kota teratas", f"{top_city.index[0]} ({top_city.iloc[0]})")
    c[3].metric("Cantumkan salary", f"{f.salary_min.notna().mean():.0%}")
    wk = f.groupby("week_start").size().reset_index(name="lowongan")
    st.plotly_chart(px.bar(wk, x="week_start", y="lowongan", title="Lowongan per minggu tayang (bukan tren: satu kali ambil)"), width="stretch")
elif page == "Skill":
    st.plotly_chart(px.bar(share.reset_index().rename(columns={"index": "skill", 0: "share"}).set_axis(["skill", "share"], axis=1).iloc[::-1], x="share", y="skill", orientation="h",
                           title=f"% lowongan yang menyebut skill (n = {n})").update_xaxes(tickformat=".0%"), width="stretch")
elif page == "Salary & Lokasi":
    s = f[f.salary_min.notna()]
    st.write(f"Lowongan dengan salary: {len(s)} dari {n}. Median salary hanya mewakili lowongan yang mencantumkannya.")
    if len(s):
        st.plotly_chart(px.scatter(s, x="salary_min", y="salary_max", color="city", hover_data=["industry", "level"], title="Rentang salary per bulan (Rp)"), width="stretch")
    st.dataframe(f.groupby("city").agg(lowongan=("city", "size"), dengan_salary=("salary_min", "count"), median_min=("salary_min", "median")).sort_values("lowongan", ascending=False))
else:
    st.write("Skill match (estimated): lowongan yang semua skill tool-nya dimiliki. Pilih skill yang Anda kuasai.")
    own = st.multiselect("Skill dikuasai", [s for s in SKILLS if s not in NON_TOOL], default=["Excel", "SQL", "Python"])
    k = st.slider("Boleh kurang berapa skill", 0, 3, 0)
    req = f[[s for s in SKILLS if s not in NON_TOOL]].apply(lambda r: {s for s in r.index if r[s] == 1}, axis=1)
    miss = req.apply(lambda r: len(r - set(own)))
    st.metric("Lowongan bisa dilamar", f"{int((miss <= k).sum())} dari {n} ({(miss <= k).mean():.0%})")
    gains = {s: int(req.apply(lambda r: len(r - set(own) - {s}) <= k).sum()) - int((miss <= k).sum()) for s in [x for x in SKILLS if x not in NON_TOOL and x not in own]}
    g = pd.Series(gains).sort_values(ascending=False)
    st.write("Skill berikutnya yang paling menambah peluang:")
    st.dataframe(g.rename("tambahan lowongan").head(5))
