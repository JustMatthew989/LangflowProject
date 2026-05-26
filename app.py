import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Project Tracker", layout="wide")

st.title("AI Project Tracker")
st.write("Система анализа ежедневных отчетов проектных команд")

st.header("Отправить ежедневный отчет")

user_id = st.text_input("ID / имя участника", value="student_1")
team_id = st.text_input("ID команды", value="team_a")

report_text = st.text_area(
    "Ежедневный отчет",
    height=180,
    placeholder="Например: Сегодня сделал авторизацию, JWT работает, блокеров нет..."
)

if st.button("Отправить отчет"):
    if not report_text.strip():
        st.error("Введите текст отчета")
    else:
        payload = {
            "user_id": user_id,
            "team_id": team_id,
            "text": report_text
        }

        with st.spinner("Отчет анализируется..."):
            response = requests.post(f"{API_URL}/report", json=payload)

        if response.status_code == 200:
            data = response.json()
            st.success("Отчет обработан и сохранен")

            st.subheader("Ответ системы")
            st.code(data["agent_response"], language="json")
        else:
            st.error("Ошибка при отправке отчета")
            st.text(response.text)

st.divider()

st.header("История отчетов")

if st.button("Обновить историю"):
    response = requests.get(f"{API_URL}/reports")

    if response.status_code == 200:
        reports = response.json()

        if reports:
            df = pd.DataFrame(reports)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Пока нет сохраненных отчетов")
    else:
        st.error("Не удалось загрузить историю")