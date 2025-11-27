import os
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

def normalize_text(text: str) -> list[str]:
    """Нормализует текст: приводит к нижнему регистру, убирает лишние пробелы, заменяет кириллицу на латиницу и наоборот, кавычки и тире."""
    text = text.strip().lower().replace('\n', ' ').replace('\r', ' ')

    # Замены для кириллических и латинских букв
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    latin_to_cyrillic = {v: k for k, v in cyrillic_to_latin.items()}

    # Замены для кавычек
    quote_replacements = [
        ('"', '«'), ('«', '"'),
        ("'", '‘'), ('‘', "'"),
        ('“', '«'), ('”', '»'),
        ('„', '«'),
    ]

    # Замены для тире
    dash_replacements = [
        (' - ', '-'),  # убираем пробелы вокруг короткого тире
        (' – ', '-'),  # убираем пробелы вокруг длинного тире
        ('-', '—'),    # заменяем короткое тире на длинное
        ('–', '—'),    # заменяем среднее тире на длинное
    ]

    # Применяем замены
    normalized_texts = [text]

    # Замены для тире
    for old, new in dash_replacements:
        normalized_texts.append(normalized_texts[-1].replace(old, new))

    # Замены для кириллических букв на латинские
    cyrillic_text = ''.join([cyrillic_to_latin.get(c, c) for c in normalized_texts[-1]])
    normalized_texts.append(cyrillic_text)

    # Замены для латинских букв на кириллические
    latin_text = ''.join([latin_to_cyrillic.get(c.lower(), c) for c in normalized_texts[-1]])
    normalized_texts.append(latin_text)

    # Замены для кавычек
    for old, new in quote_replacements:
        normalized_texts.append(normalized_texts[-1].replace(old, new))

    return normalized_texts

@app.get('/test')
async def test(quest: str = None):
    if not quest:
        raise HTTPException(status_code=400, detail='Запрос не может быть пустым')

    this_folder = os.getcwd()
    quest = quest.strip() + '\n'

    try:
        with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8-sig") as f:
            text = f.read().replace('\n', ' ').replace('\r', ' ')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Файл с ответами не найден')

    # print(f"Оригинальный запрос: {quest}")
    normalized_quests = normalize_text(quest)
    # print(f"Нормализованные варианты: {normalized_quests}")

    true_answers_list = []
    beg_beg = 0

    for normalized_quest in normalized_quests:
        # print(f"Ищем нормализованный вариант: {normalized_quest}")
        while True:
            begin = text.find(normalized_quest, beg_beg)
            if begin == -1:
                break
            beg_beg = begin + len(normalized_quest)
            # print(f"Найденный индекс: {begin}")
            # print(f"Текст вокруг найденного индекса: {text[begin-50:begin+len(normalized_quest)+50]}")

            num_quest_part = text[text.rfind(' ', 0, begin):begin].strip()
            num_quest = num_quest_part.replace('.', '').strip()
            if not num_quest.isdigit():
                continue

            end1 = text.find('\n\n', begin + len(normalized_quest))
            end2 = text.find(f'{int(num_quest) + 1}. ', begin + len(normalized_quest))
            end = min(filter(lambda val: val > 0, [end1, end2])) if end1 > 0 and end2 > 0 else max(end1, end2)
            if end == -1:
                end = len(text)

            answers = text[begin + len(normalized_quest):end].strip()
            answers_list = [a.strip() for a in answers.split('\n') if a.strip()]
            # print(f"Найденные строки с ответами: {answers_list}")

            for answer in answers_list:
                if answer.startswith('~') or answer.endswith('+'):
                    cleaned_answer = answer.strip()
                    if cleaned_answer.endswith('+'):
                        cleaned_answer = cleaned_answer[:-1].strip()
                        if cleaned_answer.endswith(';'):
                            cleaned_answer = cleaned_answer[:-1].strip()
                        if cleaned_answer.endswith('.'):
                            cleaned_answer = cleaned_answer[:-1].strip()
                        if cleaned_answer.startswith('~'):
                            cleaned_answer = cleaned_answer[1:].strip()
                    true_answers_list.append(cleaned_answer)

    if not true_answers_list:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    return true_answers_list
