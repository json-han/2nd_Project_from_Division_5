import io
import pandas as pd
import numpy as np
import platform
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams
from PIL import Image



# ───────── 한글 폰트 설정 ─────────
system = platform.system()
if system == "Darwin":  # macOS
    rcParams["font.family"] = "AppleGothic"
    wordcloud_font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
elif system == "Windows":
    rcParams["font.family"] = "Malgun Gothic"
    wordcloud_font_path = "C:/Windows/Fonts/malgun.ttf"
else:  # Linux
    rcParams["font.family"] = "NanumGothic"
    wordcloud_font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

rcParams["axes.unicode_minus"] = False

# ───────── 통합 분석 차트 ─────────
def plot_combined_chart(price_df):
    price_df = price_df.copy()
    price_df['Date'] = pd.to_datetime(price_df['Date'])

    # 임의의 감성 점수 및 트렌드 값 삽입 (가상)
    price_df['감성점수'] = np.random.uniform(0, 1, size=len(price_df))
    price_df['구글트렌드'] = np.random.randint(20, 100, size=len(price_df))

    fig, ax1 = plt.subplots(figsize=(12, 5))

    # 주가: 파란색 실선
    ax1.plot(price_df['Date'], price_df['Close'], color='tab:blue', label='주가')
    ax1.set_ylabel('주가', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # 감성점수, 구글 트렌드: 붉은색 점선, 초록색 점선
    ax2 = ax1.twinx()
    ax2.plot(price_df['Date'], price_df['감성점수'], color='tab:red', linestyle='--', label='감성 점수')
    ax2.plot(price_df['Date'], price_df['구글트렌드'], color='tab:green', linestyle=':', label='구글 트렌드')
    ax2.set_ylabel('감성점수 / 트렌드', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # x축 날짜 형식 및 범례 설정
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    # 그래프 오른쪽에 범례 배치
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    fig.legend(
        handles=lines1 + lines2,
        labels=labels1 + labels2,
        loc="center left",
        bbox_to_anchor=(1.01, 0.5),
        borderaxespad=0,
        frameon=False,
    )

    plt.title("통합 분석 차트")
    fig.tight_layout()
    return fig

# ───────── 미래 주가 예측 ─────────
def forecast_price(price_df, days=10):
    price_df = price_df.copy()
    price_df['Date'] = pd.to_datetime(price_df['Date'])
    last_date = price_df['Date'].max()
    last_price = price_df['Close'].iloc[-1]

    # 임의의 예측 생성
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
    future_prices = last_price + np.linspace(0, 5, days) + np.random.randn(days)
    lower = future_prices - np.random.uniform(1, 2, size=days)
    upper = future_prices + np.random.uniform(1, 2, size=days)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(price_df['Date'], price_df['Close'], label='과거 주가')
    ax.plot(future_dates, future_prices, label='예측 주가', color='orange')
    ax.fill_between(future_dates, lower, upper, color='orange', alpha=0.2, label='신뢰 구간')
    ax.set_title("미래 주가 예측")
    ax.legend()
    fig.tight_layout()
    return fig

def plot_feature_importance():
    features = ['감성점수', '구글 트렌드', '거래량']
    importances = [0.45, 0.30, 0.25]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.barh(features, importances, color='skyblue')
    ax.set_title("Feature Importance (가상)")
    ax.set_xlim(0, 0.5)
    plt.tight_layout()

    # BytesIO 버퍼로 저장
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=250)
    plt.close(fig)
    buf.seek(0)

    # PIL 이미지로 변환하여 반환
    image = Image.open(buf)
    return image