from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="V150.2 Forward Monitor", page_icon="📈", layout="wide")
st.title("📈 V150.2 Forward Monitor")
st.caption("Forward Test 전용 · 전략 파라미터는 변경하지 않습니다.")

DATA = Path(".")
SUMMARY = DATA / "V150_2_forward_summary.csv"
TRADES = DATA / "V150_2_forward_trades.csv"
HISTORY = DATA / "V150_2_run_history.csv"

with st.sidebar:
    st.header("데이터")
    st.caption("Colab의 V150.2 결과 CSV를 아래에 올리면 바로 갱신됩니다.")
    files = st.file_uploader(
        "CSV 업로드",
        type=["csv"],
        accept_multiple_files=True,
        help="summary / trades / run_history CSV를 한 번에 선택하세요."
    )
    st.caption("업로드하지 않으면 프로젝트의 data 폴더를 자동 확인합니다.")

uploaded = {f.name: f for f in files} if files else {}

def read_csv(name, path):
    if name in uploaded:
        return pd.read_csv(uploaded[name])
    if path.exists():
        return pd.read_csv(path)
    return None

summary = read_csv("V150_2_forward_summary.csv", SUMMARY)
trades = read_csv("V150_2_forward_trades.csv", TRADES)
history = read_csv("V150_2_run_history.csv", HISTORY)

if summary is None:
    st.info("V150.2 결과를 기다리는 중입니다.")
    st.markdown("""
**처음 사용할 때**
1. Colab에서 V150.2를 실행합니다.
2. Google Drive → `AutomaticTrading/V150_2/V150_RESULTS`에서  
   `V150_2_forward_summary.csv`, `V150_2_forward_trades.csv`를 선택합니다.
3. `V150_AUDIT`에서 `V150_2_run_history.csv`도 선택하면 누적 기록까지 표시됩니다.
4. 왼쪽 **CSV 업로드**에 파일들을 한 번에 넣습니다.
""")
    st.stop()

required = {"Symbol","ExitMode","HoldoutBars","ClosedTrades","Wins","Losses",
            "ClosedReturnPct","PF","MDDPct","OpenTrades"}
missing = required - set(summary.columns)
if missing:
    st.error("summary CSV에 필요한 열이 없습니다: " + ", ".join(sorted(missing)))
    st.stop()

closed = int(summary["ClosedTrades"].fillna(0).sum())
wins = int(summary["Wins"].fillna(0).sum())
open_trades = int(summary["OpenTrades"].fillna(0).sum())
holdout = int(summary.groupby("Symbol")["HoldoutBars"].max().sum())
winrate = (wins / closed * 100) if closed else 0.0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Holdout bars", f"{holdout:,}")
c2.metric("Closed trades", f"{closed:,}")
c3.metric("Open trades", f"{open_trades:,}")
c4.metric("Win rate", f"{winrate:.1f}%")
c5.metric("Symbols", int(summary["Symbol"].nunique()))

st.subheader("전략 비교")
show = summary.copy()
for col in ["ClosedReturnPct","PF","MDDPct"]:
    show[col] = pd.to_numeric(show[col], errors="coerce")
st.dataframe(show, use_container_width=True, hide_index=True)

modes = list(summary["ExitMode"].dropna().unique())
if modes:
    chart = summary.pivot_table(index="Symbol", columns="ExitMode",
                                values="ClosedReturnPct", aggfunc="first")
    if not chart.empty:
        st.subheader("종목별 Forward 수익률 (%)")
        st.bar_chart(chart)

st.subheader("Forward 진행 상태")
target = 30
progress = min(closed / target, 1.0)
st.progress(progress)
if closed < target:
    st.caption(f"1차 점검 기준 30건까지 {target-closed}건 남았습니다. 기간보다 거래 표본 수를 우선 확인합니다.")
else:
    st.success("1차 점검 기준인 30건 이상의 종료 거래가 쌓였습니다.")

if trades is not None:
    st.subheader("거래 기록")
    if trades.empty:
        st.info("아직 Forward 거래가 없습니다.")
    else:
        if "EntryTime" in trades.columns:
            trades = trades.sort_values("EntryTime", ascending=False)
        st.dataframe(trades, use_container_width=True, hide_index=True)

if history is not None:
    st.subheader("실행 기록")
    if history.empty:
        st.info("아직 실행 기록이 없습니다.")
    else:
        if "RunUTC" in history.columns:
            history["RunUTC"] = pd.to_datetime(history["RunUTC"], errors="coerce")
            history = history.sort_values("RunUTC")
        st.dataframe(history.tail(50).iloc[::-1], use_container_width=True, hide_index=True)
        cols = [c for c in ["BaseAvgReturnPct","CandidateAvgReturnPct"] if c in history.columns]
        if cols and "RunUTC" in history.columns:
            plot = history.set_index("RunUTC")[cols]
            st.subheader("Forward 수익률 변화")
            st.line_chart(plot)

st.divider()
st.caption("V150.2 · BASE_FIXED_2_ATR vs FROZEN_T1_5_L0_75 · Monitoring only")
