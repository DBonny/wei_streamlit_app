from __future__ import annotations
import streamlit as st
import pandas as pd
from utils.ui import CCY_OPTIONS, HORIZONS, mobile_css, render_perf_table
from utils.data import (
    today, INDICES, ytd_default_window, compute_table, ret_custom, REGION
)

st.set_page_config(page_title="Performance Dashboard", page_icon="📊", layout="wide")
mobile_css()  # padding/legibilità migliori su schermi piccoli

st.header("Performance Dashboard")
st.write("Tabella dei rendimenti per indice, con valuta selezionabile e finestra **Custom**.")

# ---- Toggle 'Modalità mobile' (ti permette di forzare la vista anche da desktop)
with st.sidebar:
    is_mobile = st.toggle("Modalità mobile", value=True, help="Interfaccia più compatta e leggibile su smartphone.")

# --- Controls
if is_mobile:
    # Stack verticale: più spazio al contenuto
    target_ccy = st.selectbox("Valuta", CCY_OPTIONS, index=1)
    s_def, e_def = ytd_default_window()
    start_custom = st.date_input("Custom start", value=s_def.date(), format="YYYY-MM-DD")
    end_custom   = st.date_input("Custom end", value=e_def.date(), format="YYYY-MM-DD")
    region_filter = st.selectbox("Regione", ["Tutte","Americas","Europe","AsiaPac","LatAm","Global","Other"])
    colA, colB = st.columns([1,1])
    with colA:
        sort_by = st.selectbox("Ordina per", ["— nessuno —"] + HORIZONS + ["Custom"])
    with colB:
        ascending = st.toggle("Ordine crescente", value=False)
else:
    c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.1, 1.1, 1.1, 1.1, 1.4])
    target_ccy = c1.selectbox("Valuta", CCY_OPTIONS, index=1)
    s_def, e_def = ytd_default_window()
    start_custom = c2.date_input("Custom start", value=s_def.date(), format="YYYY-MM-DD")
    end_custom   = c3.date_input("Custom end", value=e_def.date(), format="YYYY-MM-DD")
    region_filter = c4.selectbox("Regione", ["Tutte","Americas","Europe","AsiaPac","LatAm","Global","Other"])
    sort_by = c5.selectbox("Ordina per", ["— nessuno —"] + HORIZONS + ["Custom"])
    ascending = (c6.toggle("Ordine crescente", value=False))

st.caption(f"As of: **{today.date()}**")

# --- Compute
with st.spinner("Calcolo performance..."):
    df, conv_px = compute_table(target_ccy)

# Colonna Custom
custom_vals = []
for name in df.index:
    r = ret_custom(conv_px.get(name, pd.Series(dtype=float)), start_custom, end_custom)
    custom_vals.append(None if r is None else round(r, 2))
df["Custom"] = custom_vals

# Region + ordering per blocchi
df.insert(0, "Region", [REGION.get(ix, "Other") for ix in df.index])
order = {"Americas":0, "Europe":1, "AsiaPac":2, "LatAm":3, "Global":4, "Other":9}
df["_ord"] = df["Region"].map(order).fillna(9)
df = df.sort_values(by=["_ord", "Index"]).drop(columns="_ord")

# Filtro regione
if region_filter and region_filter != "Tutte":
    df = df[df["Region"] == region_filter]

# Ordinamento colonna
if sort_by in (HORIZONS + ["Custom"]):
    df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")

st.markdown(f"**Performance convertite in**: `{('Valuta locale (nessuna conversione)' if target_ccy=='LOCAL' else target_ccy)}`")

# --- RENDER: desktop = Styler, mobile = dataframe scrollabile
render_perf_table(df, HORIZONS + ["Custom"], mobile=is_mobile)

st.divider()
st.page_link("app.py", label="⬅️ Torna alla Home")
