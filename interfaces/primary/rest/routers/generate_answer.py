from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from application.services.answer_generation_service import AnswerGenerationService
from interfaces.primary.rest.dependencies import get_answer_generation_service
from interfaces.primary.rest.responses import SUCCESS_CODE, SUCCESS_MESSAGE
from interfaces.primary.rest.schemas import ApiResponse, CamelModel


router = APIRouter(tags=["rag"])


class GenerateAnswerRequest(CamelModel):
    query: str
    document_ids: list[str]


class GenerateAnswerData(CamelModel):
    answer: str


GenerateAnswerResponse = ApiResponse[GenerateAnswerData]


@router.post(
    "/generate-answer",
    response_model=GenerateAnswerResponse,
    response_model_exclude_none=True,
    response_model_by_alias=True,
)
def generate_answer(
    payload: GenerateAnswerRequest,
    svc: AnswerGenerationService = Depends(get_answer_generation_service),
) -> GenerateAnswerResponse:
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="query is required")
    if not payload.document_ids:
        raise HTTPException(status_code=400, detail="documentIds is required")

    answer = svc.generate_answer(query=payload.query, document_ids=payload.document_ids)
    return GenerateAnswerResponse(
        status={"code": SUCCESS_CODE, "message": SUCCESS_MESSAGE},
        data=GenerateAnswerData(answer=answer),
    )


