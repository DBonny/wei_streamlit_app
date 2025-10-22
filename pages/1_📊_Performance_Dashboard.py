from __future__ import annotations
import streamlit as st
import pandas as pd

# ⚠️ Import CORRETTI: REGION arriva da utils.data (non da utils.ui)
from utils.ui import CCY_OPTIONS, HORIZONS, style_perf_df
from utils.data import (
    today, INDICES, ytd_default_window, compute_table, ret_custom, REGION
)

st.set_page_config(page_title="Performance Dashboard", page_icon="📊", layout="wide")

st.header("Performance Dashboard")
st.write("Tabella dei rendimenti per indice, con valuta selezionabile e finestra **Custom**.")

# --- Controls (top row)
c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.1, 1.1, 1.1, 1.1, 1.4])
target_ccy = c1.selectbox("Valuta", CCY_OPTIONS, index=1)  # default USD

# Default Custom = YTD VISIBILE all'utente
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

# Colonna Custom (usa i date-picker visibili)
custom_vals = []
for name in df.index:
    r = ret_custom(conv_px.get(name, pd.Series(dtype=float)), start_custom, end_custom)
    custom_vals.append(None if r is None else round(r, 2))
df["Custom"] = custom_vals

# Aggiungi Region
df.insert(0, "Region", [REGION.get(ix, "Other") for ix in df.index])

# Ordine blocchi per regione (serve per i separatori)
order = {"Americas":0, "Europe":1, "AsiaPac":2, "LatAm":3, "Global":4, "Other":9}
df["_ord"] = df["Region"].map(order).fillna(9)
df = df.sort_values(by=["_ord", "Index"]).drop(columns="_ord")

# Filtro regione
if region_filter and region_filter != "Tutte":
    df = df[df["Region"] == region_filter]

# Ordinamento per metrica, opzionale
if sort_by in (HORIZONS + ["Custom"]):
    df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")

st.markdown(f"**Performance convertite in**: `{('Valuta locale (nessuna conversione)' if target_ccy=='LOCAL' else target_ccy)}`")

# --- Rendering tabella con fallback sicuro
try:
    styled = style_perf_df(df, HORIZONS + ["Custom"])
    st.write(styled)
except Exception as e:
    st.warning(f"Rendering avanzato non disponibile: uso visualizzazione semplice. Dettagli: {e}")
    df_show = df.copy()
    for c in HORIZONS + ["Custom"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "")
    st.dataframe(df_show, use_container_width=True)

st.divider()
st.page_link("app.py", label="⬅️ Torna alla Home")

# (Facoltativa) mini-diagnostica versioni in sidebar
with st.sidebar:
    st.subheader("Diagnostica")
    import sys, pandas as _pd, plotly as _pl
    try:
        import matplotlib
        mpl_ver = matplotlib.__version__
    except Exception:
        mpl_ver = "non installato"
    st.write({
        "Python": sys.version.split()[0],
        "pandas": _pd.__version__,
        "plotly": _pl.__version__,
        "matplotlib": mpl_ver,
    })