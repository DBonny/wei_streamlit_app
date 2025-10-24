from __future__ import annotations
import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from utils.ui import CCY_OPTIONS, HORIZONS
from utils.data import (
    INDICES, build_series_rebased, today
)

st.set_page_config(page_title="Comparison Dashboard", page_icon="📈", layout="wide")

st.header("Comparison Dashboard")
st.write("Confronta indici con **rebased=100** su finestra selezionabile e valuta target.")

left, right = st.columns([1, 1])
with left:
    indices = st.multiselect(
        "Seleziona indici",
        options=list(INDICES.keys()),
        default=["S&P 500", "Euro Stoxx 50", "DAX (Germany)"],
        help="Puoi selezionarne più di uno."
    )
    target_ccy = st.selectbox("Valuta", CCY_OPTIONS, index=1)  # default USD
with right:
    horizon = st.selectbox("Orizzonte", HORIZONS, index=4)  # default 1Y
    scrollzoom = st.toggle("Zoom con rotella", value=False)
    fullscreen = st.toggle("Schermo intero", value=False)

if not indices:
    st.info("Seleziona almeno un indice.")
else:
    with st.spinner("Creo il grafico..."):
        df = build_series_rebased(indices, target_ccy, horizon)

    if df is None or df.empty:
        st.warning("Nessun dato disponibile per la combinazione scelta.")
    else:
        width, height = (1100, 600) if not fullscreen else (1400, 800)
        # Se attiva la Modalità mobile dalla sidebar della Performance, usa parametri più compatti:
        try:
            from utils.ui import mobile_css
            # h mobile tipico
            height = 420 if not fullscreen else 560
        except Exception:
            pass

        fig = px.line(
            df, x=df.index, y=df.columns,
            labels={"value": f"Indice (base=100) in {target_ccy}", "x": ""},
            title=f"Rebased {horizon} — Valuta {target_ccy}"
        )
        fig.update_layout(
            autosize=True,
            height=height,
            font=dict(size=13),
            legend_title_text="",
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified",
            margin=dict(l=10, r=10, t=46, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"])],
            showgrid=True, gridcolor="LightGray",
            tickfont=dict(size=10), title=None
        )
        fig.update_yaxes(showgrid=True, gridcolor="LightGray", tickfont=dict(size=10))
        fig.update_traces(connectgaps=True)

        config = {
            "displaylogo": False,
            "scrollZoom": bool(scrollzoom),
            "modeBarButtonsToRemove": ["toggleSpikelines","lasso2d","select2d"],
            "displayModeBar": False,       # 🔹 nasconde la toolbar su mobile, più spazio
            "responsive": True
        }
        st.plotly_chart(fig, use_container_width=True, config=config)


st.divider()
st.page_link("app.py", label="⬅️ Torna alla Home")
