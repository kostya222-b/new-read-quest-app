import os
import re
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

# Загружаем текст один раз при старте приложения
this_folder = os.getcwd()
file_path = f'{this_folder}/src/myans.txt'

try:
    with open(file_path, 'r', encoding="utf-8") as f:
        TEXT = f.read()
except FileNotFoundError:
    raise RuntimeError(f"Файл {file_path} не найден!")

def clean_answer(answer: str) -> str:
    """Очищает строку ответа от лишних символов."""
    answer = answer.strip()
    if answer[-1] in ('+', ';', '.'):
        answer = answer[:-1].strip()
    if answer.startswith('~'):
        answer = answer[1:].strip()
    return answer

def find_answers(quest: str) -> list[str]:
    """Ищет ответы на вопрос в тексте."""
    quest = quest + '\n'
    true_answers_list = []
    beg_beg = 0

    for _ in range(TEXT.count(quest)):
        begin = TEXT.find(quest, beg_beg)
        if begin == -1:
            break
        beg_beg = begin + len(quest)

        # Ищем номер вопроса
        num_quest_line = TEXT.rfind('\n', 0, begin)
        num_quest = TEXT[num_quest_line:begin].strip()
        num_quest = num_quest.replace('.', '') if '.' in num_quest else num_quest

        # Ищем конец блока с ответами
        end1 = TEXT.find('\n\n', begin + len(quest))
        end2 = TEXT.find(f'{int(num_quest) + 1}. ', begin + len(quest))
        end = min(filter(lambda val: val > 0, [end1, end2]))

        # Получаем блок с ответами
        answers_block = TEXT[begin + len(quest):end].strip()
        answers_list = answers_block.split('\n')

        for answer in answers_list:
            if answer.startswith('~') or answer.endswith('+'):
                if answer.endswith('+'):
                    cleaned_answer = clean_answer(answer)
                    true_answers_list.append(cleaned_answer)

    return true_answers_list

@app.get('/test')
async def test(quest: str = None):
    if not quest:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    # Ищем ответы для оригинального запроса
    true_answers_list = find_answers(quest)

    # Если не найдено, пробуем с заменой символов
    if not true_answers_list:
        quest_variants = [
            quest.replace('a', 'а').replace('o', 'о'),
            quest.replace('а', 'a').replace('о', 'o')
        ]
        for variant in quest_variants:
            true_answers_list = find_answers(variant)
            if true_answers_list:
                break

    if not true_answers_list:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    # Возвращаем оригинальные и варианты ответов
    result = true_answers_list.copy()
    for answer in true_answers_list:
        result.append(answer.replace('a', 'а').replace('o', 'о'))
        result.append(answer.replace('а', 'a').replace('о', 'o'))

    return result
