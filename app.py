from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
GE_TAX_RATE = 0.02
GE_TAX_CAP = 5_000_000

st.set_page_config(
    page_title="OSRS GE Flipper",
    page_icon="💰",
    layout="wide",
)

DEFAULT_USER_AGENT = "OSRS-GE-Flipper public Streamlit app / contact: replace-with-your-email"

TEXT = {
    "LT": {
        "title": "💰 OSRS Grand Exchange Flipping Dashboard",
        "caption": "Live OSRS GE flipping scanneris naudojant OSRS Wiki real-time kainų endpointus.",
        "language": "Kalba / Language",
        "filters": "Filtrai",
        "bankroll": "Tavo bankroll GP",
        "min_volume": "Min 1h volume",
        "min_profit": "Min profit / item",
        "min_roi": "Min ROI %",
        "min_buy": "Min buy price",
        "max_buy": "Max buy price",
        "members_filter": "Members filtras",
        "all": "Visi",
        "members_only": "Members only",
        "f2p_only": "F2P only",
        "search": "Ieškoti itemo",
        "sort_by": "Rūšiuoti pagal",
        "top_n": "Kiek eilučių rodyti",
        "advanced": "Advanced",
        "ua_help": "Jeigu app bus viešas, pakeisk į savo kontaktą arba projekto pavadinimą.",
        "refresh": "Atnaujinti duomenis",
        "auto_refresh": "Automatiškai atnaujinti",
        "refresh_seconds": "Atnaujinimo intervalas, sek.",
        "auto_refresh_note": "Auto refresh įjungtas: puslapis persikrauna automatiškai, o kainos atnaujinamos pagal cache TTL.",
        "loading": "Kraunami GE duomenys...",
        "load_error": "Nepavyko užkrauti OSRS kainų duomenų",
        "candidates": "Kandidatai",
        "best_profit": "Geriausias profit/item",
        "best_bankroll": "Geriausias bankroll profit",
        "best_roi": "Geriausias ROI",
        "subheader": "Geriausi flipping kandidatai",
        "download": "Atsisiųsti filtruotą CSV",
        "how_to": "Kaip skaityti lentelę",
        "how_to_md": """
        - **Siūloma pirkti apie** = latest low price. Tai yra target buy zona pagal paskutinius low trades.
        - **Siūloma parduoti apie** = latest high price. Tai yra target sell zona pagal paskutinius high trades.
        - **Nupirkta / parduota** = kiek volume buvo užfiksuota prie high / low pusės per 5m arba 1h. Tai apytikslis likvidumo signalas, ne oficialus Jagex kiekis.
        - **Patikimumas** = score pagal volume, kainos šviežumą, profitą po tax, ROI ir ar 5m margin dar teigiamas.
        - **Profit / item** = sell price - GE tax - buy price.
        - **Volume** svarbu: didelis marginas su mažu volume dažnai yra spąstai.
        - **Momentum** rodo, ar 5 min vidurkis aukščiau / žemiau 1 h vidurkio.
        - **Score** yra paprastas reitingas, kuris maišo profitą, ROI, volume ir momentum.
        """,
        "warning": "Tai yra market scanner, ne garantuotas pelnas. OSRS kainos gali greitai keistis.",
        "item": "Itemas",
        "buy_price": "Buy price",
        "sell_price": "Sell price",
        "tax": "GE tax",
        "profit_item": "Profit / item",
        "profit_bankroll": "Profit su bankroll",
        "momentum": "5m vs 1h momentum",
        "score": "Score",
        "trend_chart": "Kainos kilimo / kritimo kreivė",
        "chart_item": "Pasirink itemą grafikui",
        "chart_timestep": "Grafiko laikotarpis",
        "chart_price_type": "Kainos kreivė",
        "high_price": "High / pardavimo kaina",
        "low_price": "Low / pirkimo kaina",
        "mid_price": "Vidurkis",
        "price_change": "Kainos pokytis",
        "rising": "Kyla",
        "falling": "Krenta",
        "stable": "Stabilu",
        "confidence": "Patikimumas",
        "confidence_score": "Patikimumo score",
        "high_confidence": "Aukštas",
        "medium_confidence": "Vidutinis",
        "low_confidence": "Žemas",
        "bought_1h": "Nupirkta 1h",
        "sold_1h": "Parduota 1h",
        "bought_5m": "Nupirkta 5m",
        "sold_5m": "Parduota 5m",
        "suggested_buy": "Siūloma pirkti apie",
        "suggested_sell": "Siūloma parduoti apie",
        "last_trade_age": "Pask. trade min",
    },
    "EN": {
        "title": "💰 OSRS Grand Exchange Flipping Dashboard",
        "caption": "Live OSRS GE flipping scanner using OSRS Wiki real-time price endpoints.",
        "language": "Language / Kalba",
        "filters": "Filters",
        "bankroll": "Your bankroll GP",
        "min_volume": "Min 1h volume",
        "min_profit": "Min profit / item",
        "min_roi": "Min ROI %",
        "min_buy": "Min buy price",
        "max_buy": "Max buy price",
        "members_filter": "Members filter",
        "all": "All",
        "members_only": "Members only",
        "f2p_only": "F2P only",
        "search": "Search item",
        "sort_by": "Sort by",
        "top_n": "Rows to show",
        "advanced": "Advanced",
        "ua_help": "For a public app, change this to your project name or contact.",
        "refresh": "Refresh data",
        "auto_refresh": "Auto refresh",
        "refresh_seconds": "Refresh interval, sec.",
        "auto_refresh_note": "Auto refresh is enabled: the page reruns automatically and prices refresh according to cache TTL.",
        "loading": "Loading GE data...",
        "load_error": "Could not load OSRS price data",
        "candidates": "Candidates",
        "best_profit": "Best profit/item",
        "best_bankroll": "Best bankroll profit",
        "best_roi": "Best ROI",
        "subheader": "Best flipping candidates",
        "download": "Download filtered CSV",
        "how_to": "How to read the table",
        "how_to_md": """
        - **Suggested buy near** = latest low price. This is a target buy zone based on recent low trades.
        - **Suggested sell near** = latest high price. This is a target sell zone based on recent high trades.
        - **Bought / sold** = volume seen on the high / low side over 5m or 1h. It is an approximate liquidity signal, not official Jagex volume.
        - **Confidence** = a score based on volume, price freshness, post-tax profit, ROI and whether the 5m margin is still positive.
        - **Profit / item** = sell price - GE tax - buy price.
        - **Volume** matters: a large margin with low volume is often a trap.
        - **Momentum** shows whether the 5 min average is above or below the 1 h average.
        - **Score** is a simple ranking that mixes profit, ROI, volume and momentum.
        """,
        "warning": "This is a market scanner, not guaranteed profit. OSRS prices can change quickly.",
        "item": "Item",
        "buy_price": "Buy price",
        "sell_price": "Sell price",
        "tax": "GE tax",
        "profit_item": "Profit / item",
        "profit_bankroll": "Profit with bankroll",
        "momentum": "5m vs 1h momentum",
        "score": "Score",
        "trend_chart": "Price rise / fall curve",
        "chart_item": "Choose item for chart",
        "chart_timestep": "Chart timeframe",
        "chart_price_type": "Price curve",
        "high_price": "High / sell price",
        "low_price": "Low / buy price",
        "mid_price": "Average",
        "price_change": "Price change",
        "rising": "Rising",
        "falling": "Falling",
        "stable": "Stable",
        "confidence": "Confidence",
        "confidence_score": "Confidence score",
        "high_confidence": "High",
        "medium_confidence": "Medium",
        "low_confidence": "Low",
        "bought_1h": "Bought 1h",
        "sold_1h": "Sold 1h",
        "bought_5m": "Bought 5m",
        "sold_5m": "Sold 5m",
        "suggested_buy": "Suggested buy near",
        "suggested_sell": "Suggested sell near",
        "last_trade_age": "Last trade min",
    },
}


