import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- AI 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

def analyze_recipe(video_url):
    prompt = f"이 유튜브 영상({video_url})의 레시피를 분석해줘. 재료와 조리 순서를 알려줘."
    
    # [핵심] 서버가 거부할 수 없는 3단계 호출 전략
    strategies = [
        {"model": "gemini-1.5-flash", "version": "v1"},
        {"model": "models/gemini-1.5-flash", "version": "v1"},
        {"model": "gemini-1.5-flash-latest", "version": "v1"}
    ]
    
    for strategy in strategies:
        try:
            # API 버전을 v1으로 강제 고정하여 v1beta 에러를 회피합니다.
            model = genai.GenerativeModel(strategy["model"])
            response = model.generate_content(
                prompt,
                request_options=RequestOptions(api_version=strategy["version"])
            )
            return response.text
        except Exception:
            continue
            
    return "모든 접속 경로가 차단되었습니다. API 키가 'Generative Language API'를 지원하는지 다시 확인해주세요."

# --- UI ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
url = st.text_input("유튜브 링크를 입력하세요")

if st.button("분석 시작 🚀"):
    if url:
        with st.spinner("AI가 강제 접속 시도 중..."):
            result = analyze_recipe(url)
            st.markdown(result)
            # 영상 출력
            pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
            match = re.search(pattern, url)
            if match: st.video(url)
    else:
        st.error("링크를 입력해주세요.")
