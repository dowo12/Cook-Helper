import streamlit as st
import google.generativeai as genai

# [수정] 여기에 키를 직접 입력하세요
MY_DIRECT_KEY = "AIzaSyABx0WRc_uX-rowdHWxSG3pe016rEWpLUU" 

st.title("Gemini 끝장 테스트")

if st.button("최후의 시동"):
    try:
        # 라이브러리 초기화
        genai.configure(api_key=MY_DIRECT_KEY)
        
        # [핵심] 모델 개체를 만들 때 명칭을 아예 경로까지 포함해서 부릅니다.
        # v1beta 에러를 피하기 위해 가장 원시적인 'models/gemini-1.5-flash'를 사용합니다.
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
        
        # 아무 옵션 없이 가장 기본 호출
        response = model.generate_content("안녕? 대답해봐.")
        
        st.success("🎉 드디어 시동 성공!")
        st.write(f"AI 답변: {response.text}")
        
    except Exception as e:
        st.error(f"시동 실패 원인: {e}")
        st.info("이래도 안 된다면, 현재 사용 중인 API 키가 '무료 할당량'을 다 썼거나 차단된 상태일 수 있습니다.")
