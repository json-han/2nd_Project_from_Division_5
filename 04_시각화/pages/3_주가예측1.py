import streamlit as st
import os
import pathlib
from PIL import Image
import collections

# ───────── 기본 설정 ─────────
APP_DIR = pathlib.Path(__file__).parent.parent.resolve()

# 대선 회차별 이미지 경로 설정
ELECTION_OPTIONS = {
    "제20대 대선": {
        "image_folder": os.path.join(APP_DIR, "data", "pngs", "20")
    },
    "제21대 대선": {
        "image_folder": os.path.join(APP_DIR, "data", "pngs", "21")
    }
}

def display_image_pairs(image_folder: str):
    """
    지정된 폴더에서 이미지 파일들을 쌍으로 묶어 2열로 표시하는 함수.
    파일명 형식: '종목코드_종목명_...'
    'pred' 이미지는 왼쪽, 'training_loss' 이미지는 오른쪽에 표시됩니다.
    """
    if not os.path.isdir(image_folder):
        st.error(f"'{image_folder}' 폴더를 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    image_files = [f for f in os.listdir(image_folder) if f.endswith('.png')]
    if not image_files:
        st.warning(f"표시할 이미지가 '{image_folder}' 폴더에 없습니다.")
        return

    # 종목코드_종목명 을 키로 사용하여 이미지 경로를 저장할 딕셔너리
    # 예: {'001470_삼부토건': {'pred': 'path/to/pred.png', 'loss': 'path/to/loss.png'}}
    image_pairs = collections.defaultdict(dict)

    for filename in image_files:
        try:
            parts = filename.split('_')
            stock_identifier = f"{parts[0]}_{parts[1]}" # '001470_삼부토건'

            if 'pred' in filename:
                image_pairs[stock_identifier]['pred'] = os.path.join(image_folder, filename)
            elif 'training_loss' in filename:
                image_pairs[stock_identifier]['loss'] = os.path.join(image_folder, filename)
        except IndexError:
            st.warning(f"파일명 '{filename}'의 형식이 올바르지 않아 건너뜁니다.")
            continue
            
    # 종목명 순으로 정렬하여 표시
    for stock_identifier, paths in sorted(image_pairs.items()):
        st.markdown(f"---")
        st.subheader(f"📊 {stock_identifier.replace('_', ' ')}")

        col1, col2 = st.columns(2)

        pred_path = paths.get('pred')
        loss_path = paths.get('loss')

        with col1:
            if pred_path:
                try:
                    image = Image.open(pred_path)
                    # st.image(image, caption="예측 결과 (Prediction)", use_column_width=True)
                    st.image(image, caption="예측 결과 (Prediction)", use_container_width=True)
                except Exception as e:
                    st.error(f"이미지 로딩 실패: {os.path.basename(pred_path)}")
            else:
                st.info("예측 결과 이미지가 없습니다.")

        with col2:
            if loss_path:
                try:
                    image = Image.open(loss_path)
                    # st.image(image, caption="학습 손실 (Training Loss)", use_column_width=True)
                    st.image(image, caption="학습 손실 (Training Loss)", use_container_width=True)
                except Exception as e:
                    st.error(f"이미지 로딩 실패: {os.path.basename(loss_path)}")
            else:
                st.info("학습 손실 이미지가 없습니다.")


# ───────── Streamlit 앱 구성 ─────────
st.set_page_config(layout="wide")
st.header("대선별 주가 예측 결과 시각화")

# ───────── 탭 생성 ─────────
tab20, tab21 = st.tabs(list(ELECTION_OPTIONS.keys()))

# --- 제20대 대선 탭 ---
with tab20:
    config_20 = ELECTION_OPTIONS["제20대 대선"]
    display_image_pairs(config_20["image_folder"])

# --- 제21대 대선 탭 ---
with tab21:
    config_21 = ELECTION_OPTIONS["제21대 대선"]
    display_image_pairs(config_21["image_folder"])