import streamlit as st 
import pandas as pd
import re


# 엑셀 파일 불러오기
data = pd.read_excel("전신_증상_별_진료과_매칭_진짜최종.xlsx")
data = data.fillna("")


# 문장에서 특수문자 제거
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^가-힣a-z0-9\s]", " ", text)
    return text


# 일상 표현을 의료 용어로 연결
synonyms = {
    "배가 아파": "복통 복부 통증",
    "배가 아프": "복통 복부 통증",
    "배 아파": "복통 복부 통증",
    "배 아프": "복통 복부 통증",
    "열이 나": "발열",
    "열 나": "발열",
    "머리가 아파": "두통",
    "머리가 아프": "두통",
    "머리 아파": "두통",
    "토할 것 같": "구역",
    "토했": "구토",
    "어지러워": "어지럼증",
    "목이 아파": "인후통",
    "목 아파": "인후통",
    "숨이 차": "호흡곤란",
    "가슴이 아파": "흉통",
    "가려워": "가려움"
}


# 입력 문장에 해당하는 의료 용어 추가
def add_synonyms(text):
    text = clean_text(text)

    for expression, medical_word in synonyms.items():
        if expression in text:
            text += " " + medical_word

    return text


# 웹사이트 화면
st.title("병원 추천 챗봇")

st.write(
    "증상을 입력하면 관련성이 높은 진료과를 추천합니다."
)

symptom = st.chat_input("예: 배가 아프고 열이 나요")


# 추천 결과
if symptom:
    with st.chat_message("user"):
        st.write(symptom)
        
    converted_text = add_synonyms(symptom)
    user_words = set(converted_text.split())

    # 사용자 입력과 데이터베이스 증상의 공통 단어 개수 계산
    def calculate_score(database_symptom):
        database_text = clean_text(database_symptom)
        database_words = set(database_text.split())

        return len(user_words & database_words)

    data["일치점수"] = data["증상"].apply(calculate_score)

    # 점수가 1점 이상인 결과만 남기고 높은 순서로 정렬
    result = data[data["일치점수"] > 0]
    result = result.sort_values("일치점수", ascending=False)

    if result.empty:
        st.warning("일치하는 증상을 찾지 못했습니다.")
        st.write("아픈 부위와 증상을 함께 적어주세요.")
        st.write("예: 배가 아프고 열이 나요.")

    else:
        # 가장 높은 점수를 받은 결과 1개 선택
        best_result = result.iloc[0]

        st.subheader("추천 진료과")
        st.write("추천 진료과:", best_result["추천 진료과"])
        st.write("관련 증상:", best_result["증상"])

        # 비고 내용이 있을 때만 출력
        if (
            "비고(병원급)" in data.columns
            and str(best_result["비고(병원급)"]).strip()
        ):
            st.write("참고:", best_result["비고(병원급)"])


st.caption(
    "이 서비스는 진료과 선택을 돕기 위한 참고용이며 의료진의 진단을 대신하지 않습니다."
) 





