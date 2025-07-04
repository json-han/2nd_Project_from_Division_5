import pandas as pd
import streamlit as st
import logging
import json
import urllib.parse
from datetime import datetime, timedelta

from trendspy.client import Trends

# --- 기본 설정 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
st.set_page_config(page_title="대선 테마주 검색량 시각화", page_icon="📈", layout="wide")

@st.cache_resource
def get_trends_client():
    """Trendspy 클라이언트를 초기화하고 캐싱합니다."""
    logging.info("Trends 클라이언트를 초기화합니다.")
    return Trends(retries=3, backoff_factor=0.5, timeout=(10, 25))

# --- 설정값 ---
MONITORING_KEYWORDS = ["덕성", "상지건설", "안랩", "써니전자", "평화산업", "코나아이"]

INDIVIDUAL_ANALYSIS_LIST = {
    "덕성":     {"start_date": "2021-09-18", "end_date": "2022-03-16", "label": "20대 기간"},
    "안랩":     {"start_date": "2021-09-18", "end_date": "2022-03-16", "label": "20대 기간"},
    "써니전자": {"start_date": "2021-09-18", "end_date": "2022-03-16", "label": "20대 기간"},
    "상지건설": {"start_date": "2024-12-14", "end_date": "2025-06-10", "label": "21대 기간"},
    "평화산업": {"start_date": "2024-12-14", "end_date": "2025-06-10", "label": "21대 기간"},
    "코나아이": {"start_date": "2024-12-14", "end_date": "2025-06-10", "label": "21대 기간"}
}
# --- 백엔드 함수 ---
@st.cache_data(ttl=3600)
def fetch_daily_interest(_tr_obj, keywords, days=240, geo="KR"):
    if not keywords: return pd.DataFrame()
    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(days=days - 1)
    timeframe = f"{start_date.strftime('%Y-%m-%d')} {end_date.strftime('%Y-%m-%d')}"
    try:
        df = _tr_obj.interest_over_time(keywords, timeframe=timeframe, geo=geo)
        if '일' in df.columns: df = df.set_index('일')
        elif 'Day' in df.columns: df = df.set_index('Day')
        df.index = pd.to_datetime(df.index)
        if 'isPartial' in df.columns: df = df.drop(columns=['isPartial'])
        if len(df.columns) == len(keywords): df.columns = keywords
        else: df = df.rename(columns={col: col.split(':')[0] for col in df.columns})
        for col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.fillna(0).astype(int)
        return df.sort_index()
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

def format_trend_data(series: pd.Series) -> pd.DataFrame:
    series = series.sort_index(ascending=True)
    processed_records = []
    in_zero_streak, streak_start_date = False, None
    sentinel_date = series.index.max() + pd.DateOffset(days=1)
    series_with_sentinel = pd.concat([series, pd.Series([1], index=[sentinel_date])])
    for date, value in series_with_sentinel.items():
        if value == 0:
            if not in_zero_streak: in_zero_streak, streak_start_date = True, date
        else:
            if in_zero_streak:
                streak_end_date = date - pd.DateOffset(days=1)
                period_str = f"{streak_start_date.strftime('%Y-%m-%d')} ~ {streak_end_date.strftime('%Y-%m-%d')}" if streak_start_date != streak_end_date else streak_start_date.strftime('%Y-%m-%d')
                processed_records.append({'sort_key': streak_start_date, '기간': period_str, '검색량': 0})
                in_zero_streak = False
            if date != sentinel_date:
                processed_records.append({'sort_key': date, '기간': date.strftime('%Y-%m-%d'), '검색량': int(value)})
    if not processed_records: return pd.DataFrame(columns=['기간', '검색량'])
    result_df = pd.DataFrame(processed_records).sort_values(by='sort_key', ascending=False)
    return result_df.drop(columns=['sort_key']).reset_index(drop=True)

