import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import yfinance as yf
from newsapi import NewsApiClient
import feedparser
import time

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="포트폴리오 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap');

/* Root Variables */
:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2234;
    --border: #1f2d45;
    --accent: #00d4aa;
    --accent2: #3b82f6;
    --accent3: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.main { background-color: var(--bg) !important; }
.block-container { padding-top: 1.5rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Metric Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.6rem; font-weight: 700; }
.metric-delta { font-size: 0.8rem; margin-top: 0.3rem; }
.delta-up { color: var(--accent); }
.delta-down { color: var(--danger); }

/* Section Headers */
.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* News Cards */
.news-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    cursor: pointer;
    transition: all 0.2s;
}
.news-card:hover { background: var(--surface2); border-left-color: var(--accent); }
.news-card.kr { border-left-color: #4ade80; }
.news-card.us { border-left-color: #60a5fa; }
.news-card.global { border-left-color: #f59e0b; }
.news-title { font-size: 0.88rem; font-weight: 500; line-height: 1.4; margin-bottom: 0.3rem; }
.news-meta { font-size: 0.72rem; color: var(--muted); display: flex; gap: 1rem; }
.news-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    margin-right: 0.4rem;
}
.badge-kr { background: rgba(74,222,128,0.15); color: #4ade80; }
.badge-us { background: rgba(96,165,250,0.15); color: #60a5fa; }
.badge-global { background: rgba(245,158,11,0.15); color: #f59e0b; }

/* Asset Rows */
.asset-row {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 0.4rem;
    transition: all 0.15s;
}
.asset-row:hover { background: var(--surface2); }
.asset-name { flex: 2; font-weight: 500; font-size: 0.9rem; }
.asset-ticker { flex: 1; font-family: 'Space Mono', monospace; font-size: 0.8rem; color: var(--muted); }
.asset-amount { flex: 1.5; font-family: 'Space Mono', monospace; font-size: 0.88rem; text-align: right; }
.asset-pnl { flex: 1; text-align: right; font-size: 0.85rem; font-weight: 600; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--muted) !important;
    font-size: 0.85rem;
    padding: 0.5rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #000 !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ─────────────────────────────────────────────────────
if "assets" not in st.session_state:
    st.session_state.assets = [
        {"name": "삼성전자", "ticker": "005930.KS", "type": "한국주식", "quantity": 50, "avg_price": 68000, "currency": "KRW"},
        {"name": "SK하이닉스", "ticker": "000660.KS", "type": "한국주식", "quantity": 20, "avg_price": 130000, "currency": "KRW"},
        {"name": "Apple", "ticker": "AAPL", "type": "미국주식", "quantity": 10, "avg_price": 175.0, "currency": "USD"},
        {"name": "NVIDIA", "ticker": "NVDA", "type": "미국주식", "quantity": 5, "avg_price": 480.0, "currency": "USD"},
        {"name": "KODEX 200", "ticker": "069500.KS", "type": "ETF", "quantity": 100, "avg_price": 28000, "currency": "KRW"},
        {"name": "현금(원화)", "ticker": "CASH_KRW", "type": "현금", "quantity": 1, "avg_price": 5000000, "currency": "KRW"},
        {"name": "현금(달러)", "ticker": "CASH_USD", "type": "현금", "quantity": 1, "avg_price": 3000, "currency": "USD"},
    ]

if "news_cache" not in st.session_state:
    st.session_state.news_cache = {"data": [], "fetched_at": None}

if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

# ── Helper Functions ────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_usd_krw():
    try:
        ticker = yf.Ticker("USDKRW=X")
        info = ticker.fast_info
        return float(info.last_price)
    except:
        return 1340.0

@st.cache_data(ttl=300)
def fetch_price(ticker: str):
    if ticker.startswith("CASH"):
        return None, None
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) >= 2:
            cur = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]
            chg = (cur - prev) / prev * 100
            return float(cur), float(chg)
        elif len(hist) == 1:
            cur = hist["Close"].iloc[-1]
            return float(cur), 0.0
        return None, None
    except:
        return None, None

@st.cache_data(ttl=600)
def fetch_rss_news(url: str, source: str, region: str, max_items: int = 6):
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:max_items]:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", "#"),
                "published": entry.get("published", ""),
                "source": source,
                "region": region,
            })
        return items
    except:
        return []

