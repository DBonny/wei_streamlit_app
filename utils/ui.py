from __future__ import annotations
import pandas as pd

HORIZONS = ["1D", "1W", "MTD", "YTD", "1Y", "3Y", "5Y"]
HARD = ["USD", "EUR", "GBP", "JPY", "CHF"]
CCY_OPTIONS = ["LOCAL"] + HARD

# Nota: REGION viene letto da utils.data nelle pagine (qui lo lasciamo vuoto per tip hints)
REGION = {}

def style_perf_df(df: pd.DataFrame, num_cols: list[str]) -> "pd.io.formats.style.Styler":
    """
    Restituisce un pandas Styler con:
    - formattazione percentuale
    - heatmap RdYlGn sulle colonne numeriche
    - separatore (bordo spesso) all'inizio di ogni blocco Region
    """
    fmt = {c: "{:+.2f}%" for c in num_cols}

    sty = (df.style
           .format(fmt)
           .background_gradient(subset=num_cols, cmap="RdYlGn", vmin=-10, vmax=10)
           .set_properties(subset=["Region","Local CCY"], **{"text-align":"left", "font-weight":"600"})
           .set_properties(subset=num_cols, **{"text-align":"right"}))

    # Separatore visivo tra regioni (bordo top spesso)
    def _apply_separators(data: pd.DataFrame):
        styles = pd.DataFrame("", index=data.index, columns=data.columns)
        prev = None
        for i, (idx, row) in enumerate(data.iterrows()):
            cur = row.get("Region", None)
            if i == 0 or cur != prev:
                styles.loc[idx, :] = "border-top: 3px solid #9aa0a6;"  # linea marcata
            prev = cur
        return styles

    return sty.apply(_apply_separators, axis=None)
