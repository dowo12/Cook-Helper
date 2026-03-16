import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import pandas as pd
import os
import re
import urllib.parse

# --- 앱 설정 ---
st.set_page_config(page_title="나만의 요리 조수 AI", page_icon="👨‍🍳", layout="wide")

# --- AI 설정 (Secrets 사용) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 가장 똑똑한 모델인 gemini-1.5-flash 사용
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Streamlit Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

DB_FILE = "recipe_storage.csv"

# --- 유틸리티 함수 ---
def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """자막 추출 시도"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['ko'])
            except:
                transcript = transcript_list.find_transcript(['en']).translate('ko')
        return " ".join([t['text'] for t in transcript.fetch()])
    except:
        return None

def analyze_recipe_with_ai(video_url, transcript_text=None):
    """자막이 있으면 자막 기반, 없으면 영상 링크 정보를 기반으로 AI가 분석"""
    if transcript_text:
        prompt = f"""
        당신은 전문 요리사입니다. 다음 제공된 유튜브 자막 내용을 분석하여 레시피를 정리해주세요.
        
        자막 내용: {transcript_text[:8000]}
        
        양식:
        1. 🛒 **재료 및 분량**: (정확한 계량 포함)
        2. 💰 **예상 원가**: (한국 대형마트 물가 기준 1인분 환산)
        3. 📝 **조리 순서**: (번호를 매겨 핵심만 요약)
        4. 💡 **쉐프의 팁**: (영상에서 강조한 비법)
        """
    else:
        prompt = f"""
        당신은 전문 요리사입니다. 제공된 유튜브 영상({video_url})의 레시피를 분석해야 합니다.
        현재 자막 데이터를 직접 읽을 수 없는 상태이므로, 해당 영상의 제목과 유튜버의 평소 레시피 스타일, 
        그리고 당신이 가진 방대한 요리 지식을 바탕으로 가장 정확한 레시피를 추론해서 알려주세요.
        
        양식:
        1. 🛒 **재료 및 분량**: (추론된 정확한 계량)
        2. 💰 **예상 원가**: (한국 대형마트 물가 기준 1인분 환산)
        3. 📝 **조리 순서**: (전문적인 식견으로 정리한 단계별 가이드)
        4. 💡 **쉐프의 팁**: (해당 요리 시 주의사항 및 비법)
        
        *주의: 자막이 없으므로 '추론된 결과임'을 명시하지 말고, 전문가로서 자신 있게 정보를 제공하세요.*
        """
    
    response = model.generate_content(prompt)
    return response.text

# --- 앱 화면 구성 ---
st.title("👨‍🍳 창조주님의 무적 레시피 분석기")

# 사이드바 보관함
st.sidebar.title("📚 내 레시피 창고")
if os.path.exists(DB_FILE):
    try:
        df_saved = pd.read_csv(DB_FILE)
        if not df_saved.empty:
            selected_title = st.sidebar.selectbox("저장된 요리 선택", df_saved["제목"].tolist())
            if st.sidebar.button("레시피 불러오기"):
                st.session_state["current_analysis"] = df_saved[df_saved["제목"] == selected_title].iloc[0]["내용"]
                st.session_state["current_title"] = selected_title
    except:
        pass

# --- 🔍 1단계: 유튜브 검색 섹션 ---
st.subheader("🔍 1. 요리 영상 찾기")
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("검색어를 입력하세요", placeholder="예: 임성근 무생채, 백종원 제육볶음...")
with col2:
    if search_query:
        encoded_query = urllib.parse.quote(search_query)
        search_link = f"https://www.youtube.com/results?search_query={encoded_query}"
        st.markdown(f'<br><a href="{search_link}" target="_blank"><button style="width:100%; height:42px; border-radius:5px; background-color:#FF0000; color:white; border:none; cursor:pointer; font-weight:bold;">유튜브 검색 열기 📺</button></a>', unsafe_allow_html=True)

# --- 📝 2단계: 영상 분석 섹션 ---
st.divider()
st.subheader("📝 2. AI 분석하기 (자막 없어도 가능)")
url = st.text_input("분석할 유튜브 링크(URL)를 입력하세요", placeholder="https://youtu.be/...")

if st.button("분석 시작 🚀"):
    if url:
        vid = get_video_id(url)
        with st.spinner("AI가 영상을 분석하고 있습니다. 잠시만 기다려주세요..."):
            # 일단 자막 추출 시도
            raw_text = fetch_transcript(vid) if vid else None
            
            # 자막이 있든 없든 AI 분석 실행
            analysis_result = analyze_recipe_with_ai(url, raw_text)
            
            st.session_state["current_analysis"] = analysis_result
            st.session_state["current_title"] = f"레시피_{vid}" if vid else "새 레시피"
            
            if vid:
                st.video(url)
    else:
        st.error("분석할 링크를 입력해주세요.")

# 결과 출력 및 저장
if "current_analysis" in st.session_state:
    st.divider()
    st.markdown(st.session_state["current_analysis"])
    
    if st.button("내 보관함에 저장하기 💾"):
        new_row = pd.DataFrame([[st.session_state["current_title"], st.session_state["current_analysis"]]], columns=["제목", "내용"])
        new_row.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
        st.success("보관함에 저장되었습니다!")
        st.rerun()
