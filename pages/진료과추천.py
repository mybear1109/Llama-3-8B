# 📄 pages/진료과추천.py
import streamlit as st
import toml
import os
import json
import re
from huggingface_hub import InferenceClient

# ✅ secrets.toml 경로 지정 및 API 키 로딩
toml_path = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "secrets.toml")
secrets = toml.load(toml_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# ✅ LLaMA 모델 클라이언트 생성
client = InferenceClient(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    token=HF_API_KEY
)

st.header("🏥 증상 기반 진료과 추천")

user_input = st.text_input("어떤 증상이 있으신가요?", key="진료과입력")

# 코드블록 제거 유틸 함수
def remove_code_blocks(text: str) -> str:
    return re.sub(r"```(?:json|python)?\\n?|```", "", text).strip()

if st.button("진료과 분석 시작") and user_input:
    prompt = f"""
다음 문장을 보고 적절한 진료과 1~2개를 JSON 형식으로 출력해줘.
문장: "{user_input}"
출력 형식:
{{
  "진료과": ["내과", "신경과"]
}}
반드시 위와 같은 JSON만 출력하고 코드블럭 없이 출력해줘.
"""

    try:
        response = client.text_generation(prompt=prompt, max_new_tokens=256)
        cleaned = remove_code_blocks(response)
        result = json.loads(cleaned)

        진료과 = result.get("진료과", [])
        if 진료과:
            st.markdown("## 🏷️ 추천 진료과")
            for idx, dept in enumerate(진료과, 1):
                st.success(f"**추천 {idx}: {dept}**")
        else:
            st.warning("❗ 진료과 정보가 추출되지 않았습니다.")

    except Exception as e:
        st.error(f"❗ 진료과 분석 실패: {e}")
        st.text_area("AI 원문 응답", response)