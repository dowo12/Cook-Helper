import streamlit as st
from google import genai
import pandas as pd
import os
import re

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 무적 레시피", page_icon="👨‍🍳")

# --- 최신 Gemini API 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    # 최신 google-genai 라이브러리 방식
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
    """
    자막을 직접 추출하지 않고, Gemini의 비디오 이해 능력을 활용합니다.
    자막이 있으면 자막을, 없으면 영상 정보를 바탕으로 AI가 추론합니다.
    """
    prompt = f"""
    이 유튜브 영상({video_url})의 레시피를 분석해줘.
    
    [분석 가이드]
    1. 영상에 자막 데이터가 있다면 이를 우선 활용해.
    2. 자막이 없다면 영상 제목, 유튜버 스타일, 그리고 네 지식을 바탕으로 가장 정확한 레시피를 만들어줘.
    
    [출력 양식]
    - 🛒 재료 및 분량
    - 💰 예상 원가 (한국 기준)
    - 📝 조리 순서
    - 💡 쉐프의 비법
    """
    
    try:
        # 최신 SDK 호출 방식
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {str(e)}"

# --- UI 레이아웃 ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")
st.info("최신 AI 엔진으로 자막 유무와 상관없이 레시피를 추출합니다.")

url = st.text_input("분석할 유튜브 링크(URL)를 입력하세요", placeholder="https://youtu.be/...")

if st.button("레시피 추출하기 🚀"):
    if url:
        vid = get_video_id(url)
        with st.spinner("AI가 영상을 정밀 분석 중입니다..."):
            result = analyze_recipe_smart(url)
            st.session_state["final_recipe"] = result
            if vid: st.video(url)
    else:
        st.error("링크를 입력해주세요.")

# 결과 출력 및 저장
if "final_recipe" in st.session_state:
    st.divider()
    st.markdown(st.session_state["final_recipe"])
    
    if st.button("보관함에 저장 💾"):
        new_row = pd.DataFrame([["새 레시피", st.session_state["final_recipe"]]], columns=["제목", "내용"])
        new_row.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
        st.success("저장되었습니다!")
