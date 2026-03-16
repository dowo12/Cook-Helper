import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import os
import re
import urllib.parse

# --- 앱 설정 ---
st.set_page_config(page_title="창조주님의 레시피 분석기", page_icon="👨‍🍳", layout="wide")

# --- AI 설정 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 모델 호출 방식을 가장 표준적인 형태로 유지합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Secrets에 API 키가 설정되지 않았습니다.")
    st.stop()

DB_FILE = "recipe_storage.csv"

def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id):
    """자막 데이터를 시도하고, 실패 시 None 반환"""
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

def analyze_recipe(video_url, transcript_text=None):
    """자막이 있으면 자막 기반, 없으면 AI 지식 기반 분석"""
    if transcript_text:
        prompt = f"다음 유튜브 자막을 분석해서 레시피(재료, 원가, 순서, 팁)를 정리해줘:\n\n{transcript_text[:10000]}"
    else:
        prompt = f"이 유튜브 영상({video_url})의 레시피를 분석해줘. 자막이 없으니 네가 아는 정보를 바탕으로 요리 전문가로서 상세히 알려줘."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 분석 중 오류 발생: {str(e)}"

# --- UI 레이아웃 ---
st.title("👨‍🍳 창조주님의 레시피 분석기")

# 🔍 유튜브 검색 기능
st.subheader("🔍 영상 찾기")
search_query = st.text_input("검색어를 입력하세요 (예: 임성근 무생채)")
if search_query:
    encoded = urllib.parse.quote(search_query)
    st.markdown(f'[👉 유튜브에서 "{search_query}" 검색 결과 보기](https://www.youtube.com/results?search_query={encoded})')

st.divider()

# 📝 분석 기능
st.subheader("📝 영상 분석 및 저장")
url = st.text_input("분석할 유튜브 링크(URL)를 입력하세요")

if st.button("AI 분석 시작 🚀"):
    if url:
        vid = get_video_id(url)
        with st.spinner("AI 요리사가 분석 중입니다..."):
            raw_text = fetch_transcript(vid) if vid else None
            # 자막 유무와 상관없이 AI 분석 실행
            result = analyze_recipe(url, raw_text)
            st.session_state["result"] = result
            if vid: st.video(url)
    else:
        st.error("링크를 입력해주세요.")

if "result" in st.session_state:
    st.markdown(st.session_state["result"])
    if st.button("이 레시피 보관함에 저장 💾"):
        new_data = pd.DataFrame([["새 레시피", st.session_state["result"]]], columns=["제목", "내용"])
        new_data.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
        st.success("보관함에 저장되었습니다!")