def ge_tax(sell_price: int) -> int:
    """OSRS Grand Exchange tax: 2%, capped at 5M gp per item."""
    if sell_price <= 0:
        return 0
    return min(int(sell_price * GE_TAX_RATE), GE_TAX_CAP)


@st.cache_data(ttl=60, show_spinner=False)
def get_json(endpoint: str, user_agent: str) -> dict:
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"User-Agent": user_agent or DEFAULT_USER_AGENT},
        timeout=25,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600, show_spinner=False)
def load_mapping(user_agent: str) -> pd.DataFrame:
    rows = []
    for item in get_json("mapping", user_agent):
        rows.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "limit": item.get("limit"),
                "members": item.get("members"),
                "examine": item.get("examine"),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=60, show_spinner=False)
def load_latest(user_agent: str) -> pd.DataFrame:
    rows = []
    data = get_json("latest", user_agent).get("data", {})
    for item_id, price in data.items():
        low = price.get("low")
        high = price.get("high")
        if low is None or high is None or low <= 0 or high <= 0:
            continue
        rows.append(
            {
                "id": int(item_id),
                "buy_price": int(low),
                "sell_price": int(high),
                "raw_margin": int(high) - int(low),
                "low_time": price.get("lowTime"),
                "high_time": price.get("highTime"),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=300, show_spinner=False)
def load_period(period: str, user_agent: str) -> pd.DataFrame:
    rows = []
    data = get_json(period, user_agent).get("data", {})
    for item_id, price in data.items():
        rows.append(
            {
                "id": int(item_id),
                f"avg_high_{period}": price.get("avgHighPrice"),
                f"avg_low_{period}": price.get("avgLowPrice"),
                f"volume_high_{period}": price.get("highPriceVolume", 0),
                f"volume_low_{period}": price.get("lowPriceVolume", 0),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=300, show_spinner=False)
def load_timeseries(item_id: int, timestep: str, user_agent: str) -> pd.DataFrame:
    data = requests.get(
        f"{BASE_URL}/timeseries",
        params={"id": int(item_id), "timestep": timestep},
        headers={"User-Agent": user_agent or DEFAULT_USER_AGENT},
        timeout=25,
    )
    data.raise_for_status()
    rows = []
    for point in data.json().get("data", []):
        avg_high = point.get("avgHighPrice")
        avg_low = point.get("avgLowPrice")
        if avg_high is None and avg_low is None:
            continue
        if avg_high is not None and avg_low is not None:
            mid = (avg_high + avg_low) / 2
        else:
            mid = avg_high if avg_high is not None else avg_low
        rows.append(
            {
                "time": pd.to_datetime(point.get("timestamp"), unit="s", utc=True, errors="coerce"),
                "high": avg_high,
                "low": avg_low,
                "mid": mid,
                "volume": (point.get("highPriceVolume") or 0) + (point.get("lowPriceVolume") or 0),
            }
        )
    return pd.DataFrame(rows).dropna(subset=["time"]).sort_values("time")


def build_flips(user_agent: str, bankroll_gp: int) -> pd.DataFrame:
    mapping = load_mapping(user_agent)
    latest = load_latest(user_agent)
    five_min = load_period("5m", user_agent)
    one_hour = load_period("1h", user_agent)

    df = latest.merge(mapping, on="id", how="left")
    df = df.merge(five_min, on="id", how="left")
    df = df.merge(one_hour, on="id", how="left")

    df["limit"] = df["limit"].fillna(1).astype(int)
    df["bought_5m"] = df["volume_high_5m"].fillna(0)
    df["sold_5m"] = df["volume_low_5m"].fillna(0)
    df["bought_1h"] = df["volume_high_1h"].fillna(0)
    df["sold_1h"] = df["volume_low_1h"].fillna(0)
    df["volume_5m"] = df["bought_5m"] + df["sold_5m"]
    df["volume_1h"] = df["bought_1h"] + df["sold_1h"]

    df["tax"] = df["sell_price"].apply(ge_tax)
    df["profit_per_item"] = df["sell_price"] - df["tax"] - df["buy_price"]
    df["roi_percent"] = (df["profit_per_item"] / df["buy_price"]) * 100
    df["raw_margin_percent"] = (df["raw_margin"] / df["buy_price"]) * 100

    df["affordable_qty"] = (bankroll_gp // df["buy_price"]).astype(int)
    df["flip_qty"] = df[["limit", "affordable_qty"]].min(axis=1)
    df["profit_if_limit"] = df["profit_per_item"] * df["limit"]
    df["profit_with_bankroll"] = df["profit_per_item"] * df["flip_qty"]

    df["avg_high_5m"] = pd.to_numeric(df["avg_high_5m"], errors="coerce")
    df["avg_high_1h"] = pd.to_numeric(df["avg_high_1h"], errors="coerce")
    df["momentum_percent"] = ((df["avg_high_5m"] - df["avg_high_1h"]) / df["avg_high_1h"]) * 100

    df["current_mid_price"] = (df["buy_price"] + df["sell_price"]) / 2
    df["avg_mid_1h"] = (pd.to_numeric(df["avg_high_1h"], errors="coerce") + pd.to_numeric(df["avg_low_1h"], errors="coerce")) / 2
    df["price_change_percent"] = ((df["current_mid_price"] - df["avg_mid_1h"]) / df["avg_mid_1h"]) * 100

    df["last_high_trade"] = pd.to_datetime(df["high_time"], unit="s", utc=True, errors="coerce")
    df["last_low_trade"] = pd.to_datetime(df["low_time"], unit="s", utc=True, errors="coerce")
    df["last_trade_time"] = df[["last_high_trade", "last_low_trade"]].max(axis=1)
    now_utc = pd.Timestamp.now(tz="UTC")
    df["minutes_since_trade"] = ((now_utc - df["last_trade_time"]).dt.total_seconds() / 60).fillna(9999)

    avg_high_5m_numeric = pd.to_numeric(df["avg_high_5m"], errors="coerce")
    avg_low_5m_numeric = pd.to_numeric(df["avg_low_5m"], errors="coerce")
    df["recent_profit_per_item"] = avg_high_5m_numeric - avg_low_5m_numeric - avg_high_5m_numeric.fillna(0).apply(lambda x: ge_tax(int(x)) if x > 0 else 0)

    df["confidence_score"] = (
        np.minimum(df["volume_1h"] / 2000, 1) * 25
        + np.minimum(df["volume_5m"] / 200, 1) * 15
        + np.where(df["profit_per_item"] > 0, 15, 0)
        + np.minimum(df["roi_percent"].clip(lower=0) / 2, 1) * 15
        + np.where(df["minutes_since_trade"] <= 15, 15, np.where(df["minutes_since_trade"] <= 60, 8, 0))
        + np.where(df["recent_profit_per_item"] > 0, 15, 0)
    ).round(0).astype(int)
    df["confidence_label"] = np.select(
        [df["confidence_score"] >= 70, df["confidence_score"] >= 45],
        ["High", "Medium"],
        default="Low",
    )

    df["flip_score"] = (
        df["profit_per_item"] * 0.45
        + df["roi_percent"] * 20
        + df["volume_1h"].clip(upper=10_000) * 0.01
        + df["momentum_percent"].fillna(0) * 5
    )
    return df


def format_rs_number(value, suffix: str = "") -> str:
    """RuneScape-style compact numbers: 100K, 1.2M, 2.5B."""
    try:
        number = float(value)
    except Exception:
        return f"0{suffix}"

    sign = "-" if number < 0 else ""
    number = abs(number)

    if number >= 1_000_000_000:
        text = f"{number / 1_000_000_000:.2f}".rstrip("0").rstrip(".") + "B"
    elif number >= 1_000_000:
        text = f"{number / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"
    elif number >= 100_000:
        text = f"{number / 1_000:.0f}K"
    elif number >= 10_000:
        text = f"{number / 1_000:.1f}".rstrip("0").rstrip(".") + "K"
    else:
        text = f"{number:,.0f}"

    return f"{sign}{text}{suffix}"


def format_gp(value) -> str:
    return format_rs_number(value, " gp")


def color_positive_negative(value):
    try:
        number = float(value)
    except Exception:
        return ""
    if number > 0:
        return "color: #16a34a; font-weight: 700"
    if number < 0:
        return "color: #dc2626; font-weight: 700"
    return "color: #6b7280"


def color_confidence(value):
    if value in ("High", "Aukštas"):
        return "color: #16a34a; font-weight: 700"
    if value in ("Medium", "Vidutinis"):
        return "color: #ca8a04; font-weight: 700"
    if value in ("Low", "Žemas"):
        return "color: #dc2626; font-weight: 700"
    return ""


def row_market_color(row):
    value = row.get("price_change_percent", 0)
    try:
        value = float(value)
    except Exception:
        value = 0
    if value > 0:
        return ["background-color: rgba(22, 163, 74, 0.08)"] * len(row)
    if value < 0:
        return ["background-color: rgba(220, 38, 38, 0.08)"] * len(row)
    return [""] * len(row)


with st.sidebar:
    lang = st.selectbox("Kalba / Language", ["LT", "EN"], index=0)

t = TEXT[lang]

st.title(t["title"])
st.caption(t["caption"])

with st.sidebar:
    st.header(t["filters"])
    bankroll_gp = st.number_input(t["bankroll"], min_value=1_000, max_value=10_000_000_000, value=10_000_000, step=100_000)
    min_volume_1h = st.number_input(t["min_volume"], min_value=0, value=100, step=50)
    min_profit = st.number_input(t["min_profit"], min_value=-1_000_000, value=5, step=5)
    min_roi = st.number_input(t["min_roi"], min_value=-100.0, value=0.2, step=0.1)
    min_buy = st.number_input(t["min_buy"], min_value=1, value=100, step=100)
    max_buy = st.number_input(t["max_buy"], min_value=1, value=50_000_000, step=100_000)

    member_options = [t["all"], t["members_only"], t["f2p_only"]]
    members_filter = st.selectbox(t["members_filter"], member_options)

    search = st.text_input(t["search"])
    sort_by = st.selectbox(t["sort_by"], ["flip_score", "profit_with_bankroll", "profit_per_item", "roi_percent", "volume_1h", "momentum_percent"])
    top_n = st.slider(t["top_n"], min_value=10, max_value=500, value=50, step=10)

    auto_refresh = st.checkbox(t["auto_refresh"], value=True)
    refresh_seconds = st.selectbox(t["refresh_seconds"], [30, 60, 120, 300], index=1)

    with st.expander(t["advanced"]):
        user_agent = st.text_input(
            "User-Agent",
            value=DEFAULT_USER_AGENT,
            help=t["ua_help"],
        )

    if st.button(t["refresh"]):
        st.cache_data.clear()
        st.rerun()

if auto_refresh:
    if st_autorefresh is not None:
        st_autorefresh(interval=int(refresh_seconds) * 1000, key="osrs_auto_refresh")
        st.caption(t["auto_refresh_note"])
    else:
        st.warning("Auto refresh library is missing. Check requirements.txt and redeploy.")

try:
    with st.spinner(t["loading"]):
        df = build_flips(user_agent=user_agent, bankroll_gp=int(bankroll_gp))
except Exception as exc:
    st.error(f"{t['load_error']}: {exc}")
    st.stop()

filtered = df.copy()
filtered = filtered[filtered["volume_1h"] >= min_volume_1h]
filtered = filtered[filtered["profit_per_item"] >= min_profit]
filtered = filtered[filtered["roi_percent"] >= min_roi]
filtered = filtered[filtered["buy_price"] >= min_buy]
filtered = filtered[filtered["buy_price"] <= max_buy]
filtered = filtered[filtered["flip_qty"] > 0]

if members_filter == t["members_only"]:
    filtered = filtered[filtered["members"] == True]
elif members_filter == t["f2p_only"]:
    filtered = filtered[filtered["members"] == False]

if search.strip():
    filtered = filtered[filtered["name"].str.contains(search.strip(), case=False, na=False)]

filtered = filtered.sort_values(sort_by, ascending=False).head(top_n)

display_filtered = filtered.copy()
if lang == "LT" and not display_filtered.empty:
    display_filtered["confidence_label"] = display_filtered["confidence_label"].replace({
        "High": t["high_confidence"],
        "Medium": t["medium_confidence"],
        "Low": t["low_confidence"],
    })
# Numeric columns stay numeric so Streamlit can color percentages and profits.
# RuneScape-style K/M/B formatting is applied with Styler below.

col1, col2, col3, col4 = st.columns(4)
col1.metric(t["candidates"], f"{len(filtered):,}")
col2.metric(t["best_profit"], format_gp(filtered["profit_per_item"].max()) if not filtered.empty else "0 gp")
col3.metric(t["best_bankroll"], format_gp(filtered["profit_with_bankroll"].max()) if not filtered.empty else "0 gp")
col4.metric(t["best_roi"], f"{filtered['roi_percent'].max():.2f}%" if not filtered.empty else "0%")

if not filtered.empty:
    avg_change = filtered["price_change_percent"].mean()
    trend_label = t["rising"] if avg_change > 0 else t["falling"] if avg_change < 0 else t["stable"]
    st.metric(t["price_change"], f"{avg_change:.2f}%", delta=trend_label)

st.subheader(t["subheader"])

display_cols = [
    "name",
    "buy_price",
    "sell_price",
    "confidence_label",
    "confidence_score",
    "tax",
    "profit_per_item",
    "roi_percent",
    "limit",
    "bought_5m",
    "sold_5m",
    "bought_1h",
    "sold_1h",
    "volume_5m",
    "volume_1h",
    "flip_qty",
    "profit_with_bankroll",
    "price_change_percent",
    "momentum_percent",
    "last_high_trade",
    "last_low_trade",
    "flip_score",
]

formatters = {
    "buy_price": format_gp,
    "sell_price": format_gp,
    "tax": format_gp,
    "profit_per_item": format_gp,
    "profit_with_bankroll": format_gp,
    "limit": lambda v: format_rs_number(v),
    "bought_5m": lambda v: format_rs_number(v),
    "sold_5m": lambda v: format_rs_number(v),
    "bought_1h": lambda v: format_rs_number(v),
    "sold_1h": lambda v: format_rs_number(v),
    "volume_5m": lambda v: format_rs_number(v),
    "volume_1h": lambda v: format_rs_number(v),
    "flip_qty": lambda v: format_rs_number(v),
    "roi_percent": lambda v: f"{v:.2f}%",
    "momentum_percent": lambda v: "n/a" if pd.isna(v) else f"{v:.2f}%",
    "price_change_percent": lambda v: "n/a" if pd.isna(v) else f"{v:.2f}%",
    "confidence_score": lambda v: f"{v:.0f}/100",
    "minutes_since_trade": lambda v: f"{v:.0f}m",
    "flip_score": lambda v: f"{v:.2f}",
}

styled_table = (
    display_filtered[display_cols]
    .style
    .format(formatters)
    .apply(row_market_color, axis=1)
    .map(color_positive_negative, subset=["profit_per_item", "roi_percent", "momentum_percent", "price_change_percent", "profit_with_bankroll"])
    .map(color_confidence, subset=["confidence_label"])
)

st.dataframe(
    styled_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "name": t["item"],
        "buy_price": t["suggested_buy"],
        "sell_price": t["suggested_sell"],
        "confidence_label": t["confidence"],
        "confidence_score": t["confidence_score"],
        "tax": t["tax"],
        "profit_per_item": t["profit_item"],
        "roi_percent": "ROI %",
        "price_change_percent": t["price_change"],
        "limit": "Limit",
        "bought_5m": t["bought_5m"],
        "sold_5m": t["sold_5m"],
        "bought_1h": t["bought_1h"],
        "sold_1h": t["sold_1h"],
        "volume_5m": "Volume 5m",
        "volume_1h": "Volume 1h",
        "flip_qty": "Flip qty",
        "profit_with_bankroll": t["profit_bankroll"],
        "momentum_percent": t["momentum"],
        "flip_score": t["score"],
    },
)


if not filtered.empty:
    st.subheader(t["trend_chart"])
    chart_options = filtered[["id", "name"]].drop_duplicates().head(250)
    name_to_id = dict(zip(chart_options["name"], chart_options["id"]))
    default_name = chart_options.iloc[0]["name"]

    chart_col1, chart_col2, chart_col3 = st.columns([2, 1, 1])
    with chart_col1:
        selected_item_name = st.selectbox(t["chart_item"], list(name_to_id.keys()), index=0)
    with chart_col2:
        timestep_label = st.selectbox(t["chart_timestep"], ["24h / 5m", "7d / 1h", "30d / 6h", "1y / 24h"], index=0)
    with chart_col3:
        chart_price_type = st.selectbox(t["chart_price_type"], [t["mid_price"], t["high_price"], t["low_price"]], index=0)

    timestep = timestep_label.split(" / ")[1]
    selected_id = int(name_to_id[selected_item_name])

    try:
        ts = load_timeseries(selected_id, timestep, user_agent)
        if not ts.empty:
            value_col = "mid"
            if chart_price_type == t["high_price"]:
                value_col = "high"
            elif chart_price_type == t["low_price"]:
                value_col = "low"

            first_price = ts[value_col].dropna().iloc[0]
            last_price = ts[value_col].dropna().iloc[-1]
            change_percent = ((last_price - first_price) / first_price) * 100 if first_price else 0
            line_color = "#16a34a" if change_percent >= 0 else "#dc2626"

            st.metric(
                f"{selected_item_name} — {t['price_change']}",
                format_gp(last_price),
                delta=f"{change_percent:.2f}%",
            )

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=ts["time"],
                    y=ts[value_col],
                    mode="lines",
                    line=dict(color=line_color, width=3),
                    name=chart_price_type,
                    hovertemplate="%{x}<br>%{y:,.0f} gp<extra></extra>",
                )
            )
            fig.update_layout(
                height=420,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_title="Time",
                yaxis_title="GP",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No chart data for this item yet.")
    except Exception as exc:
        st.warning(f"Chart could not load: {exc}")

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    t["download"],
    data=csv,
    file_name=f"osrs_flips_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)

with st.expander(t["how_to"]):
    st.markdown(t["how_to_md"])

st.warning(t["warning"])
