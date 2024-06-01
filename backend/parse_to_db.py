import csv
import json

from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from src.tinkoff_qna.lms.rubert.get_answer import BertModel

def parse_to_db():
    def create_db_engine(db_uri: str) -> Engine:
        engine_options = {
            "echo": False,
            "pool_size": 15,
            "max_overflow": 15,
        }
        return create_engine(db_uri, **engine_options)


    def create_session_maker(engine: Engine) -> sessionmaker[Session]:
        return sessionmaker(engine, autoflush=True, expire_on_commit=False)


    DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres"

    engine = create_db_engine(DB_URI)
    session_factory = create_session_maker(engine)

    model_facade = BertModel(DB_URI, "")

    with open(
            "./train_Tinkoff/dataset.json",
            'r', encoding='utf-8') as f:
        data = json.load(f)['data']
        with session_factory() as session:
            for row in data:
                if len(row['description']) <= 1:
                    continue
                
                emb = model_facade.generate_embeddings([row['title']])
                session.execute(
                    statement=text('INSERT INTO question_answer (question, product, source, url, type, embedding, parent_title, parent_url, answer) VALUES (:question, :product, :source, :url, :type, :embedding, :parent_title, :parent_url, :answer)'), 
                    params={
                        'question': row['title'],
                        'product': row['product'],
                        'source': row['source'],
                        'url': row['url'],
                        'type': row['type'],
                        'embedding': emb,
                        'parent_title': row['parent_title'],
                        'parent_url': row['parent_url'],
                        'answer': row['description']
                    },
                )

            session.commit()
