import csv

from sentence_transformers import SentenceTransformer

from scipy.spatial import distance

from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker


class BertModel:
    def __init__(self, db_uri: str):
        self.model = SentenceTransformer('cointegrated/rubert-tiny2')
        self.session_factory = sessionmaker(create_engine(db_uri.replace('asyncpg', 'psycopg2')))

    def generate_embeddings(self, sentences: list[str]) -> list[float]:
        embs = self.model.encode(sentences)[0]
        return embs.tolist()

    def add_new(self, answer: str):
        emb = self.generate_embeddings([answer])

        with self.session_factory() as session:
            session.execute(text(
                "INSERT INTO answers (answer, embedding) VALUES (:a, :e) RETURNING id"
            ), {'a': answer, 'e': emb})
            session.commit()

    def find_best(self, sentence: str) -> tuple[str, list[str]]: 
        emb = self.model.encode([sentence])[0]

        with self.session_factory() as session:
            questions = session.execute(text(
                "SELECT question, embedding, answer, url FROM question_answer"
            )).all()

        distances = {}
        for i, item in enumerate(questions):
            question, embedding, answer, url = item
            dist = distance.cosine(emb, embedding)
            distances[(question, i)] = (dist, answer, url)

        dists = sorted(list(distances.items()), key=lambda a: a[1][0])[:10]
        closest_one = dists[0]

        print(dists)

        answer_links = set()
        final_answer = closest_one[1][1]

        occured_questions = {closest_one[0][0]}
        for question, answer in dists:
            question_text, _ = question
            dist, answer_text, url = answer
            
            if dist - closest_one[1][0] == 0:
                answer_links.add(url)
            elif dist - closest_one[1][0] < 0.04:
                if question_text not in occured_questions:
                    final_answer += f'\n\n{answer_text}'
                    occured_questions.add(question_text)

        return final_answer, answer_links


# model = BertModel("postgresql://postgres:postgres@localhost:5432/postgres")

# ans = model.find_best('Каким образом можно переместить контракт из другого банка ?')

# print()
# print()
# print(ans)


