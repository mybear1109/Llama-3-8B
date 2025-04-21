import streamlit as st
import toml
import os
import json
import re
from huggingface_hub import InferenceClient
from requests.exceptions import RequestException

# ✅ Hugging Face API 키 로딩
toml_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(toml_path)
HF_API_KEY = secrets["huggingface"]["HUGGINGFACE_API_TOKEN"]

# ✅ 모델 클라이언트
client = InferenceClient(model="meta-llama/Meta-Llama-3.1-8B-Instruct", token=HF_API_KEY)

# ✅ 유틸 함수

def remove_code_blocks(text: str) -> str:
    return re.sub(r"```(?:json|python)?\\n?|```", "", text).strip()

def extract_json_block(text: str) -> str:
    """
    응답에서 첫 번째 JSON 블록만 추출
    """
    # 가장 먼저 등장하는 중괄호 페어만 추출
    brace_stack = []
    start, end = -1, -1
    for i, ch in enumerate(text):
        if ch == '{':
            if not brace_stack:
                start = i
            brace_stack.append('{')
        elif ch == '}':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack:
                    end = i + 1
                    break
    if start != -1 and end != -1:
        json_str = text[start:end]
        json.loads(json_str)  # 파싱 확인
        return json_str
    raise ValueError("유효한 JSON 블록을 찾지 못했습니다.")


def safe_parse_json(raw_text: str) -> dict:
    clean = remove_code_blocks(raw_text)
    return json.loads(extract_json_block(clean))

# ✅ UI 설정
st.set_page_config(page_title="AI 진료 도우미", layout="centered")
st.title("🩺 AI 진료 도우미")
st.markdown("AI가 입력한 증상을 분석해 진료과, 주요 증상, 관련 질환 및 응급도까지 알려드립니다.")

# 사용자 입력
user_input = st.text_input("🤔 어떤 증상이 있으신가요?", "")

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
        try:
            parsed = safe_parse_json(raw_response)
        except Exception:
            parsed = json.loads(remove_code_blocks(raw_response))  # fallback

        진료과 = parsed.get("진료과", [])
        증상 = parsed.get("증상", [])
        질환 = parsed.get("관련 질환", [])
        응급도 = parsed.get("응급도", "")

        with st.container():
            st.markdown("## 🏥 추천 진료과")
            for idx, dep in enumerate(진료과, 1):
                st.markdown(f"""
                <div style='background-color:#e3f2fd;padding:1rem;margin-bottom:10px;border-radius:10px;'>
                    <strong>추천 진료과 {idx}</strong>: <span style='font-size:18px;'>{dep}</span>
                </div>
                """, unsafe_allow_html=True)

        if 증상:
            st.markdown("## 💡 주요 증상 및 설명")
            for item in 증상:
                st.markdown(f"""
                <div style='background-color:#fff9e6;padding:0.8rem;margin-bottom:8px;border-left:6px solid #f1c40f;border-radius:5px;'>
                    <strong>{item['이름']}</strong>: {item['설명']}
                </div>
                """, unsafe_allow_html=True)

        if 질환:
            st.markdown("## 🧬 관련 질환")
            for item in 질환:
                st.markdown(f"""
                <div style='background-color:#f6f6f6;padding:0.8rem;margin-bottom:8px;border-left:4px solid #7f8c8d;border-radius:5px;'>
                    <strong>{item['이름']}</strong>: {item['설명']}
                </div>
                """, unsafe_allow_html=True)

        if 응급도:
            st.markdown("## 🚨 응급도 평가")
            st.markdown(f"""
            <div style='background-color:#fdecea;color:#b71c1c;padding:1rem;border-radius:10px;text-align:center;font-weight:bold;'>
                {응급도}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<div style='color:gray;'>🔎 이 결과는 참고용입니다. 증상이 계속되거나 악화된다면 반드시 전문의와 상담하세요.</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❗ JSON 파싱 실패: {e}")
        st.text_area("AI 원문 응답", raw_response)
        st.markdown("<div style='background-color:#fff3cd;padding:1rem;border-left:6px solid #ffc107;border-radius:5px;'>JSON 형식이 정확하지 않지만 원문을 기반으로 결과를 참고하세요.</div>", unsafe_allow_html=True)