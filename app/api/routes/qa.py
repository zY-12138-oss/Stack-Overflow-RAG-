from fastapi import APIRouter, Request

from app.api.schemas.qa import AskRequest, AskResponse

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, request: Request) -> AskResponse:
    qa_service = request.app.state.qa_service
    return qa_service.ask(payload)
