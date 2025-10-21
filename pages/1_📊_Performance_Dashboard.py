from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.ui import CCY_OPTIONS, HORIZONS, REGION, style_perf_df
from utils.data import (
    today, INDICES,
    ytd_default_window, compute_table,
    ret_custom
)

st.set_page_config(page_title="Performance Dashboard", page_icon="📊", layout="wide")

st.header("Performance Dashboard")
st.write("Tabella dei rendimenti per indice, con valuta selezionabile e finestra **Custom**.")

c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.1, 1.1, 1.1, 1.1, 1.4])
target_ccy = c1.selectbox("Valuta", CCY_OPTIONS, index=1)  # default USD
start_custom = c2.date_input("Custom start", value=None)
end_custom   = c3.date_input("Custom end", value=None)
region_filter = c4.selectbox("Regione", ["Tutte","Americas","Europe","AsiaPac","LatAm","Global"])
sort_by = c5.selectbox("Ordina per", ["— nessuno —"] + HORIZONS + ["Custom"])
ascending = (c6.toggle("Ordine crescente", value=False))

st.caption(f"As of: **{today.date()}**")

with st.spinner("Calcolo performance..."):
    df, conv_px = compute_table(target_ccy)

custom_vals = []
for name in df.index:
    r = ret_custom(conv_px.get(name, pd.Series(dtype=float)), start_custom, end_custom)
    custom_vals.append(None if r is None else round(r, 2))
df["Custom"] = custom_vals

df.insert(0, "Region", [REGION.get(ix, "Other") for ix in df.index])
if region_filter and region_filter != "Tutte":
    df = df[df["Region"] == region_filter]

if sort_by in (HORIZONS + ["Custom"]):
    df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")

st.markdown(f"**Performance convertite in**: `{('Valuta locale (nessuna conversione)' if target_ccy=='LOCAL' else target_ccy)}`")

styled = style_perf_df(df, HORIZONS + ["Custom"])
st.write(styled)

st.divider()
st.page_link("app.py", label="⬅️ Torna alla Home")