def generate_trends_embed_html(keywords: list, start_date_str: str, end_date_str: str) -> str:
    time_str = f"{start_date_str} {end_date_str}"
    comparison_list = [{"keyword": kw, "geo": "KR", "time": time_str} for kw in keywords]
    comparison_item_json = json.dumps(comparison_list)
    q_param = urllib.parse.quote(','.join(keywords))
    explore_query_str = f"date={urllib.parse.quote(time_str)}&geo=KR&q={q_param}&hl=ko"
    return f"""
        <script type="text/javascript" src="https://ssl.gstatic.com/trends_nrtr/4116_RC01/embed_loader.js"></script>
        <script type="text/javascript">
        trends.embed.renderExploreWidget("TIMESERIES", {{"comparisonItem":{comparison_item_json},"category":0,"property":""}}, {{"exploreQuery":"{explore_query_str}","guestPath":"https://trends.google.com:443/trends/embed/"}});
        </script>"""

# --- Streamlit UI 구성 ---
tr = get_trends_client()

with st.sidebar:
    st.title("메뉴")
    page_choice = st.radio("페이지를 선택하세요.", ("실시간 트렌드 분석", "지정 기간 트렌드 분석"))

if page_choice == "실시간 트렌드 분석":
    st.header("실시간 트렌드 분석 (최근 240일)")
    with st.sidebar:
        st.divider()
        st.header("⚙️ 실시간 분석 옵션")
        selected_keywords = st.multiselect(
            "분석할 키워드를 선택하세요 (최대 5개):",
            options=MONITORING_KEYWORDS,
            default=["코나아이"],
            max_selections=5
        )
        if st.button("데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()

    if not selected_keywords:
        st.warning("👈 사이드바에서 분석할 키워드를 1개 이상 선택해주세요.")
    else:
        end_date_realtime = datetime.now()
        start_date_realtime = end_date_realtime - timedelta(days=239)
        html_code = generate_trends_embed_html(selected_keywords, start_date_realtime.strftime('%Y-%m-%d'), end_date_realtime.strftime('%Y-%m-%d'))
        st.components.v1.html(html_code, height=500)
        df_trends = fetch_daily_interest(tr, selected_keywords, days=240)
        if not df_trends.empty:
            with st.expander("자세한 데이터 보기 (0인 기간 요약)"):
                tabs = st.tabs([f"'{kw}'" for kw in selected_keywords])
                for i, keyword in enumerate(selected_keywords):
                    with tabs[i]:
                        display_df = format_trend_data(df_trends[keyword])
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

elif page_choice == "지정 기간 트렌드 분석":
    st.header("지정 기간 트렌드 분석")
    
    # --- ★ 탭 생성 ---
    tab20, tab21 = st.tabs(["20대 기간", "21대 기간"])

    with tab20:
        # 20대 기간 정보 가져오기 (첫 번째 키워드 기준)
        period_data = INDIVIDUAL_ANALYSIS_LIST["덕성"]
        st.info(f"**분석 기간:** {period_data['start_date']} ~ {period_data['end_date']}")
        st.divider()

        # '20대 기간'에 해당하는 키워드만 필터링하여 차트 생성
        for keyword, data in INDIVIDUAL_ANALYSIS_LIST.items():
            if data['label'] == '20대 기간':
                st.subheader(f"📊 '{keyword}' 트렌드")
                period_html_code = generate_trends_embed_html([keyword], data["start_date"], data["end_date"])
                st.components.v1.html(period_html_code, height=500)

    with tab21:
        # 21대 기간 정보 가져오기 (첫 번째 키워드 기준)
        period_data = INDIVIDUAL_ANALYSIS_LIST["상지건설"]
        st.info(f"**분석 기간:** {period_data['start_date']} ~ {period_data['end_date']}")
        st.divider()

        # '21대 기간'에 해당하는 키워드만 필터링하여 차트 생성
        for keyword, data in INDIVIDUAL_ANALYSIS_LIST.items():
            if data['label'] == '21대 기간':
                st.subheader(f"📊 '{keyword}' 트렌드")
                period_html_code = generate_trends_embed_html([keyword], data["start_date"], data["end_date"])
                st.components.v1.html(period_html_code, height=500)