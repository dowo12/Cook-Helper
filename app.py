import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# [수정] 여기에 키를 직접 입력하세요
MY_DIRECT_KEY = "AIzaSy..." 

st.title("Gemini 강제 접속 테스트")

if st.button("강제 시동"):
    try:
        # 1. API 설정
        genai.configure(api_key=MY_DIRECT_KEY)
        
        # 2. 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. [핵심] v1beta 주소를 무시하고 v1 주소로 강제 전송
        response = model.generate_content(
            "안녕? 강제로 접속 성공했니?",
            request_options=RequestOptions(api_version='v1')
        )
        
        st.success("드디어 성공! 강제 접속되었습니다.")
        st.write(f"AI 답변: {response.text}")
        
    except Exception as e:
        st.error(f"강제 시동 실패: {e}")
        st.info("이래도 안 된다면 라이브러리를 완전히 지우고 다시 깔아야 합니다.")
