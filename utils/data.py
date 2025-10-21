from __future__ import annotations
import pandas as pd
import numpy as np
import yfinance as yf
from functools import lru_cache
from pandas.tseries.offsets import BDay
import streamlit as st

today = pd.Timestamp.today().normalize()

HORIZONS = ["1D", "1W", "MTD", "YTD", "1Y", "3Y", "5Y"]
HARD = ["USD", "EUR", "GBP", "JPY", "CHF"]
CCY_OPTIONS = ["LOCAL"] + HARD

INDICES: dict[str, tuple[str, str]] = {
    "S&P 500": ("^GSPC","USD"), "Dow Jones": ("^DJI","USD"),
    "Nasdaq 100": ("^NDX","USD"), "Russell 2000": ("^RUT","USD"),
    "S&P/TSX Composite (Canada)": ("^GSPTSE","CAD"),
    "STOXX Europe 600": ("^STOXX","EUR"), "Euro Stoxx 50": ("^STOXX50E","EUR"),
    "DAX (Germany)": ("^GDAXI","EUR"), "CAC 40 (France)": ("^FCHI","EUR"),
    "FTSE 100 (UK)": ("^FTSE","GBP"), "FTSE MIB (Italy)": ("FTSEMIB.MI","EUR"),
    "IBEX 35 (Spain)": ("^IBEX","EUR"), "AEX (Netherlands)": ("^AEX","EUR"),
    "SMI (Switzerland)": ("^SSMI","CHF"),
    "OMX Stockholm 30": ("^OMX","SEK"), "OMX Copenhagen 25": ("^OMXC25","DKK"),
    "Nikkei 225 (Japan)": ("^N225","JPY"), "Shenzhen (China)": ("399001.SZ","CNY"),
    "Hang Seng (Hong Kong)": ("^HSI","HKD"), "TAIEX (Taiwan)": ("^TWII","TWD"),
    "KOSPI (Korea)": ("^KS11","KRW"), "S&P/ASX 200 (Australia)": ("^AXJO","AUD"),
    "Ibovespa (Brazil)": ("^BVSP","BRL"), "IPC Mexico": ("^MXX","MXN"),
    "MSCI World (USD)": ("URTH", "USD"),
    "MSCI Emerging Markets (USD)": ("EEM", "USD"),
}

REGION = {
    **{k:"Americas" for k in ["S&P 500","Dow Jones","Nasdaq 100","Russell 2000","S&P/TSX Composite (Canada)"]},
    **{k:"Europe"   for k in ["STOXX Europe 600","Euro Stoxx 50","DAX (Germany)","CAC 40 (France)","FTSE 100 (UK)",
                              "FTSE MIB (Italy)","IBEX 35 (Spain)","AEX (Netherlands)","SMI (Switzerland)"]},
    **{k:"AsiaPac"  for k in ["Nikkei 225 (Japan)","Shenzhen (China)","Hang Seng (Hong Kong)","TAIEX (Taiwan)",
                              "KOSPI (Korea)","S&P/ASX 200 (Australia)"]},
    **{k:"LatAm"    for k in ["Ibovespa (Brazil)","IPC Mexico"]},
    **{k:"Global"   for k in ["MSCI World (USD)","MSCI Emerging Markets (USD)"]},
}

def period_start(h: str) -> pd.Timestamp | None:
    if h == "1D": return None
    if h == "1W": return today - pd.DateOffset(weeks=1)
    if h == "MTD": return pd.Timestamp(today.year, today.month, 1)
    if h == "YTD": return pd.Timestamp(today.year, 1, 1)
    if h == "1Y": return today - pd.DateOffset(years=1)
    if h == "3Y": return today - pd.DateOffset(years=3)
    if h == "5Y": return today - pd.DateOffset(years=5)
    return today - pd.DateOffset(years=1)

def ytd_default_window() -> tuple[pd.Timestamp, pd.Timestamp]:
    return (pd.Timestamp(today.year, 1, 1) - BDay(1)).normalize(), today

def _ensure_series1d(x: pd.Series | pd.DataFrame) -> pd.Series:
    if isinstance(x, pd.DataFrame):
        if x.shape[1] >= 1: x = x.iloc[:,0]
        else: return pd.Series(dtype=float)
    s = x.copy()
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return pd.to_numeric(s, errors="coerce").astype(float)

@st.cache_data(show_spinner=False, ttl=60*60)
def fetch_series(ticker: str, start_str: str | pd.Timestamp) -> pd.Series:
    start = pd.to_datetime(start_str)
    df = yf.download(ticker, start=start, end=today + pd.Timedelta(days=1),
                     interval="1d", auto_adjust=False, progress=False)
    if df.empty: return pd.Series(dtype=float)
    s = df["Adj Close"] if "Adj Close" in df.columns else df["Close"]
    return _ensure_series1d(s).dropna()

@st.cache_data(show_spinner=False, ttl=60*60)
def usd_per_ccy(ccy: str, start_str: str | pd.Timestamp) -> pd.Series:
    start = pd.to_datetime(start_str)
    if ccy == "USD":
        return pd.Series(1.0, index=pd.date_range(start=start, end=today, freq="B"))
    df = yf.download(f"{ccy}USD=X", start=start, end=today + pd.Timedelta(days=1),
                     interval="1d", auto_adjust=False, progress=False)
    if not df.empty and "Close" in df: s = df["Close"]
    else:
        df2 = yf.download(f"USD{ccy}=X", start=start, end=today + pd.Timedelta(days=1),
                          interval="1d", auto_adjust=False, progress=False)
        if df2.empty or "Close" not in df2: return pd.Series(dtype=float)
        s = 1.0/df2["Close"]
    return _ensure_series1d(s).dropna()

