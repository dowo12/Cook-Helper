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
    prompt = f"이 유튜브 영상({video_url})의 레시피를 분석해줘. 재료와 조리 순서를 한국어로 상세히 알려줘."
    
    # [핵심] 서버가 인식할 수 있는 모든 모델 이름 후보군입니다.
    # 404 에러를 피하기 위해 하나씩 돌아가며 시도합니다.
    model_candidates = [
        'gemini-1.5-flash', 
        'models/gemini-1.5-flash', 
        'gemini-1.5-flash-latest',
        'gemini-pro'
    ]
    
    last_error = ""
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # 에러 나면 다음 후보로 이동
            
    return f"사용 가능한 모델을 찾지 못했습니다. 마지막 에러: {last_error}"

# --- UI 레이아웃 ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
st.info("자막 유무와 상관없이 AI가 영상을 분석합니다.")

url = st.text_input("분석할 유튜브 링크를 입력하세요")

if st.button("분석 시작 🚀"):
    if url:
        with st.spinner("AI가 최적의 연결 통로를 찾는 중..."):
            result = analyze_recipe(url)
            st.markdown(result)
            
            vid = get_video_id(url)
            if vid:
                st.video(url)
    else:
        st.error("링크를 입력해주세요.")
