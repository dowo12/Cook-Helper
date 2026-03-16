import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import os
import re

# 페이지 설정
st.set_page_config(page_title="레시피 AI 조수", page_icon="🍳")

# 데이터 저장용 파일
DB_FILE = "my_recipes.csv"

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def save_to_db(title, ingredients, steps, url):
    new_data = pd.DataFrame([[title, ingredients, steps, url]], columns=["제목", "재료", "조리법", "링크"])
    if not os.path.isfile(DB_FILE):
        new_data.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    else:
        new_data.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

# --- 사이드바: 내 레시피 보관함 ---
st.sidebar.title("📚 레시피 보관함")
if os.path.isfile(DB_FILE):
    df = pd.read_csv(DB_FILE)
    selected = st.sidebar.selectbox("저장된 요리 선택", df["제목"].tolist())
    if st.sidebar.button("불러오기"):
        row = df[df["제목"] == selected].iloc[0]
        st.session_state['view_recipe'] = row
else:
    st.sidebar.write("저장된 레시피가 없습니다.")

# --- 메인 화면 ---
st.title("🍳 나만의 유튜브 레시피 분석기")
st.write("유튜브 링크를 넣으면 AI가 재료와 조리법을 정리해 드립니다.")

url_input = st.text_input("유튜브 링크(URL) 입력", placeholder="https://www.youtube.com/watch?v=...")

if st.button("레시피 분석 시작"):
    vid = get_video_id(url_input)
    if vid:
        try:
            # 1. 자막 가져오기
            transcript_list = YouTubeTranscriptApi.get_transcript(vid, languages=['ko'])
            full_text = " ".join([t['text'] for t in transcript_list])
            
            st.video(url_input)
            
            # 2. AI 분석 결과 표시 (여기서는 분석된 결과 예시를 보여줍니다)
            # 실제 배포 시에는 제가 분석해드린 텍스트 구조를 사용하게 됩니다.
            st.success("분석이 완료되었습니다!")
            
            # 임시 데이터 (실제로는 LLM API를 연동하여 추출)
            st.subheader("🥗 분석된 재료 및 원가")
            ingredients_sample = "무 1.5kg, 대파 1대, 고춧가루, 뉴슈가 등\n(예상 원가: 1인분 약 400원)"
            st.info(ingredients_sample)
            
            st.subheader("👨‍🍳 단계별 조리법")
            steps_sample = "1. 무를 채 썰고 물에 헹구기\n2. 양념장 배합\n3. 골고루 버무리기"
            st.write(steps_sample)
            
            if st.button("내 보관함에 저장하기"):
                save_to_db("분석된 요리", ingredients_sample, steps_sample, url_input)
                st.toast("보관함에 저장되었습니다!")
                
        except Exception as e:
            st.error("자막을 불러올 수 없는 영상입니다. (자막 설정 확인 필요)")
    else:
        st.error("올바른 유튜브 링크를 입력해 주세요.")

# 저장된 레시피 보기 모드
if 'view_recipe' in st.session_state:
    r = st.session_state['view_recipe']
    st.divider()
    st.header(f"📖 {r['제목']}")
    st.write(f"[영상 링크]({r['링크']})")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛒 재료")
        st.write(r['재료'])
    with col2:
        st.markdown("### 📝 방법")
        st.write(r['조리법'])