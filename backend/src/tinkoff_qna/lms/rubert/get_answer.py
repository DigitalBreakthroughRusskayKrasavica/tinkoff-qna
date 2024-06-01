import asyncio

import aiohttp
from scipy.spatial import distance
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

LLM_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


class BertModel:
    def __init__(self, db_uri: str, llm_api_key: str):
        self.model = SentenceTransformer('cointegrated/rubert-tiny2')
        self.session_factory = sessionmaker(create_engine(db_uri.replace('asyncpg', 'psycopg2')))
        self._llm_api_key = llm_api_key

    def generate_embeddings(self, sentences: list[str]) -> list[float]:
        embs = self.model.encode(sentences)[0]
        return embs.tolist()

    async def get_answer(self, question: str) -> tuple[str, list[str]]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self._llm_api_key}"
        }

        loop = asyncio.get_event_loop()
        best_answers, links = await loop.run_in_executor(None, self.find_best, question)

        text = f"Найди информацию в инструкциях, которая может быть ответом к этому вопросу: {question}?"

        prompt = {
            "modelUri": "gpt://b1g72uajlds114mlufqi/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": """Ты умный помощник, тебя зовут "Русская красавица", ты должен отвечать на вопросы только по инструкциям.
Если в инструкции нет информации ничего не пиши.
Не давай лишней информации, не относящейся к вопросу.
НЕ пиши ничего, кроме ответа на поставленный вопрос.
НЕ давай НИКАКИХ комментариев к инструкциям."""
                },
                *[
                    {
                        "role": "user",
                        "text": "Это инструкция для ответов:\n" + info
                    }
                    for info in best_answers
                ],
                {
                    "role": "user",
                    "text": text
                },
            ]
        }

        async with aiohttp.ClientSession() as session:
            try:
                response = await session.post(LLM_API_URL, headers=headers, json=prompt, timeout=8)
            except asyncio.TimeoutError as e:
                print('An error occured:', e)
                return best_answers[0], links
            result = await response.json()
        try:
            answer = result["result"]["alternatives"][0]["message"]["text"]
        except Exception as e:
            print(answer, e)
            answer = best_answers[0]
        return answer, links


    def find_best(self, sentence: str) -> tuple[str, list[str]]:
        emb = self.model.encode([sentence])[0]

        with self.session_factory() as session:
            rows = session.execute(text(
                "SELECT question, embedding, answer, url FROM question_answer"
            )).all()

        distances = {}
        for i, item in enumerate(rows):
            question, embedding, answer, url = item
            dist = distance.cosine(emb, embedding)
            distances[(question, i)] = (dist, answer, url)

        dists = sorted(list(distances.items()), key=lambda a: a[1][0])[:10]

        closest_one = dists[0]

        # if closest_one[1][0] > 0.1:
        #     return 'Не получилось найти ответ - свяжитесь со специалистом техподдержки', []

        answer_links = set()
        best_answers = [closest_one[1][1]]

        occured_questions = {closest_one[0][0]}
        for question, answer in dists:
            question_text, _ = question
            dist, answer_text, url = answer

            if dist - closest_one[1][0] == 0:
                answer_links.add(url)
            elif dist - closest_one[1][0] < 0.04:
                if question_text not in occured_questions:
                    best_answers.append(answer_text)
                    occured_questions.add(question_text)

        print(sentence)
        print()
        print(best_answers)
        print()
        print()
        print('Distances:', dists)

        return best_answers, answer_links


# model = BertModel("postgresql://postgres:postgres@localhost:5432/postgres")
#
# ans = model.find_best('Каким образом можно переместить контракт из другого банка ?')
#
# print()
# print()
# print(ans)


