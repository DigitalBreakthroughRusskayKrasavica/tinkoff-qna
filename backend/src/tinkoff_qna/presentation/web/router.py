from dataclasses import dataclass

from fastapi import APIRouter, Depends

from tinkoff_qna.presentation.web.depends_stub import Stub
from tinkoff_qna.services import HelperService


from pydantic import BaseModel

router = APIRouter(prefix='')


class RequestBody(BaseModel):
    title: str


@dataclass
class AssistResponse:
    title: str
    links: list[str]
    
@router.post('/assist')
async def assist(
    body: RequestBody, 
    service: HelperService = Depends(Stub(HelperService))
) -> AssistResponse:
    ans, links = await service.get_answer_with_links(question=body.title)
    return AssistResponse(
        title=ans,
        links=links
    )
