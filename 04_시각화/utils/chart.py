import os
import re
import platform
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib import rcParams
from wordcloud import WordCloud

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

# ───────── ChartGenerator 정의 ─────────
class ChartGenerator:
    def __init__(self, keyword_df: pd.DataFrame, article_df: pd.DataFrame, price_dir: str):
        self.keyword_df = keyword_df
        self.article_df = article_df
        self.price_dir = price_dir

    def extract_keywords_by_date(self, stock_name: str, start_date=None, end_date=None):
        post_df = self.article_df[self.article_df["종목명"] == stock_name].copy()
        keywords_row = self.keyword_df[self.keyword_df["종목명"] == stock_name]
        if keywords_row.empty:
            raise ValueError(f"{stock_name}의 키워드가 keyword_df에 없습니다.")

        raw_kw = keywords_row["키워드"].values[0]
        keyword_dict = raw_kw if isinstance(raw_kw, dict) else eval(raw_kw)
        keywords = list(keyword_dict.keys())

        keyword_freq_by_date = defaultdict(lambda: defaultdict(int))

        for _, row in post_df.iterrows():
            date = pd.to_datetime(row["날짜"]).date()
            if start_date and date < start_date.date():
                continue
            if end_date and date > end_date.date():
                continue

            text = f"{row['제목']} {row['내용']}"
            for kw in keywords:
                count = len(re.findall(re.escape(kw), str(text)))
                if count > 0:
                    keyword_freq_by_date[date][kw] += count

        buzz_data = [
            {"날짜": date, "총언급량": sum(freqs.values())}
            for date, freqs in keyword_freq_by_date.items()
        ]

        if not buzz_data:
            return pd.DataFrame(columns=["날짜", "총언급량"])

        buzz_df = pd.DataFrame(buzz_data)
        buzz_df["날짜"] = pd.to_datetime(buzz_df["날짜"])
        return buzz_df

    def merge_with_price(self, stock_name: str, buzz_df: pd.DataFrame, start_date=None, end_date=None):
        matched_files = [f for f in os.listdir(self.price_dir) if stock_name in f and f.endswith(".csv")]
        if not matched_files:
            raise FileNotFoundError(f"{stock_name} 관련 주가 CSV 파일이 {self.price_dir}에 없습니다.")

        price_path = os.path.join(self.price_dir, matched_files[0])
        price_df = pd.read_csv(price_path)
        price_df["Date"] = pd.to_datetime(price_df["Date"])

        merged_df = pd.merge(price_df, buzz_df, left_on="Date", right_on="날짜", how="left")
        merged_df["총언급량"] = merged_df["총언급량"].fillna(0)

        if start_date:
            merged_df = merged_df[merged_df["Date"] >= start_date]
        if end_date:
            merged_df = merged_df[merged_df["Date"] <= end_date]

        return merged_df

    def plot_buzz_chart(self, merged_df: pd.DataFrame, stock_name: str):
        fig, ax1 = plt.subplots(figsize=(12, 5))
        ax1.plot(merged_df["Date"], merged_df["Close"], color="tab:blue", label="종가")
        ax1.set_ylabel("주가", color="tab:blue")
        ax2 = ax1.twinx()
        ax2.plot(merged_df["Date"], merged_df["총언급량"], color="tab:red", linestyle='--', marker='o')
        ax2.set_ylabel("키워드 언급량", color="tab:red")
        plt.title(f"{stock_name} - 키워드 언급량 vs 주가 흐름")
        fig.tight_layout()
        return fig

    def plot_wordcloud(self, stock_name: str, max_words=100):
        row = self.keyword_df[self.keyword_df["종목명"] == stock_name]
        if row.empty:
            raise ValueError(f"{stock_name} 키워드가 존재하지 않습니다.")
        
        raw_kw = row["키워드"].values[0]
        keyword_dict = raw_kw if isinstance(raw_kw, dict) else eval(raw_kw)
        if not keyword_dict:
            raise ValueError(f"{stock_name}의 키워드 정보가 비어 있습니다.")

        wc = WordCloud(
            font_path=wordcloud_font_path,
            background_color='white',
            width=800,
            height=400,
            max_words=max_words
        )
        wc.generate_from_frequencies(keyword_dict)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        plt.title(f"{stock_name} - 키워드 워드클라우드")
        return fig