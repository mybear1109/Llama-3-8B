# symptoms.py

SYMPTOM_TO_DEPARTMENT = {
    "감기": "내과",
    "기침": "내과",
    "열": "내과",
    "두통": "신경과",
    "어지럼증": "신경과",
    "복통": "내과",
    "소화불량": "내과",
    "미식거림": "내과",
    "구토": "내과",
    "가슴통증": "순환기내과",
    "당뇨": "내분비내과",
    "고혈압": "순환기내과",
    "피부 가려움": "피부과",
    "발진": "피부과",
    "관절통": "정형외과",
    "허리통증": "정형외과",
    "눈 따가움": "안과",
    "시야 흐림": "안과",
    "청력 저하": "이비인후과",
    "목 통증": "이비인후과"
}

def classify_symptoms(user_text: str):
    matched_departments = set()
    matched_symptoms = []

    for keyword, department in SYMPTOM_TO_DEPARTMENT.items():
        if keyword in user_text:
            matched_symptoms.append(keyword)
            matched_departments.add(department)

    return {
        "진료과": list(matched_departments),
        "증상": matched_symptoms
    }
