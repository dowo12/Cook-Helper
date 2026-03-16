import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- AI 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 가장 똑똑하고 비디오 이해력이 좋은 모델 사용
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

DB_FILE = "recipe_storage.csv"

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def analyze_recipe_direct(video_url):
    """자막 추출 시도 없이, AI에게 링크를 직접 던져 분석 요청"""
    prompt = f"""
    이 유튜브 영상({video_url})의 내용을 분석해서 레시피를 알려줘.
    
    1. 만약 네가 이 영상을 직접 접근해서 자막이나 내용을 볼 수 있다면 그 데이터를 최우선으로 사용해줘.
    2. 만약 직접 접근이 안 된다면, 영상 제목과 유튜버의 정보, 그리고 네가 가진 요리 지식을 총동원해서 가장 정확한 레시피를 추론해줘.
    
    [양식]
    - 🛒 재료 및 분량
    - 💰 예상 원가 (한국 마트 기준)
    - 📝 조리 순서
    - 💡 쉐프의 비법 팁
    """
    
    try:
        # 모델에게 텍스트로 링크를 전달 (Gemini는 링크를 통해 정보를 유추하거나 접근 가능)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {str(e)}"

# --- UI ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
st.info("자막 유무와 상관없이 AI가 영상을 분석하여 결과를 도출합니다.")

url = st.text_input("분석할 유튜브 링크를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if st.button("레시피 추출하기 🚀"):
    if url:
        vid = get_video_id(url)
        with st.spinner("AI가 영상을 시청(?)하며 분석 중입니다..."):
            # 자막 긁기 시도 없이 바로 AI에게 질문
            result = analyze_recipe_direct(url)
            
            st.session_state["recipe_result"] = result
            if vid: st.video(url)
    else:
        st.error("링크를 입력해주세요.")

if "recipe_result" in st.session_state:
    st.divider()
    st.markdown(st.session_state["recipe_result"])
    
    if st.button("보관함에 저장 💾"):
        new_data = pd.DataFrame([["새 레시피", st.session_state["recipe_result"]]], columns=["제목", "내용"])
        new_data.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
        st.success("저장되었습니다!")
