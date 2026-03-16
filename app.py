import streamlit as st
from google import genai
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- 최신 Gemini API 설정 (정석) ---
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키가 등록되지 않았습니다.")
    st.stop()

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- UI 레이아웃 ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")

url = st.text_input("분석할 유튜브 링크(URL)를 입력하세요")

if st.button("레시피 추출하기 🚀"):
    if url:
        with st.spinner("AI가 영상을 분석하고 있습니다..."):
            try:
                # 최신 SDK의 정석 호출 방식입니다.
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=f"이 유튜브 영상의 레시피를 한국어로 자세히 정리해줘: {url}"
                )
                st.markdown(response.text)
                
                vid = get_video_id(url)
                if vid: st.video(url)
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
    else:
        st.error("링크를 입력해주세요.")
