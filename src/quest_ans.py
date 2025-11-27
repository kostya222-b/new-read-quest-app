import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

@app.get('/test')
async def test(quest: str = None):
    this_folder = os.getcwd()
    if quest:
        true_answers_list = []
        with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8") as f:
            text = f.read()

        # Ищем вопрос в тексте
        begin = text.find(quest)
        if begin != -1:
            # Ищем конец вопроса (начало ответа)
            end_of_question = text.find('\n', begin + len(quest))
            if end_of_question == -1:
                raise HTTPException(status_code=404, detail='Нет такого вопроса')

            # Получаем текст после вопроса (ответы)
            answers_section = text[end_of_question:].strip()
            answers_list = answers_section.split('\n')

            # Обрабатываем ответы
            for answer in answers_list:
                if '+' in answer:
                    cleaned_answer = answer.replace('+', '').strip()
                    # Убираем номер ответа (например, "1)")
                    cleaned_answer = cleaned_answer.split(')', 1)[-1].strip()
                    true_answers_list.append(cleaned_answer)
        else:
            raise HTTPException(status_code=404, detail='Нет такого вопроса')

        return true_answers_list
    else:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')
