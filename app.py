import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import pandas as pd
import os
import re

# --- 앱 설정 ---
st.set_page_config(page_title="나만의 요리 조수 AI", page_icon="👨‍🍳", layout="centered")

# --- AI 설정 (Secrets 사용) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
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
    """모든 종류의 자막(수동, 자동 생성 포함)을 시도하여 가져옵니다."""
    try:
        # 해당 영상에서 사용 가능한 자막 리스트 확인
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 1. 한국어(ko) 자막 탐색 (수동 작성 우선, 없으면 자동 생성)
        try:
            transcript = transcript_list.find_transcript(['ko'])
        except:
            # 2. 한국어 자막이 없으면 자동 생성된 한국어 자막 시도
            try:
                transcript = transcript_list.find_generated_transcript(['ko'])
            except:
                # 3. 그것도 없으면 사용 가능한 아무 자막(보통 영어)을 가져와 한국어로 번역
                transcript = transcript_list.find_transcript(['en', 'ja']).translate('ko')
        
        data = transcript.fetch()
        return " ".join([t['text'] for t in data])
    except Exception as e:
        # 상세 에러 로그 출력 (디버깅용)
        print(f"Transcript Error: {e}")
        return None

def analyze_recipe(text):
    prompt = f"""
    당신은 전문 요리사입니다. 제공된 유튜브 자막을 분석하여 다음 양식으로 출력하세요.
    마크다운 형식을 사용하여 가독성 좋게 출력해줘.

    1. 🛒 **재료 및 분량**: (정확한 계량 포함)
    2. 💰 **예상 원가**: (한국 대형마트 물가 기준 1인분 환산)
    3. 📝 **조리 순서**: (번호를 매겨 핵심만 요약)
    4. 💡 **쉐프의 팁**: (영상에서 강조한 비법)

    자막 내용: {text[:8000]}
    """
    response = model.generate_content(prompt)
    return response.text

# --- 앱 화면 ---
st.title("👨‍🍳 창조주님의 레시피 분석기")
st.markdown("유튜브 영상을 분석해 재료부터 원가까지 정리해 드립니다.")

# 사이드바 보관함
st.sidebar.title("📚 저장된 레시피")
if os.path.exists(DB_FILE):
    try:
        df_saved = pd.read_csv(DB_FILE)
        if not df_saved.empty:
            selected_title = st.sidebar.selectbox("요리를 선택하세요", df_saved["제목"].tolist())
            if st.sidebar.button("불러오기"):
                recipe_content = df_saved[df_saved["제목"] == selected_title].iloc[0]["내용"]
                st.session_state["current_analysis"] = recipe_content
                st.session_state["current_title"] = selected_title
    except:
        st.sidebar.write("저장된 레시피가 없습니다.")

# 메인 분석 로직
url = st.text_input("유튜브 링크(URL)를 입력하세요", placeholder="https://youtu.be/...")

if st.button("AI 분석 시작 🚀"):
    vid = get_video_id(url)
    if vid:
        with st.spinner("AI가 영상을 분석하고 있습니다..."):
            raw_text = fetch_transcript(vid)
            if raw_text:
                analysis_result = analyze_recipe(raw_text)
                st.session_state["current_analysis"] = analysis_result
                st.session_state["current_title"] = f"레시피_{vid}"
                st.video(url)
            else:
                st.error("자막 데이터를 추출할 수 없습니다. (유튜브 서버에서 자막 제공을 차단했거나 자막이 아예 없는 영상일 수 있습니다)")
    else:
        st.error("올바른 유튜브 링크를 입력해주세요.")

# 분석 결과 출력 및 저장
if "current_analysis" in st.session_state:
    st.divider()
    st.markdown(st.session_state["current_analysis"])
    
    if st.button("이 레시피 보관함에 저장하기 💾"):
        new_row = pd.DataFrame([[st.session_state["current_title"], st.session_state["current_analysis"]]], columns=["제목", "내용"])
        new_row.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
        st.success("보관함에 저장되었습니다!")
        st.rerun()
