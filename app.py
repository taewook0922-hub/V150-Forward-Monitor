import os
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="V150 Forward Monitor", page_icon="📈", layout="wide")
root=Path(os.getenv("V150_ROOT","/content/drive/MyDrive/AutomaticTrading/V150_2"))
st.title("📈 V150 Forward Monitor")
st.caption("Forward-test dashboard · strategy parameters are read-only")
summary_path=root/"V150_RESULTS"/"V150_2_forward_summary.csv"
trades_path=root/"V150_RESULTS"/"V150_2_forward_trades.csv"
history_path=root/"V150_AUDIT"/"V150_2_run_history.csv"
if not summary_path.exists():
    st.warning("V150.2 결과 파일을 찾지 못했습니다.")
    st.code(str(summary_path))
    st.info("먼저 V150.2를 실행해 Google Drive에 결과를 저장하세요.")
    st.stop()
summary=pd.read_csv(summary_path)
a,b,c,d=st.columns(4)
a.metric("Holdout bars",int(summary.groupby("Symbol")["HoldoutBars"].max().sum()))
b.metric("Closed trades",int(summary["ClosedTrades"].sum()))
c.metric("Open trades",int(summary["OpenTrades"].sum()))
d.metric("Tracked symbols",int(summary["Symbol"].nunique()))
st.subheader("전략 현황")
st.dataframe(summary,use_container_width=True,hide_index=True)
if trades_path.exists():
    trades=pd.read_csv(trades_path)
    st.subheader("거래 기록")
    if len(trades):
        st.dataframe(trades.sort_values("EntryTime",ascending=False),use_container_width=True,hide_index=True)
    else:
        st.info("아직 Forward 거래가 없습니다.")
if history_path.exists():
    history=pd.read_csv(history_path)
    st.subheader("Forward Test 누적 기록")
    st.dataframe(history.tail(30).iloc[::-1],use_container_width=True,hide_index=True)
st.divider()
st.caption(f"Data root: {root}")
st.caption("BASE_FIXED_2_ATR vs FROZEN_T1_5_L0_75 · monitoring only")
