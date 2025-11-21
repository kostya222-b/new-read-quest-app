import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import re

tags_metadata = [
    {
        'name': 'SEARCH ANSWERS',
        'description': 'API для поиска правильных ответов.',
    }
]

origin_endpoint = [
    'https://iomqt-vo.edu.rosminzdrav.ru',
    'https://iomqt-spo.edu.rosminzdrav.ru',
    'https://iomqt-nmd.edu.rosminzdrav.ru'
]

app = FastAPI(
    root_path="/api",
    title='API for SEARCH ANSWERS',
    description='API для поиска правильных ответов',
    version='0.1.0',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_endpoint,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем файл с ответами один раз при запуске приложения
this_folder = os.getcwd()
with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8") as f:
    text = f.read()

# Создаём индекс: {вопрос: [список правильных ответов]}
answers_index = {}

def build_index():
    lines = text.split('\n')
    current_question = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r'^\d+\.', line):
            # Это номер вопроса
            current_question = line
        elif line.startswith('~') or line.endswith('+'):
            # Это вариант ответа
            if current_question and line.endswith('+'):
                answer = line[:-1].strip()
                answer = answer[1:] if answer.startswith('~') else answer
                answer = re.sub(r'[;.]$', '', answer).strip()
                if current_question not in answers_index:
                    answers_index[current_question] = []
                answers_index[current_question].append(answer)

# Строим индекс при запуске
build_index()

@app.get('/test')
async def test(quest: str = None):
    if not quest:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    quest = quest.strip() + '\n'
    true_answers_list = []

    # Ищем вопрос в индексе
    for question, answers in answers_index.items():
        if quest in question:
            true_answers_list.extend(answers)

    if not true_answers_list:
        # Пробуем с заменой символов
        quest_variants = [
            quest.replace('a', 'а').replace('o', 'о'),
            quest.replace('а', 'a').replace('о', 'o')
        ]
        for variant in quest_variants:
            for question, answers in answers_index.items():
                if variant in question:
                    true_answers_list.extend(answers)

    if not true_answers_list:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    return true_answers_list
