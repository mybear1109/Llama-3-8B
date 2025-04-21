import streamlit as st
import toml
import os
import json
import re
from huggingface_hub import InferenceClient


# ✅ secrets.toml에서 Hugging Face API 키 불러오기
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# ✅ LLaMA 모델 클라이언트
client = InferenceClient(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    token=HF_API_KEY
)

# ✅ Streamlit UI 설정
st.set_page_config(page_title="AI 진료 도우미", layout="centered")
st.title("🩺 AI 진료 도우미")
st.markdown("증상을 입력하면 진료과와 증상 요약, 관련 증상 설명까지 AI가 분석해줍니다.")

# ✅ 사용자 입력
user_input = st.text_input("증상을 입력하세요:", "")

# ✅ 분석 요청
if st.button("AI 분석 요청") and user_input:
    # 1️⃣ 프롬프트 기반 AI 분석 요청
    prompt = f"""
다음 문장을 보고 적절한 진료과 1~2개와 관련 증상, 해당 증상에 대한 설명도 함께 JSON 형식으로 출력해줘.
문장: "{user_input}"

응답 예시(JSON 형식):
{{
  "진료과": ["내과", "신경과"],
  "증상": [
    {{ "이름": "두통", "설명": "머리가 아프고 무거운 느낌이 드는 증상입니다." }},
    {{ "이름": "미식거림", "설명": "속이 울렁거리고 구역질이 날 것 같은 느낌이에요." }}
  ]
}}
반드시 위와 같은 형식으로 JSON만 출력해줘. 설명 없이.
"""

    completion = client.text_generation(prompt=prompt, max_new_tokens=512)
    ai_response = completion


    

    # 2️⃣ JSON 파싱 및 카드 출력
    try:
        json_start = ai_response.find("{")
        json_end = ai_response.rfind("}") + 1
        parsed_json = json.loads(ai_response[json_start:json_end])

        진료과 = parsed_json.get("진료과", [])
        증상설명 = parsed_json.get("증상", [])

        st.markdown("## 🏥 추천 진료과")
        cols = st.columns(2 if len(진료과) > 1 else 1)

        if len(진료과) > 0:
            with cols[0]:
                st.markdown(f"""
                <div style='background-color:#f0f0f0;padding:1rem;border-radius:10px;text-align:center;'>
                    <h5>추천 진료과 1</h5>
                    <p style='font-size:18px;'><strong>{진료과[0]}</strong></p>
                </div>
                """, unsafe_allow_html=True)

        if len(진료과) > 1:
            with cols[1]:
                st.markdown(f"""
                <div style='background-color:#f0f0f0;padding:1rem;border-radius:10px;text-align:center;'>
                    <h5>추천 진료과 2</h5>
                    <p style='font-size:18px;'><strong>{진료과[1]}</strong></p>
                </div>
                """, unsafe_allow_html=True)

        # 3️⃣ 의심 증상 설명
        if 증상설명:
            st.markdown("## 💡 의심 증상 및 설명")
            for item in 증상설명:
                st.markdown(f"""
                <div style='background-color:#fdfdfd;padding:1rem;border-left:4px solid #4CAF50;margin-bottom:0.5rem;'>
                    <strong>{item['이름']}</strong><br>
                    <span style='color:#444;'>{item['설명']}</span>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.warning("❗ 진료과 또는 증상 정보를 파싱하지 못했습니다.\n원문을 참고하세요.")


        

    # 4️⃣ 결과 출력
    st.write("🤖 **AI 응답 (원문)**")
    st.code(ai_response, language="json")

    # 5️⃣ 사용자 친화 설명 출력
    st.markdown("🧑‍⚕️ **사용자 친화 설명 보기**")
    st.markdown(generate_user_friendly_explanation(ai_response))