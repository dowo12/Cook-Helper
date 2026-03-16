import streamlit as st
import google.generativeai as genai
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- AI 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def analyze_recipe(video_url):
    prompt = f"이 유튜브 영상({video_url})의 레시피를 분석해줘. 재료와 조리 순서를 알려줘."
    
    # [핵심] 여러 모델 이름을 순차적으로 시도합니다.
    model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(name)
            response = model.generate_content(prompt)
            return response.text
        except Exception:
            continue # 실패하면 다음 모델로 넘어감
            
    return "현재 API 키로 사용 가능한 모델을 찾을 수 없습니다. AI Studio 설정을 확인해주세요."

# --- UI ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
url = st.text_input("유튜브 링크를 입력하세요")

if st.button("분석 시작 🚀"):
    if url:
        with st.spinner("AI가 분석 중입니다..."):
            result = analyze_recipe(url)
            st.markdown(result)
            vid = get_video_id(url)
            if vid: st.video(url)
    else:
        st.error("링크를 입력해주세요.")
