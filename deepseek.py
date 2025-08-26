from g4f.client import Client

client = Client()

print()

def ask(q):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q}],
        web_search=False
    )
    return response.choices[0].message.content;

def isAd(text):
    prompt = f'Проверь, является ли текст рекламой. Если да - пиши только YES иначе только NO. Пиши YES только если это очевидная реклама, а не часть переписки в чате. Вот текст: {text}'
    res = ask(prompt)

    return res == "YES"
