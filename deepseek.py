import requests
import json

API_KEY = ""  # внутри скобок свой апи ключ отсюда https://openrouter.ai/settings/keys
with open('deepsecret.txt', 'r') as file:
    API_KEY = file.read().replace('\n', '')

MODEL = "deepseek/deepseek-r1"


def process_content(content):
    return content.replace('<think>', '').replace('</think>', '')


def chat_stream(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""

        full_response = []

        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = process_content(content)
                            full_response.append(cleaned)
                except:
                    pass

        print()  # Перенос строки после завершения потока
        return ''.join(full_response)

def isAd(text):
    prompt = f'Проверь, является ли текст рекламой. Если да - пиши только YES иначе только NO. Пиши YES только если это очевидная реклама, а не часть переписки. Вот текст: {text}'
    res = chat_stream(prompt)

    return res == "YES"