def get_all_news():
    feeds = [
        ("https://feeds.feedburner.com/businessinsider", "Business Insider", "us"),
        ("https://feeds.reuters.com/reuters/businessNews", "Reuters", "global"),
        ("https://www.ft.com/rss/home/korean", "Financial Times", "global"),
        ("https://rss.cnn.com/rss/money_news_international.rss", "CNN Money", "us"),
        ("https://www.investing.com/rss/news.rss", "Investing.com", "global"),
        ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "WSJ Markets", "us"),
    ]
    all_news = []
    for url, source, region in feeds:
        all_news.extend(fetch_rss_news(url, source, region, 4))
    return all_news

def calculate_portfolio(assets, usd_krw):
    rows = []
    total_krw = 0
    total_cost_krw = 0

    for a in assets:
        price, chg = fetch_price(a["ticker"])
        is_cash = a["ticker"].startswith("CASH")

        if is_cash:
            cur_price = a["avg_price"]
            chg = 0.0
        else:
            cur_price = price if price else a["avg_price"]

        val = a["quantity"] * cur_price
        cost = a["quantity"] * a["avg_price"]
        pnl = val - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0

        # Convert to KRW
        if a["currency"] == "USD":
            val_krw = val * usd_krw
            cost_krw = cost * usd_krw
        else:
            val_krw = val
            cost_krw = cost

        total_krw += val_krw
        total_cost_krw += cost_krw

        rows.append({
            "이름": a["name"],
            "티커": a["ticker"],
            "유형": a["type"],
            "수량": a["quantity"],
            "평균단가": a["avg_price"],
            "현재가": cur_price,
            "평가금액": val,
            "평가금액(원)": val_krw,
            "손익": pnl,
            "손익률(%)": pnl_pct,
            "등락률(%)": chg if chg else 0.0,
            "통화": a["currency"],
        })

    return pd.DataFrame(rows), total_krw, total_cost_krw

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 포트폴리오 대시보드")
    st.markdown("---")

    # USD/KRW Rate
    usd_krw = get_usd_krw()
    st.metric("USD/KRW", f"₩{usd_krw:,.0f}")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("---")
    st.markdown("### ⚙️ 설정")

    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📌 자산 추가")
    with st.form("add_asset_form", clear_on_submit=True):
        new_name = st.text_input("자산명", placeholder="삼성전자")
        new_ticker = st.text_input("티커", placeholder="005930.KS")
        new_type = st.selectbox("유형", ["한국주식", "미국주식", "ETF", "현금", "암호화폐", "기타"])
        new_qty = st.number_input("수량", min_value=0.0, step=0.01)
        new_avg = st.number_input("평균단가", min_value=0.0, step=0.01)
        new_cur = st.selectbox("통화", ["KRW", "USD"])
        submitted = st.form_submit_button("➕ 추가", use_container_width=True)
        if submitted and new_name and new_ticker:
            st.session_state.assets.append({
                "name": new_name, "ticker": new_ticker,
                "type": new_type, "quantity": new_qty,
                "avg_price": new_avg, "currency": new_cur,
            })
            st.success(f"✅ {new_name} 추가됨")
            st.rerun()

# ── Main Content ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; align-items:baseline; gap:1rem; margin-bottom:1.5rem;">
  <h1 style="font-family:'Space Mono',monospace; font-size:1.6rem; margin:0; color:#00d4aa;">PORTFOLIO DASHBOARD</h1>
  <span style="font-size:0.8rem; color:#64748b;">{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</span>
</div>
""", unsafe_allow_html=True)

# ── Compute Portfolio ────────────────────────────────────────────────────────
with st.spinner("실시간 데이터 로딩 중..."):
    df, total_val_krw, total_cost_krw = calculate_portfolio(st.session_state.assets, usd_krw)

total_pnl_krw = total_val_krw - total_cost_krw
total_pnl_pct = (total_pnl_krw / total_cost_krw * 100) if total_cost_krw > 0 else 0
pnl_color = "#00d4aa" if total_pnl_krw >= 0 else "#ef4444"
pnl_sign = "+" if total_pnl_krw >= 0 else ""

# ── KPI Cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">총 평가금액</div>
      <div class="metric-value">₩{total_val_krw/1e6:.2f}M</div>
      <div class="metric-delta" style="color:var(--muted);">{total_val_krw:,.0f}원</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">총 투자금액</div>
      <div class="metric-value">₩{total_cost_krw/1e6:.2f}M</div>
      <div class="metric-delta" style="color:var(--muted);">{total_cost_krw:,.0f}원</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">총 손익</div>
      <div class="metric-value" style="color:{pnl_color};">{pnl_sign}₩{total_pnl_krw/1e6:.2f}M</div>
      <div class="metric-delta {'delta-up' if total_pnl_krw>=0 else 'delta-down'}">{pnl_sign}{total_pnl_pct:.2f}%</div>
    </div>""", unsafe_allow_html=True)
