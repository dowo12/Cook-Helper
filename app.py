import streamlit as st
import google.generativeai as genai

# --- [수정] 여기에 키를 직접 입력하세요 ---
MY_DIRECT_KEY = "AIzaSy..." 

st.title("Gemini 직결 테스트")

if st.button("직결 시동"):
    try:
        # 시크릿 거치지 않고 직접 설정
        genai.configure(api_key=MY_DIRECT_KEY)
        
        # 모델 선언
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 테스트 메시지 전송
        response = model.generate_content("안녕? 너 지금 내 키로 연결된 거 맞아?")
        
        st.success("대성공! 연결되었습니다.")
        st.write(f"AI 답변: {response.text}")
        
    except Exception as e:
        st.error(f"직결 시동 실패: {e}")
        st.info("이래도 404가 뜨면 계정이나 프로젝트 문제입니다.")
