# 추천 결과
if symptom:
    with st.chat_message("user"):
        st.write(symptom)

    converted_text = add_synonyms(symptom)
    user_words = set(converted_text.split())

    # 사용자 입력과 데이터베이스 증상의 관련성 점수 계산
    def calculate_score(database_symptom):
        database_text = clean_text(database_symptom)
        database_words = set(database_text.split())

        score = 0

        # 엑셀의 증상 표현이 입력 문장 안에 포함되면 10점 추가
        if database_text and database_text in converted_text:
            score += 10

        # 공통으로 포함된 단어 개수만큼 점수 추가
        score += len(user_words & database_words)

        return score

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