with c4:
    # Count positive/negative assets
    pos = (df["손익률(%)"] > 0).sum()
    neg = (df["손익률(%)"] < 0).sum()
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">종목 현황</div>
      <div class="metric-value">{len(df)}</div>
      <div class="metric-delta"><span class="delta-up">▲{pos}</span> <span style="color:var(--muted);">│</span> <span class="delta-down">▼{neg}</span></div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 포트폴리오", "🗺️ 자산 배분", "📰 경제 뉴스", "🛠️ 자산 관리"])

# ── Tab 1: Portfolio Overview ─────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">📊 보유 자산 현황</div>', unsafe_allow_html=True)

    # Asset table
    for _, row in df.iterrows():
        pnl_c = "#00d4aa" if row["손익률(%)"] >= 0 else "#ef4444"
        chg_c = "#00d4aa" if row["등락률(%)"] >= 0 else "#ef4444"
        chg_s = "+" if row["등락률(%)"] >= 0 else ""
        pnl_s = "+" if row["손익률(%)"] >= 0 else ""
        cur_sym = "$" if row["통화"] == "USD" else "₩"

        if row["통화"] == "USD":
            val_str = f"${row['평가금액']:,.0f}"
        else:
            val_str = f"₩{row['평가금액']:,.0f}"

        st.markdown(f"""
        <div class="asset-row">
          <div class="asset-name">{row['이름']} <span style="font-size:0.72rem;background:rgba(100,116,139,0.2);padding:0.1rem 0.4rem;border-radius:4px;color:var(--muted);">{row['유형']}</span></div>
          <div class="asset-ticker">{row['티커']}</div>
          <div class="asset-amount">{val_str}</div>
          <div class="asset-pnl" style="color:{chg_c};">{chg_s}{row['등락률(%)']:.2f}%</div>
          <div class="asset-pnl" style="color:{pnl_c};">{pnl_s}{row['손익률(%)']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Performance Chart
    st.markdown('<div class="section-header">📉 수익률 비교</div>', unsafe_allow_html=True)
    chart_df = df[df["티커"].str[:4] != "CASH"].copy()
    chart_df = chart_df.sort_values("손익률(%)")

    fig = go.Figure()
    colors = ["#ef4444" if v < 0 else "#00d4aa" for v in chart_df["손익률(%)"]]
    fig.add_trace(go.Bar(
        x=chart_df["이름"],
        y=chart_df["손익률(%)"],
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in chart_df["손익률(%)"]],
        textposition="outside",
        textfont=dict(size=11, color=colors),
    ))
    fig.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font=dict(color="#e2e8f0", family="Noto Sans KR"),
        showlegend=False,
        xaxis=dict(gridcolor="#1f2d45"),
        yaxis=dict(gridcolor="#1f2d45", ticksuffix="%"),
        margin=dict(l=10, r=10, t=20, b=10),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Asset Allocation ──────────────────────────────────────────────────
with tab2:
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="section-header">🎯 유형별 배분</div>', unsafe_allow_html=True)
        type_df = df.groupby("유형")["평가금액(원)"].sum().reset_index()
        fig_pie = go.Figure(go.Pie(
            labels=type_df["유형"],
            values=type_df["평가금액(원)"],
            hole=0.55,
            marker=dict(colors=["#00d4aa","#3b82f6","#f59e0b","#8b5cf6","#ec4899","#14b8a6"]),
            textfont=dict(size=12),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0", family="Noto Sans KR"),
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
            height=320,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">💰 통화별 배분</div>', unsafe_allow_html=True)
        cur_df = df.groupby("통화")["평가금액(원)"].sum().reset_index()
        fig_cur = go.Figure(go.Pie(
            labels=cur_df["통화"],
            values=cur_df["평가금액(원)"],
            hole=0.55,
            marker=dict(colors=["#60a5fa","#4ade80"]),
        ))
        fig_cur.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font=dict(color="#e2e8f0", family="Noto Sans KR"),
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            height=320,
        )
        st.plotly_chart(fig_cur, use_container_width=True)

    st.markdown('<div class="section-header">📊 종목별 비중</div>', unsafe_allow_html=True)
    df_sorted = df.sort_values("평가금액(원)", ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=df_sorted["평가금액(원)"],
        y=df_sorted["이름"],
        orientation="h",
        marker=dict(
            color=df_sorted["평가금액(원)"],
            colorscale=[[0,"#1f2d45"],[0.5,"#3b82f6"],[1,"#00d4aa"]],
        ),
        text=[f"₩{v/1e6:.1f}M ({v/total_val_krw*100:.1f}%)" for v in df_sorted["평가금액(원)"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig_bar.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font=dict(color="#e2e8f0", family="Noto Sans KR"),
        xaxis=dict(gridcolor="#1f2d45"),
        yaxis=dict(gridcolor="#1f2d45"),
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        height=350,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ── Tab 3: Economic News ──────────────────────────────────────────────────────
with tab3:
    col_filter, col_refresh = st.columns([3, 1])
    with col_filter:
        region_filter = st.selectbox("지역 필터", ["전체", "한국", "미국", "글로벌"])
    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 뉴스 새로고침"):
            fetch_rss_news.clear()
            st.rerun()

    with st.spinner("뉴스 수집 중..."):
        news = get_all_news()

    if not news:
        st.info("뉴스를 불러올 수 없습니다. 인터넷 연결을 확인하거나 나중에 다시 시도해주세요.")
    else:
        col_n1, col_n2 = st.columns(2)
        for i, item in enumerate(news[:20]):
            region_map = {"us": "🇺🇸 미국", "kr": "🇰🇷 한국", "global": "🌐 글로벌"}
            badge_map = {"us": "badge-us", "kr": "badge-kr", "global": "badge-global"}
            label_map = {"us": "US", "kr": "KR", "global": "GLOBAL"}

            if region_filter != "전체":
                rmap = {"한국": "kr", "미국": "us", "글로벌": "global"}
                if item["region"] != rmap.get(region_filter, ""):
                    continue

            card_html = f"""
            <a href="{item['link']}" target="_blank" style="text-decoration:none; color:inherit;">
            <div class="news-card {item['region']}">
              <div class="news-title">
                <span class="news-badge {badge_map[item['region']]}">{label_map[item['region']]}</span>
                {item['title']}
              </div>
              <div class="news-meta">
                <span>📰 {item['source']}</span>
                <span>🕐 {item.get('published','')[:16] if item.get('published') else ''}</span>
              </div>
            </div></a>
            """
            if i % 2 == 0:
                with col_n1:
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                with col_n2:
                    st.markdown(card_html, unsafe_allow_html=True)

    # Market Index Summary
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🌏 주요 지수</div>', unsafe_allow_html=True)

    indices = [
        ("KOSPI", "^KS11"), ("KOSDAQ", "^KQ11"),
        ("S&P 500", "^GSPC"), ("나스닥", "^IXIC"),
        ("다우존스", "^DJI"), ("니케이", "^N225"),
    ]
    idx_cols = st.columns(len(indices))
    for col, (name, ticker) in zip(idx_cols, indices):
        price, chg = fetch_price(ticker)
        if price:
            c = "#00d4aa" if chg >= 0 else "#ef4444"
            s = "+" if chg >= 0 else ""
            col.markdown(f"""
            <div style="text-align:center; background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:0.8rem 0.5rem;">
              <div style="font-size:0.7rem; color:var(--muted); text-transform:uppercase;">{name}</div>
              <div style="font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; margin:0.3rem 0;">{price:,.1f}</div>
              <div style="color:{c}; font-size:0.8rem; font-weight:600;">{s}{chg:.2f}%</div>
            </div>""", unsafe_allow_html=True)

# ── Tab 4: Asset Management ───────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">🛠️ 자산 수정 / 삭제</div>', unsafe_allow_html=True)

    for i, asset in enumerate(st.session_state.assets):
        with st.expander(f"📌 {asset['name']} ({asset['ticker']})"):
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 1])
            with c1:
                new_qty = st.number_input("수량", value=float(asset["quantity"]), key=f"qty_{i}", step=0.01)
            with c2:
                new_avg = st.number_input("평균단가", value=float(asset["avg_price"]), key=f"avg_{i}", step=0.01)
            with c3:
                new_type = st.selectbox("유형", ["한국주식","미국주식","ETF","현금","암호화폐","기타"],
                                        index=["한국주식","미국주식","ETF","현금","암호화폐","기타"].index(asset["type"]) if asset["type"] in ["한국주식","미국주식","ETF","현금","암호화폐","기타"] else 0,
                                        key=f"type_{i}")
            with c4:
                if st.button("💾 저장", key=f"save_{i}", use_container_width=True):
                    st.session_state.assets[i]["quantity"] = new_qty
                    st.session_state.assets[i]["avg_price"] = new_avg
                    st.session_state.assets[i]["type"] = new_type
                    st.success("저장됨!")
                    st.rerun()
            with c5:
                if st.button("🗑️", key=f"del_{i}", use_container_width=True):
                    st.session_state.assets.pop(i)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 전체 데이터 내보내기</div>', unsafe_allow_html=True)
    csv = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "📥 CSV 다운로드",
        data=csv,
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
