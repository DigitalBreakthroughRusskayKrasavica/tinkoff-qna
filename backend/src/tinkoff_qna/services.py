import asyncio
import os

from sqlalchemy import select

from tinkoff_qna.lms.rubert.get_answer import BertModel
from tinkoff_qna.database.repository import DbRepository

from redis.asyncio import Redis

from tinkoff_qna.models import User


class HelperService:


    def __init__(self, db_repo: DbRepository, rubert_model: BertModel):
        self.db_repo = db_repo
        self.rubert_model = rubert_model

        if not os.path.exists('current_model'):
            with open('current_model', 'w') as f:
                f.write("rubert")


    async def get_answer_with_links(self, question: str) -> tuple[str, list[str]]:
        loop = asyncio.get_event_loop()

        answer, links = await loop.run_in_executor(None, self.rubert_model.find_best, question)
        return answer, links

    async def add_new_pair(self, question, category, answer, url):
        embeddings = self.rubert_model.generate_embeddings([question])
        await self.db_repo.add_new_pair(question, embeddings, category, answer, url)

    async def find_unassigned_curator(self, redis_connection: Redis) -> int:
        curators = await self.db_repo.get_all_support_technicians()

        for curator_id in curators:
            item = await redis_connection.get(curator_id)
            if item is None:
                return curator_id
        return 0

    async def change_role(self, user_id, role):
        await self.db_repo.change_role(user_id, role)
