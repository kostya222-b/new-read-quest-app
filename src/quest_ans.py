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
    """Нормализует текст: убирает лишние пробелы, заменяет кириллицу на латиницу и наоборот, кавычки и тире."""
    text = ' '.join(text.split())

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

    dash_replacements = [
        (' - ', '-'),
        (' – ', '-'),
        ('-', '—'),
        ('–', '—'),
    ]

    normalized_texts = [text]

    for old, new in dash_replacements:
        normalized_texts.append(normalized_texts[-1].replace(old, new))

    cyrillic_text = ''.join([cyrillic_to_latin.get(c, c) for c in normalized_texts[-1]])
    normalized_texts.append(cyrillic_text)

    latin_text = ''.join([latin_to_cyrillic.get(c.lower(), c) for c in normalized_texts[-1]])
    normalized_texts.append(latin_text)

    return normalized_texts

@app.get('/test')
async def test(quest: str = None):
    this_folder = os.getcwd()
    if quest:
        true_answers_list = []
        with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8") as f:
            text = f.read()

        normalized_quests = normalize_text(quest)

        for normalized_quest in normalized_quests:
            if normalized_quest in text:
                begin = text.find(normalized_quest)
                if begin != -1:
                    end = text.find('\n', begin + len(normalized_quest))
                    answers = text[begin + len(normalized_quest):end].strip()

                    answers_list = answers.split('\n')
                    for answer in answers_list:
                        if '+' in answer:
                            cleaned_answer = answer.replace('+', '').strip()
                            cleaned_answer = cleaned_answer.split(')', 1)[-1].strip()
                            true_answers_list.append(cleaned_answer)

        if not true_answers_list:
            raise HTTPException(status_code=404, detail='Нет такого вопроса')
        return true_answers_list
    else:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')