def build_fx_map(needed_ccys: list[str], start: pd.Timestamp) -> dict[str, pd.Series]:
    ccys = sorted(set(needed_ccys) | set(HARD))
    return {c: usd_per_ccy(c, start) for c in ccys}

def convert_series(series_local: pd.Series | pd.DataFrame, local_ccy: str, target_ccy: str,
                   fx_map: dict[str, pd.Series]) -> pd.Series:
    s_loc = _ensure_series1d(series_local).dropna()
    if target_ccy == "LOCAL" or target_ccy == local_ccy: return s_loc
    usd_local  = _ensure_series1d(fx_map.get(local_ccy, pd.Series(dtype=float)))
    usd_target = _ensure_series1d(fx_map.get(target_ccy, pd.Series(dtype=float)))
    return _ensure_series1d(s_loc * (usd_local.reindex(s_loc.index).ffill()
                                     / usd_target.reindex(s_loc.index).ffill())).dropna()

def _prev_close_before(s: pd.Series, dt: pd.Timestamp):
    s2 = s[s.index < dt];  return None if s2.empty else float(s2.iloc[-1])
def _last_close_on_or_before(s: pd.Series, dt: pd.Timestamp):
    s2 = s[s.index <= dt]; return None if s2.empty else float(s2.iloc[-1])

def pct_return(series: pd.Series | pd.DataFrame, horizon: str):
    s = _ensure_series1d(series).dropna()
    if s.empty: return None
    if horizon == "1D":
        if len(s) < 2: return None
        prev, last = s.iloc[-2], s.iloc[-1]
        if pd.isna(prev) or pd.isna(last) or prev <= 0: return None
        return (last/prev - 1.0)*100.0
    if horizon in ("MTD","YTD"):
        last = s.iloc[-1]
        start_dt = (pd.Timestamp(s.index[-1].year, s.index[-1].month, 1)
                    if horizon=="MTD" else pd.Timestamp(s.index[-1].year,1,1))
        base = _prev_close_before(s, start_dt)
        if base is None or base <= 0: return None
        return (last/base - 1.0)*100.0
    start = period_start(horizon); s2 = s[s.index >= start] if start is not None else s
    if s2.empty or s2.iloc[0] <= 0: return None
    return (s2.iloc[-1]/s2.iloc[0] - 1.0)*100.0

def ret_custom(series: pd.Series | pd.DataFrame, start_date, end_date):
    s = _ensure_series1d(series).dropna()
    if s.empty: return None
    if not start_date and not end_date:
        start_date, end_date = ytd_default_window()
    start = pd.Timestamp(start_date); end = pd.Timestamp(end_date)
    if start.month==12 and start.day==31 and end.year==start.year+1:
        start = pd.Timestamp(end.year,1,1)
    base = _prev_close_before(s, start); last = _last_close_on_or_before(s, end)
    if base is None or last is None or base <= 0: return None
    return (last/base - 1.0)*100.0

def compute_table(target_ccy: str):
    start_min = period_start("5Y") - pd.DateOffset(months=1)
    fx_map = {} if target_ccy=="LOCAL" else build_fx_map([ccy for _,ccy in INDICES.values()], start_min)
    rows, conv_px = [], {}
    for name,(tkr,lcy) in INDICES.items():
        px_local = fetch_series(tkr, start_min)
        if px_local.empty:
            rows.append({"Index":name,"Local CCY":lcy, **{h:None for h in HORIZONS}})
            continue
        px_conv = convert_series(px_local, lcy, target_ccy, fx_map)
        conv_px[name] = px_conv
        row = {"Index":name,"Local CCY":lcy}
        for h in HORIZONS:
            r = pct_return(px_conv, h); row[h] = None if r is None else round(r,2)
        rows.append(row)
    df = pd.DataFrame(rows).set_index("Index")
    return df, conv_px

def build_series_rebased(name_list: list[str], target_ccy: str, horizon: str) -> pd.DataFrame | None:
    start = period_start(horizon) or (today - pd.DateOffset(days=10))
    need_ccy = [INDICES[n][1] for n in name_list] if target_ccy != "LOCAL" else []
    fx_map = build_fx_map(need_ccy, start - pd.DateOffset(months=1)) if need_ccy else {}

    cols = {}
    for name in name_list:
        tkr, lcy = INDICES[name]
        s_local = fetch_series(tkr, start)
        s_tgt = s_local if target_ccy == "LOCAL" else convert_series(s_local, lcy, target_ccy, fx_map)
        s = _ensure_series1d(s_tgt).dropna()
        if s.empty: continue
        s = s[s.index >= (period_start(horizon) or s.index.min())]
        cols[name] = s

    if not cols: return None

    df = pd.concat(cols, axis=1).sort_index().ffill()
    base = df.apply(lambda s: s.dropna().iloc[0] if s.dropna().size else np.nan)
    df = (df / base) * 100.0
    return df
