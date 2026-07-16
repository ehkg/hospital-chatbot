import streamlit as st
import pandas as pd
import re


st.title("병원 추천 챗봇")


# 엑셀 파일 불러오기
data = pd.read_excel("전신_증상_별_진료과_매칭_진짜최종.xlsx")
data = data.fillna("")


# 자주 쓰는 일상 표현을 의료 증상 표현으로 바꾸기
synonyms = {
    "배가 아파": "복통 복부 통증",
    "배가 아프": "복통 복부 통증",
    "배 아파": "복통 복부 통증",
    "배 아프": "복통 복부 통증",
    "머리가 아파": "두통",
    "머리가 아프": "두통",
    "머리 아파": "두통",
    "열이 나": "발열",
    "열 나": "발열",
    "토할 것 같": "구역",
    "토했": "구토",
    "어지러워": "어지럼증",
    "목이 아파": "인후통",
    "목 아파": "인후통",
    "숨이 차": "호흡곤란",
    "가슴이 아파": "흉통",
    "가려워": "가려움"
}


def normalize_text(text):
    text = str(text).lower().strip()

    for everyday_word, medical_word in synonyms.items():
        if everyday_word in text:
            text += " " + medical_word

    # 기호 제거
    text = re.sub(r"[^가-힣a-z0-9\s]", " ", text)

    return text


# 사용자 입력과 엑셀 증상의 관련성 점수 계산
def calculate_score(user_text, symptom_text):
    user_text = normalize_text(user_text)
    symptom_text = normalize_text(symptom_text)

    score = 0

    # 엑셀 증상 표현이 사용자 입력 안에 들어 있으면 10점 추가
    if symptom_text and symptom_text in user_text:
        score += 10

    # 공통으로 포함된 단어 개수만큼 점수 추가
    user_words = set(user_text.split())
    symptom_words = set(symptom_text.split())

    score += len(user_words & symptom_words)

    return score


st.write(
    "증상을 입력하면 관련성이 높은 진료과를 추천합니다."
)

symptom = st.chat_input("예: 배가 아프고 열이 나요")


if symptom:
    # 사용자가 입력한 문장 표시
    with st.chat_message("user"):
        st.write(symptom)

    # 모든 증상과 관련성 점수 비교
    data["일치점수"] = data["증상"].apply(
        lambda x: calculate_score(symptom, x)
    )

    # 점수가 높은 순서대로 정렬
    result = data.sort_values(
        "일치점수",
        ascending=False
    )

    with st.chat_message("assistant"):
        if result.iloc[0]["일치점수"] > 0:
            # 가장 높은 점수를 받은 결과 1개 선택
            best_result = result.iloc[0]

            st.write("입력하신 증상과 관련성이 높은 진료과입니다.")
            st.write(f"### {best_result['추천 진료과']}")
            st.write(f"관련 증상: {best_result['증상']}")

            if (
                "비고(병원급)" in data.columns
                and str(best_result["비고(병원급)"]).strip()
            ):
                st.write(f"참고: {best_result['비고(병원급)']}")

        else:
            st.write("관련된 증상을 찾지 못했습니다.")
            st.write("아픈 부위와 증상을 함께 적어주세요.")
            st.write("예: 배가 아프고 열이 나요.")


st.caption(
    "이 서비스는 진료과 선택을 돕기 위한 참고용이며 의료진의 진단을 대신하지 않습니다."
)
