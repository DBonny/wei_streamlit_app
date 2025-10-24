from __future__ import annotations
import pandas as pd
import streamlit as st

HORIZONS = ["1D", "1W", "MTD", "YTD", "1Y", "3Y", "5Y"]
HARD = ["USD", "EUR", "GBP", "JPY", "CHF"]
CCY_OPTIONS = ["LOCAL"] + HARD

# Nota: REGION viene letto da utils.data nelle pagine

def mobile_css():
    """Compatta padding e migliora leggibilità su schermi < 640px."""
    st.markdown("""
    <style>
    @media (max-width: 640px){
      .block-container{padding:0.6rem 0.6rem;}
      .stMarkdown p{margin-bottom:.4rem;}
      .stDataFrame{font-size:0.90rem;}
      .element-container:has(.stSelectbox), 
      .element-container:has(.stDateInput), 
      .element-container:has(.stToggle){
        margin-bottom:.35rem;
      }
    }
    </style>
    """, unsafe_allow_html=True)

def style_perf_df(df: pd.DataFrame, num_cols: list[str]) -> "pd.io.formats.style.Styler":
    """Styler con percentuali, heatmap e separatore tra regioni (desktop)."""
    fmt = {c: "{:+.2f}%" for c in num_cols}
    sty = (df.style
           .format(fmt)
           .background_gradient(subset=num_cols, cmap="RdYlGn", vmin=-10, vmax=10)
           .set_properties(subset=["Region","Local CCY"], **{"text-align":"left", "font-weight":"600"})
           .set_properties(subset=num_cols, **{"text-align":"right"}))

    def _apply_separators(data: pd.DataFrame):
        styles = pd.DataFrame("", index=data.index, columns=data.columns)
        prev = None
        for i, (idx, row) in enumerate(data.iterrows()):
            cur = row.get("Region", None)
            if i == 0 or cur != prev:
                styles.loc[idx, :] = "border-top: 3px solid #9aa0a6;"
            prev = cur
        return styles

    return sty.apply(_apply_separators, axis=None)

def render_perf_table(df: pd.DataFrame, num_cols: list[str], mobile: bool):
    """
    Desktop: Styler (colori + separatori).
    Mobile:  DataFrame scrollabile e più leggibile.
    """
    if not mobile:
        st.write(style_perf_df(df, num_cols))
        return

    # Mobile: converti le colonne % in stringhe formattate, usa st.dataframe
    df_show = df.copy()
    for c in num_cols:
        if c in df_show.columns:
            df_show[c] = df_show[c].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "")
    st.dataframe(df_show, use_container_width=True, hide_index=False)

