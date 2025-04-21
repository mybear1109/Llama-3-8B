import streamlit as st
import toml
import os
import json
import re
from huggingface_hub import InferenceClient
import requests
from requests.exceptions import RequestException

# ✅ Hugging Face API 키 로딩
# ✅ API 키 로딩
toml_path = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "secrets.toml")
secrets = toml.load(toml_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# ✅ HuggingFace LLaMA 모델 클라이언트
client = InferenceClient(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    token=HF_API_KEY
)

st.header("🚨 응급도 평가")
st.markdown("증상을 입력하면 진료과, 증상 요약, 관련 질환 및 응급도까지 AI가 분석해줍니다.")

# 사용자 입력
user_input = st.text_input("🤔 어떤 증상이 있으신가요?", "")

# 코드블럭 제거 함수
def remove_code_blocks(text: str) -> str:
    return re.sub(r"```(?:json|python)?\\n?|```", "", text).strip()

# 분석 버튼 클릭 시
if st.button("AI 분석 요청") and user_input:
    prompt = f"""
다음 문장을 보고 적절한 진료과 1~2개, 증상 이름 및 설명, 관련 질환, 응급도를 JSON 형식으로 출력해줘.
문장: "{user_input}"
형식:
{{
  "진료과": ["내과", "신경과"],
  "증상": [
    {{ "이름": "두통", "설명": "머리가 아프고 무거운 느낌이 드는 증상입니다." }},
    {{ "이름": "미식거림", "설명": "속이 울렁거리고 구역질이 날 것 같은 느낌이에요." }}
  ],
  "관련 질환": [
    {{ "이름": "편두통", "설명": "일측성 두통으로 메스꺼움과 빛 예민 증상이 함께 나타나요." }}
  ],
  "응급도": "중간 - 빠른 진료 권장"
}}
JSON만 출력해줘. 설명/코드블럭 없이.
"""

    try:
        raw_response = client.text_generation(prompt=prompt, max_new_tokens=384)
        clean_response = remove_code_blocks(raw_response)
        parsed = json.loads(clean_response)

        진료과 = parsed.get("진료과", [])
        증상 = parsed.get("증상", [])
        질환 = parsed.get("관련 질환", [])
        응급도 = parsed.get("응급도", "")

        if 진료과:
            st.markdown("## 🏥 추천 진료과")
            for idx, dep in enumerate(진료과, 1):
                st.markdown(f"- **추천 진료과 {idx}**: {dep}")

        if 증상:
            st.markdown("## 💡 주요 증상 및 설명")
            for item in 증상:
                st.markdown(f"- **{item['이름']}**: {item['설명']}")

        if 질환:
            st.markdown("## 🧬 관련 질환")
            for j in 질환:
                st.markdown(f"- **{j['이름']}**: {j['설명']}")

        if 응급도:
            st.markdown("## 🚨 응급도 평가")
            st.success(f"{응급도}")

        st.markdown("---")
        st.markdown("✅ 위 결과는 참고용입니다. 증상이 계속되면 병원 방문을 권장드립니다.")

    except Exception as e:
        st.error(f"❗ JSON 파싱 실패: {e}")
        st.text_area("AI 원문 응답", raw_response)
