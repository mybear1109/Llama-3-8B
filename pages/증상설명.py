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

st.header("💡 의심 증상 및 설명")

user_input = st.text_input("증상을 입력하세요:", key="증상입력")

# 코드블록 제거 함수
def remove_code_blocks(text: str) -> str:
    return re.sub(r"```(?:json|python)?\\n?|```", "", text).strip()

if st.button("증상 분석") and user_input:
    prompt = f"""
다음 문장을 보고 주요 증상 목록과 설명을 JSON으로 출력해줘.
형식:
{{
  "증상": [
    {{"이름": "두통", "설명": "머리가 아픈 증상입니다."}},
    {{"이름": "구토", "설명": "음식을 토해내는 증상입니다."}}
  ]
}}
문장: "{user_input}"
코드블록 없이 JSON만 출력해줘. 설명 없이.
"""
    try:
        response = client.text_generation(prompt=prompt, max_new_tokens=384)
        cleaned = remove_code_blocks(response)
        result = json.loads(cleaned)
        증상들 = result.get("증상", [])

        if not 증상들:
            st.warning("❗ 증상 정보가 추출되지 않았습니다.")
        else:
            for 증 in 증상들:
                st.markdown(f"- **{증['이름']}**: {증['설명']}")

    except Exception as e:
        st.error(f"❗ 증상 설명 추출 실패: {e}")
        st.text_area("AI 원문 응답", response)