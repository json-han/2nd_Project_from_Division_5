# app.py
import streamlit as st
from datetime import datetime

# ───────── 페이지 설정 ─────────
st.set_page_config(
    page_title="대선 테마주 예측 서비스",
    layout="wide",
    page_icon="🗳️"
)

# ───────── 스타일 커스터마이징 ─────────
st.markdown("""
<style>
/* 공통 스타일 */
.main-title {
    font-size: 48px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 0.5em;
}
.subtitle {
    font-size: 20px;
    text-align: center;
    color: var(--subtitle-text);
    margin-bottom: 2em;
}
.highlight-box {
    padding: 1.5em;
    border-radius: 12px;
    border: 1px solid var(--box-border);
    background-color: var(--box-bg);
    color: var(--box-text);
    box-shadow: 0 0 5px rgba(0,0,0,0.05);
}
.highlight-box p {
    margin: 0.3em 0;
    font-size: 1.05rem;
}
.emoji {
    font-size: 28px;
}
.box-title {
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 0.5em;
}
.box-subtitle {
    font-size: 16px;
    color: var(--subtitle-text);
    margin-left: 1em;
}

/* 라이트 테마 */
@media (prefers-color-scheme: light) {
    :root {
        --box-bg: #f2f2f2;
        --box-text: #222222;
        --box-border: #cccccc;
        --subtitle-text: #666666;
    }
}

/* 다크 테마 */
@media (prefers-color-scheme: dark) {
    :root {
        --box-bg: #2a2a2a;
        --box-text: #f2f2f2;
        --box-border: #444444;
        --subtitle-text: #aaaaaa;
    }
}
</style>
""", unsafe_allow_html=True)

# ───────── 타이틀 및 소개 ─────────
st.markdown(f"<div class='main-title'>🗳️ 대선 테마주 예측 서비스</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>시계열 / 비정형 데이터 기반 테마주 검색량 및 주가 예측 시각화 플랫폼</div>", unsafe_allow_html=True)

# ───────── 카드 스타일 정보 박스 ─────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 분석 소개")
    st.markdown(
        """
        이 서비스는 다음과 같은 정보를 제공합니다:

        - 📈 **테마주별 트렌드 분석** (구글 검색량 기반)
        - 📊 **테마주별 키워드 분석** (커뮤니티 기반)
        - ☁️ **워드클라우드 시각화**
        - 📊 **종가 vs 키워드 언급량 그래프**
        - 🧠 **주가 예측 모델** 확장 예정
        """
    )

with col2:
    st.markdown("### 📆 대선 회차별 정보")
    st.markdown(
        """
        <div class='highlight-box'>
        <p class='emoji'>🗓️ <b>제20대 대선</b><br/>
        - 후보: 이재명 (1번), 윤석열 (2번)</p>
        - 기간: 2021-09-18 ~ 2022-03-16
        <hr/>
        <p class='emoji'>🗓️ <b>제21대 대선</b><br/>
        - 후보: 이재명 (1번), 윤석열 (2번), 이준석 (4번)</p>
        - 기간: 2024-12-14 ~ 2025-06-10
        </div>
        """, unsafe_allow_html=True
    )

# ───────── 강조 문구 ─────────
st.markdown("---")
st.success("👈 왼쪽 사이드바에서 원하는 분석 페이지를 선택해 주세요.")
st.markdown(f"<small>© {datetime.now().year} ThemeStock AI • Division 5</small>", unsafe_allow_html=True)

# streamlit run 2nd_Project_from_Division_5/04_visualization/app.py