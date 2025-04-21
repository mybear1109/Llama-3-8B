# pages/질환정보.py

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

client = InferenceClient(model="meta-llama/Meta-Llama-3.1-8B-Instruct", token=HF_API_KEY)

st.header("🧬 관련 질환 설명")

user_input = st.text_input("증상을 입력하세요:", key="질환입력")

if st.button("관련 질환 보기") and user_input:
    prompt = f"""
다음 증상에서 관련 질환 1~2개와 설명을 JSON으로 출력해줘.
형식:
{{"관련 질환": [{{"이름": "편두통", "설명": "일측성 두통으로..."}}, ...]}}
문장: "{user_input}"
JSON만 출력하고 설명하지 마.
"""

    try:
        response = client.text_generation(prompt=prompt, max_new_tokens=384)
        response = re.sub(r"```.*?\\n|```", "", response.strip())
        result = json.loads(response)
        질환들 = result.get("관련 질환", [])

        for 질환 in 질환들:
            st.markdown(f"- **{질환['이름']}**: {질환['설명']}")

    except Exception as e:
        st.error(f"❗ 관련 질환 정보 추출 실패: {e}")