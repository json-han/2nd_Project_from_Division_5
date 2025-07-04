import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pathlib
from utils.chart import ChartGenerator

# ───────── 기본 설정 ─────────
APP_DIR = pathlib.Path(__file__).parent.parent.resolve()  # main.py 기준 디렉토리

ROUND_OPTIONS = {
    "제20대": {
        "keyword_path": os.path.join(APP_DIR, "data/제20대_대선후보_종목별_키워드.csv"),
        "price_dir": os.path.join(APP_DIR, "price_data/제20대_대선_테마주/"),
        "article_path": os.path.join(APP_DIR, "data/제20대_전체_통합_기사.csv"),
        "paxnet_path": os.path.join(APP_DIR, "../01_데이터수집/비정형데이터/faxnet_20/팍스넷_20대_대선_테마주_크롤링_20250627.csv"),
        "naver_path": os.path.join(APP_DIR, "../01_데이터수집/비정형데이터/stock_community/output/csv/제20대_대선_테마주/"),
        "start_date": datetime(2022, 2, 5),
        "end_date": datetime(2022, 3, 16)
    },
    "제21대": {
        "keyword_path": os.path.join(APP_DIR, "data/제21대_대선후보_종목별_키워드.csv"),
        "price_dir": os.path.join(APP_DIR, "price_data/제21대_대선_테마주/"),
        "article_path": os.path.join(APP_DIR, "data/제21대_전체_통합_기사.csv"),
        "paxnet_path": os.path.join(APP_DIR, "../01_데이터수집/비정형데이터/faxnet_21/팍스넷_21대_대선_테마주_크롤링_20250627.csv"),
        "naver_path": os.path.join(APP_DIR, "../01_데이터수집/비정형데이터/stock_community/output/csv/제21대_대선_테마주/"),
        "start_date": datetime(2025, 5, 3),
        "end_date": datetime(2025, 6, 10)
    },
}

st.title("📊 대선 테마주 키워드 분석")

selected_round = st.selectbox("대선 회차 선택", list(ROUND_OPTIONS.keys()))
config = ROUND_OPTIONS[selected_round]

# ───────── 데이터 로딩 ─────────
@st.cache_data
def load_keyword_df(path):
    df = pd.read_csv(path)
    df["키워드"] = df["키워드"].apply(eval)
    return df

@st.cache_data
def load_or_generate_article_df(article_path, paxnet_path, naver_path):
    if os.path.exists(article_path):
        return pd.read_csv(article_path, parse_dates=["날짜"])

    # ── 팍스넷 로딩 ──
    paxnet_df = pd.read_csv(paxnet_path)
    paxnet_df["날짜"] = pd.to_datetime(paxnet_df["날짜"])
    paxnet_df = paxnet_df[["종목명", "날짜", "제목", "내용"]]

    # ── 네이버 종토방 로딩 ──
    csv_files = [f for f in os.listdir(naver_path) if f.endswith(".csv")]
    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(os.path.join(naver_path, file))
            df['filename'] = file
            dataframes.append(df)
        except Exception as e:
            print(f"파일 오류: {file} - {e}")
    naver_df = pd.concat(dataframes, ignore_index=True)
    naver_df["날짜"] = pd.to_datetime(naver_df["article_date"])
    naver_df.rename(columns={
        "stock_name": "종목명",
        "article_title": "제목",
        "article_content": "내용"
    }, inplace=True)
    naver_df = naver_df[["종목명", "날짜", "제목", "내용"]]

    # ── 병합 및 저장 ──
    all_df = pd.concat([paxnet_df, naver_df], ignore_index=True)
    all_df.to_csv(article_path, index=False)
    return all_df

keyword_df = load_keyword_df(config["keyword_path"])
article_df = load_or_generate_article_df(config["article_path"], config["paxnet_path"], config["naver_path"])

# ───────── 후보 / 종목 선택 ─────────
candidates = keyword_df["후보"].unique().tolist()
selected_candidate = st.radio("후보 선택", candidates)

filtered_df = keyword_df[keyword_df["후보"] == selected_candidate]
stock = st.selectbox("종목 선택", sorted(filtered_df["종목명"].unique()))

# ───────── 키워드 시각화 ─────────
stock_keywords = filtered_df[filtered_df["종목명"] == stock]["키워드"].values[0]
sorted_keywords = sorted(stock_keywords.items(), key=lambda x: x[1], reverse=True)

st.subheader(f"📌 {stock} 키워드 (빈도 기준)")

# 상위 10개 키워드
top_n = 10
top_df = pd.DataFrame(sorted_keywords[:top_n], columns=["키워드", "빈도수"])
st.table(top_df)

# 전체 키워드는 펼치기(expander)로 감추기
with st.expander("📂 전체 키워드 더보기"):
    full_df = pd.DataFrame(sorted_keywords, columns=["키워드", "빈도수"])
    st.dataframe(full_df, use_container_width=True)

# ───────── 워드클라우드 시각화 ─────────
generator = ChartGenerator(keyword_df=keyword_df, article_df=article_df, price_dir=config["price_dir"])

st.subheader("☁️ 키워드 워드클라우드")
try:
    fig_wc = generator.plot_wordcloud(stock)
    st.pyplot(fig_wc)
except Exception as e:
    st.warning(f"워드클라우드 생성 실패: {e}")

# ───────── 버즈 차트 시각화 ─────────
try:
    buzz_df = generator.extract_keywords_by_date(stock, start_date=config["start_date"], end_date=config["end_date"])
    merged_df = generator.merge_with_price(stock, buzz_df, start_date=config["start_date"], end_date=config["end_date"])

    st.subheader("📈 주가 vs 키워드 언급량")
    fig = generator.plot_buzz_chart(merged_df, stock)
    st.pyplot(fig)
except Exception as e:
    st.warning(f"시각화 실패: {e}")