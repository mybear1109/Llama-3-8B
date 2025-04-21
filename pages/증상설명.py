# 📄 pages/증상설명.py
import streamlit as st
import json
from huggingface_hub import InferenceClient
import toml
import os
import re

# ✅ API 키 로딩
toml_path = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "secrets.toml")
secrets = toml.load(toml_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# ✅ HuggingFace LLaMA 모델 클라이언트
client = InferenceClient(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    token=HF_API_KEY
)

st.set_page_config(page_title="증상 설명", layout="centered")
st.header("💡 의심 증상별 진료과 및 설명")
st.markdown("증상 문장을 입력하면, 각 증상별 추천 진료과와 설명을 보여드립니다.")

user_input = st.text_input("🩺 증상을 입력해주세요:", key="증상입력")

# 코드블록 제거 함수
def remove_code_blocks(text: str) -> str:
    return re.sub(r"```(?:json|python)?\\n?|```", "", text).strip()

# JSON 문자열에서 첫 유효 JSON 블록만 추출
def extract_valid_json(text: str):
    matches = re.findall(r"\{.*?\}\s*$", text, re.DOTALL | re.MULTILINE)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    raise ValueError("유효한 JSON 블록을 찾지 못했습니다.")

if st.button("증상 분석") and user_input:
    prompt = f"""
다음 문장에서 증상별로 추천 진료과와 설명을 아래 JSON 형식으로 출력해줘.
문장: "{user_input}"
형식 예시 (구조만 참고하고 내용은 바꿔줘):
{{
  "증상": [
    {{"이름": "목 통증", "설명": "목이 따끔거리거나 아픈 증상입니다.", "추천 진료과": "이비인후과"}},
    {{"이름": "복통", "설명": "배가 아프고 쥐어짜는 듯한 느낌입니다.", "추천 진료과": "내과"}}
  ]
}}
반드시 위 형식을 참고해 JSON으로만 출력하고, 설명이나 코드블럭은 출력하지 마.
"""
    try:
        response = client.text_generation(prompt=prompt, max_new_tokens=384)
        cleaned = remove_code_blocks(response)
        result = extract_valid_json(cleaned)
        증상들 = result.get("증상", [])

        if not 증상들:
            st.warning("❗ 증상 정보가 추출되지 않았습니다.")
        else:
            for 증 in 증상들:
                st.markdown(f"""
                <div style='background-color:#f9f9f9;padding:1rem;margin-bottom:10px;border-left:5px solid #4a90e2;border-radius:5px;'>
                    <strong>증상:</strong> {증['이름']}<br>
                    <strong>설명:</strong> {증['설명']}<br>
                    <strong>추천 진료과:</strong> 🏥 {증['추천 진료과']}
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❗ 증상 설명 추출 실패: {e}")
        st.text_area("AI 원문 응답", response if 'response' in locals() else "응답 없음")