# Langflow Project Tracker

Прототип мультиагентной системы мониторинга проектных команд на базе Langflow и больших языковых моделей (LLM) для ВКР.

## Используемые технологии

* Langflow
* OpenAI API / VseLLM
* Python
* SQLite
* Streamlit

## Структура проекта

* `main.py` — основной backend системы
* `app.py` — интерфейс приложения
* `langflow_project.json` — экспортированная Langflow-схема проекта
* `requirements.txt` — зависимости проекта

## Установка

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Настройка

Создать файл `.env` на основе `.env.example` и указать API key.

## Запуск проекта

Запуск backend:

```bash
python main.py
```

Запуск интерфейса Streamlit:

```bash
streamlit run app.py
```

## Langflow

Для загрузки схемы необходимо импортировать файл:

```text
langflow_project.json
```

в интерфейсе Langflow через функцию Import.
