from dataclasses import dataclass

from fastapi import APIRouter, Depends

from tinkoff_qna.presentation.web.depends_stub import Stub
from tinkoff_qna.services import HelperService

router = APIRouter(prefix='')

@dataclass
class AssistResponse:
    title: str
    links: list[str]
    
@router.post('/assist')
async def assist(
    title: str, 
    service: HelperService = Depends(Stub(HelperService))
) -> AssistResponse:
    ans, links = await service.get_answer(question=title)
    return
