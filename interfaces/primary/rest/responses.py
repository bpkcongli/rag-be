from __future__ import annotations

from typing import Optional

from application.dtos.document_dto import DocumentDTO
from interfaces.primary.rest.schemas import ApiResponse, CamelModel


SUCCESS_CODE = 1000200100
SUCCESS_MESSAGE = "Success!"


class DocumentsData(CamelModel):
    documents: list[DocumentDTO]


DocumentsListResponse = ApiResponse[DocumentsData]
DocumentObjectResponse = ApiResponse[DocumentDTO]


def success_response(*, data: Optional[object] = None):
    # Typed wrappers are used in endpoints; this is mainly for exception handlers.
    return ApiResponse(status={"code": SUCCESS_CODE, "message": SUCCESS_MESSAGE}, data=data)
