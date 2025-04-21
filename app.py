import streamlit as st
import toml
import os
from huggingface_hub import InferenceClient
from symptoms import classify_symptoms

# ✅ secrets.toml에 저장된 값 불러오기
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# LLaMA 모델 클라이언트
client = InferenceClient(
    provider="novita",
    api_key=HF_API_KEY
)

# Streamlit UI
st.set_page_config(page_title="AI 진료 도우미", layout="centered")
st.title("🩺 AI 진료 도우미")
st.markdown("증상을 입력하면 진료과와 증상 요약을 AI가 분석해줍니다.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 증상에서 진료과와 주요 증상을 요약해주는 AI야. 결과는 JSON으로 알려줘."}
    ]

user_input = st.text_input("증상을 입력하세요:", "")

if st.button("AI 분석 요청") and user_input:
    # 로컬 사전 기반 진단
    local_result = classify_symptoms(user_input)
    st.write("📋 **로컬 진단 결과**")
    st.json(local_result)

    # AI 대화 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct",
        messages=st.session_state.messages,
        max_tokens=512,
    )
    ai_response = completion.choices[0].message["content"]
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # 결과 출력
    st.write("🤖 **AI 응답**")
    st.code(ai_response, language="json")
