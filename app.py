import streamlit as st
import google.generativeai as genai
import re

# 1. API 키 설정 (정석)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Streamlit Secrets에 API 키를 등록해주세요.")
    st.stop()

# 2. 모델 설정 (가장 표준적인 Flash 1.5)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# --- UI ---
st.title("👨‍🍳 레시피 분석기 (정석 버전)")

url = st.text_input("유튜브 링크를 입력하세요")

if st.button("분석 시작"):
    if url:
        with st.spinner("분석 중..."):
            try:
                # 3. 정석적인 콘텐츠 생성 호출
                prompt = f"다음 유튜브 영상의 레시피를 한국어로 정리해줘: {url}"
                response = model.generate_content(prompt)
                
                st.markdown(response.text)
                
                vid = get_video_id(url)
                if vid:
                    st.video(url)
            except Exception as e:
                st.error(f"연결 오류가 발생했습니다: {e}")
                st.info("API 키가 활성화된 후 실제 적용까지 약간의 시간이 걸릴 수 있습니다.")
    else:
        st.warning("링크를 입력해주세요.")
