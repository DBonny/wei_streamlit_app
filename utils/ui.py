from __future__ import annotations
import pandas as pd

HORIZONS = ["1D", "1W", "MTD", "YTD", "1Y", "3Y", "5Y"]
HARD = ["USD", "EUR", "GBP", "JPY", "CHF"]
CCY_OPTIONS = ["LOCAL"] + HARD

REGION = {}

def style_perf_df(df: pd.DataFrame, num_cols: list[str]) -> "pd.io.formats.style.Styler":
    fmt = {c: "{:+.2f}%" for c in num_cols}
    sty = (df.style
           .format(fmt)
           .background_gradient(subset=num_cols, cmap="RdYlGn", vmin=-10, vmax=10)
           .set_properties(subset=["Region","Local CCY"], **{"text-align":"left", "font-weight":"600"})
           .set_properties(subset=num_cols, **{"text-align":"right"}))
    return sty
