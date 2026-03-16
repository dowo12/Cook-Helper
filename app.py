import streamlit as st
from google import genai
from google.genai import types # 추가적인 설정 제어를 위해 필요
import pandas as pd
import os
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- 최신 Gemini API 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    # 설정을 통해 API 버전을 명시적으로 제어하거나 기본값으로 생성
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

DB_FILE = "recipe_storage.csv"

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def analyze_recipe_smart(video_url):
    prompt = f"""
    이 유튜브 영상({video_url})의 레시피를 분석해줘.
    네가 가진 요리 지식을 바탕으로 가장 정확한 레시피를 정리해줘.
    
    [출력 양식]
    - 🛒 재료 및 분량
    - 💰 예상 원가 (한국 기준)
    - 📝 조리 순서
    - 💡 쉐프의 비법
    """
    
    try:
        # 모델 이름을 'gemini-1.5-flash'로 호출하되 
        # 에러가 나면 'gemini-1.5-flash-latest'로 시도하게끔 설계
        response = client.models.generate_content(
            model='gemini-1.5-flash', 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # 만약 여기서도 404가 뜨면 모델명을 다르게 시도
        try:
            response = client.models.generate_content(
                model='gemini-1.5-pro', # 플래시가 안되면 프로로 시도
                contents=prompt
            )
            return response.text
        except:
            return f"AI 분석 중 오류가 발생했습니다. API 키의 모델 권한을 확인해주세요: {str(e)}"

# --- UI 레이아웃 ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
st.info("API 연동 상태를 정밀 체크하며 분석을 진행합니다.")

url = st.text_input("분석할 유튜브 링크(URL)를 입력하세요")

if st.button("레시피 추출하기 🚀"):
    if url:
        vid = get_video_id(url)
        with st.spinner("AI 엔진 가동 중..."):
            result = analyze_recipe_smart(url)
            st.session_state["final_recipe"] = result
            if vid: st.video(url)
    else:
        st.error("링크를 입력해주세요.")

if "final_recipe" in st.session_state:
    st.divider()
    st.markdown(st.session_state["final_recipe"])
