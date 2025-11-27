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

def normalize_text(text: str) -> list[str]:
    """Нормализует текст: заменяет кириллицу на латиницу и наоборот, кавычки и тире (включая пробелы по краям)."""
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

    # Замены для тире (сначала с пробелами, потом без)
    dash_replacements = [
        (' - ', '—'),  # короткое тире с пробелами
        (' – ', '—'),  # среднее тире с пробелами
        ('-', '—'),    # короткое тире без пробелов
        ('–', '—'),    # среднее тире без пробелов
    ]

    # Применяем замены
    normalized_texts = [text]

    # Замены для тире (сначала с пробелами, потом без)
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
    this_folder = os.getcwd()
    beg_beg = 0
    if quest:
        quest += '\n'
        true_answers_list = []
        with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8") as f:
            text = f.read()
        # Нормализуем запрос
        normalized_quests = normalize_text(quest)
        for normalized_quest in normalized_quests:
            for c in range(text.count(normalized_quest)):
                begin = text.find(normalized_quest, beg_beg)
                beg_beg = begin + len(normalized_quest)
                if begin != -1:
                    num_quest = text[text.rfind('\n', 0, begin):begin-2].strip()
                    num_quest = num_quest.replace('.', '') if '.' in num_quest else num_quest
                    end1 = text.find('\n\n', begin+len(normalized_quest))
                    end2 = text.find(f'{int(num_quest) + 1}. ', begin+len(normalized_quest))
                    end = min(filter(lambda val: val > 0, [end1, end2]))
                    answers = text[begin+len(normalized_quest):end].strip()
                    answers_list = answers.split('\n')
                    for i in answers_list:
                        if i[0] == '~' or i[-1] == '+':
                            if i[-1] == '+':
                                cleaned_i = i[0:-1]
                                cleaned_i = cleaned_i[0:-1] if cleaned_i[-1] == ';' else cleaned_i
                                cleaned_i = cleaned_i[0:-1] if cleaned_i[-1] == '.' else cleaned_i
                                cleaned_i = cleaned_i[1:] if cleaned_i[0] == '~' else cleaned_i
                                cleaned_i = cleaned_i[2:].strip()
                                true_answers_list.append(cleaned_i)
                else:
                    continue
        if not true_answers_list:
            raise HTTPException(status_code=404, detail='Нет такого вопроса')
        return true_answers_list
    else:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')
