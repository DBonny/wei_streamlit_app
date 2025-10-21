from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="WEI-like Market Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("WEI-like Market Dashboards")
st.markdown(
    '''
Benvenuto! Scegli quale dashboard aprire:

- **Performance Dashboard**: tabella con rendimenti multi-orizzonte (1D, 1W, MTD, YTD, 1Y, 3Y, 5Y) e finestra **Custom**.  
- **Comparison Dashboard**: grafico **rebased=100** per confrontare più indici e valute.

L’app è **responsive** e fruibile anche da smartphone.  
    '''
)

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/1_📊_Performance_Dashboard.py", label="Apri Performance Dashboard", icon="📊")
with col2:
    st.page_link("pages/2_📈_Comparison_Dashboard.py", label="Apri Comparison Dashboard", icon="📈")

st.divider()
st.caption("Suggerimento: salva questa pagina tra i preferiti per un accesso rapido 🚀")
