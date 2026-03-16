import streamlit as st
from google import genai

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("Gemini 테스트")

if st.button("테스트"):
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="안녕?"
    )
    st.write(response.text)
