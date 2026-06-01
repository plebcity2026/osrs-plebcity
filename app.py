from datetime import datetime

import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://prices.runescape.wiki/api/v1/osrs"
GE_TAX_RATE = 0.02
GE_TAX_CAP = 5_000_000

st.set_page_config(
    page_title="OSRS GE Flipper",
    page_icon="💰",
    layout="wide",
)

DEFAULT_USER_AGENT = "OSRS-GE-Flipper public Streamlit app / contact: replace-with-your-email"


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


def build_flips(user_agent: str, bankroll_gp: int) -> pd.DataFrame:
    mapping = load_mapping(user_agent)
    latest = load_latest(user_agent)
    five_min = load_period("5m", user_agent)
    one_hour = load_period("1h", user_agent)

    df = latest.merge(mapping, on="id", how="left")
    df = df.merge(five_min, on="id", how="left")
    df = df.merge(one_hour, on="id", how="left")

    df["limit"] = df["limit"].fillna(1).astype(int)
    df["volume_5m"] = df["volume_high_5m"].fillna(0) + df["volume_low_5m"].fillna(0)
    df["volume_1h"] = df["volume_high_1h"].fillna(0) + df["volume_low_1h"].fillna(0)

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

    df["last_high_trade"] = pd.to_datetime(df["high_time"], unit="s", utc=True, errors="coerce")
    df["last_low_trade"] = pd.to_datetime(df["low_time"], unit="s", utc=True, errors="coerce")

    df["flip_score"] = (
        df["profit_per_item"] * 0.45
        + df["roi_percent"] * 20
        + df["volume_1h"].clip(upper=10_000) * 0.01
        + df["momentum_percent"].fillna(0) * 5
    )
    return df


def format_gp(value) -> str:
    try:
        return f"{int(value):,} gp"
    except Exception:
        return "0 gp"


st.title("💰 OSRS Grand Exchange Flipping Dashboard")
st.caption("Live OSRS GE flipping scanner using OSRS Wiki real-time price endpoints.")

with st.sidebar:
    st.header("Filtrai")
    bankroll_gp = st.number_input("Tavo bankroll GP", min_value=1_000, max_value=10_000_000_000, value=10_000_000, step=100_000)
    min_volume_1h = st.number_input("Min 1h volume", min_value=0, value=100, step=50)
    min_profit = st.number_input("Min profit / item", min_value=-1_000_000, value=5, step=5)
    min_roi = st.number_input("Min ROI %", min_value=-100.0, value=0.2, step=0.1)
    min_buy = st.number_input("Min buy price", min_value=1, value=100, step=100)
    max_buy = st.number_input("Max buy price", min_value=1, value=50_000_000, step=100_000)
    members_filter = st.selectbox("Members filter", ["All", "Members only", "F2P only"])
    search = st.text_input("Ieškoti itemo")
    sort_by = st.selectbox("Rūšiuoti pagal", ["flip_score", "profit_with_bankroll", "profit_per_item", "roi_percent", "volume_1h", "momentum_percent"])
    top_n = st.slider("Kiek eilučių rodyti", min_value=10, max_value=500, value=50, step=10)

    with st.expander("Advanced"):
        user_agent = st.text_input(
            "User-Agent",
            value=DEFAULT_USER_AGENT,
            help="Jeigu app bus viešas, pakeisk į savo kontaktą arba projekto pavadinimą.",
        )

    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

try:
    with st.spinner("Kraunami GE duomenys..."):
        df = build_flips(user_agent=user_agent, bankroll_gp=int(bankroll_gp))
except Exception as exc:
    st.error(f"Nepavyko užkrauti OSRS kainų duomenų: {exc}")
    st.stop()

filtered = df.copy()
filtered = filtered[filtered["volume_1h"] >= min_volume_1h]
filtered = filtered[filtered["profit_per_item"] >= min_profit]
filtered = filtered[filtered["roi_percent"] >= min_roi]
filtered = filtered[filtered["buy_price"] >= min_buy]
filtered = filtered[filtered["buy_price"] <= max_buy]
filtered = filtered[filtered["flip_qty"] > 0]

if members_filter == "Members only":
    filtered = filtered[filtered["members"] == True]
elif members_filter == "F2P only":
    filtered = filtered[filtered["members"] == False]

if search.strip():
    filtered = filtered[filtered["name"].str.contains(search.strip(), case=False, na=False)]

filtered = filtered.sort_values(sort_by, ascending=False).head(top_n)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Candidates", f"{len(filtered):,}")
col2.metric("Best profit/item", format_gp(filtered["profit_per_item"].max()) if not filtered.empty else "0 gp")
col3.metric("Best bankroll profit", format_gp(filtered["profit_with_bankroll"].max()) if not filtered.empty else "0 gp")
col4.metric("Best ROI", f"{filtered['roi_percent'].max():.2f}%" if not filtered.empty else "0%")

st.subheader("Geriausi flipping kandidatai")

display_cols = [
    "name",
    "buy_price",
    "sell_price",
    "tax",
    "profit_per_item",
    "roi_percent",
    "limit",
    "volume_5m",
    "volume_1h",
    "flip_qty",
    "profit_with_bankroll",
    "momentum_percent",
    "last_high_trade",
    "last_low_trade",
    "flip_score",
]

st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "name": "Item",
        "buy_price": st.column_config.NumberColumn("Buy price", format="%d gp"),
        "sell_price": st.column_config.NumberColumn("Sell price", format="%d gp"),
        "tax": st.column_config.NumberColumn("GE tax", format="%d gp"),
        "profit_per_item": st.column_config.NumberColumn("Profit / item", format="%d gp"),
        "roi_percent": st.column_config.NumberColumn("ROI %", format="%.2f%%"),
        "profit_with_bankroll": st.column_config.NumberColumn("Profit with bankroll", format="%d gp"),
        "momentum_percent": st.column_config.NumberColumn("5m vs 1h momentum", format="%.2f%%"),
        "flip_score": st.column_config.NumberColumn("Score", format="%.2f"),
    },
)

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered CSV",
    data=csv,
    file_name=f"osrs_flips_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv",
)

with st.expander("Kaip skaityti lentelę"):
    st.markdown(
        """
        - **Buy price** = latest low price. Dažnai naudojama kaip target buy / instasell pusė.
        - **Sell price** = latest high price. Dažnai naudojama kaip target sell / instabuy pusė.
        - **Profit / item** = sell price - GE tax - buy price.
        - **Volume** svarbu: didelis marginas su mažu volume dažnai yra spąstai.
        - **Momentum** rodo, ar 5 min vidurkis aukščiau / žemiau 1 h vidurkio.
        - **Score** yra paprastas reitingas, kuris maišo profitą, ROI, volume ir momentum.
        """
    )

st.warning("Tai yra market scanner, ne garantuotas pelnas. OSRS kainos gali greitai keistis.")
