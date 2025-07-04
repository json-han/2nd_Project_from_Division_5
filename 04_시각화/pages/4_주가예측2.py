import streamlit as st
import pandas as pd
import os
import pathlib
from datetime import datetime
from utils.stock_forecast import plot_combined_chart, forecast_price, plot_feature_importance

# ───────── 기본 경로 설정 ─────────
APP_DIR = pathlib.Path(__file__).parent.parent.resolve()

ROUND_OPTIONS = {
    "제20대": os.path.join(APP_DIR, "price_data/제20대_대선_테마주/"),
    "제21대": os.path.join(APP_DIR, "price_data/제21대_대선_테마주/"),
}

st.set_page_config(page_title="주가 예측 및 영향 분석", layout="wide")
st.title("📉 주가 예측 및 영향 분석")

selected_round = st.selectbox("대선 회차 선택", list(ROUND_OPTIONS.keys()))
price_dir = ROUND_OPTIONS[selected_round]

def get_stock_names(price_dir):
    stock_names = []
    for filename in os.listdir(price_dir):
        if filename.endswith(".csv"):
            parts = filename.split("_")
            if len(parts) >= 2:
                name = "_".join(parts[1:]).replace(".csv", "")
                stock_names.append(name)
    return sorted(stock_names)

stock_list = get_stock_names(price_dir)
stock_name = st.selectbox("종목 선택", stock_list)

# ───────── 파일 로딩 ─────────
file_path = None
for f in os.listdir(price_dir):
    if f.endswith(".csv") and stock_name in f:
        file_path = os.path.join(price_dir, f)
        break

if file_path and os.path.exists(file_path):
    price_df = pd.read_csv(file_path)
    price_df["Date"] = pd.to_datetime(price_df["Date"])

    # ───────── 날짜 범위 선택 ─────────
    min_date = price_df["Date"].min().date()
    max_date = price_df["Date"].max().date()
    start_date, end_date = st.date_input("분석 기간 선택", [min_date, max_date], min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.error("⚠️ 시작 날짜는 종료 날짜보다 이전이어야 합니다.")
    else:
        filtered_df = price_df[(price_df["Date"] >= pd.to_datetime(start_date)) &
                               (price_df["Date"] <= pd.to_datetime(end_date))]

        if filtered_df.empty:
            st.warning("해당 기간에 데이터가 없습니다.")
        else:
            st.subheader("📊 통합 분석 차트")
            st.pyplot(plot_combined_chart(filtered_df))

            st.subheader("🔮 주가 예측")
            st.pyplot(forecast_price(filtered_df, days=10))

            st.subheader("🧠 영향 요인 분석 (Feature Importance)")
            image_buf = plot_feature_importance()
            st.image(image_buf, caption="Feature Importance", width=600)
else:
    st.warning("선택한 종목의 주가 데이터가 존재하지 않습니다.")