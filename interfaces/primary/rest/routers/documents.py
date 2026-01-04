from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from application.dtos.document_dto import DocumentDTO
from application.services.document_management_service import DocumentManagementService
from domain.exceptions import StorageError, UnsupportedFileTypeError
from interfaces.primary.rest.dependencies import get_document_service
from interfaces.primary.rest.responses import (
    DocumentObjectResponse,
    DocumentsData,
    DocumentsListResponse,
    SUCCESS_CODE,
    SUCCESS_MESSAGE,
)


router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "",
    response_model=DocumentsListResponse,
    response_model_exclude_none=True,
    response_model_by_alias=True,
)
def list_documents(
    svc: DocumentManagementService = Depends(get_document_service),
) -> DocumentsListResponse:
    docs = svc.list_documents()
    return DocumentsListResponse(
        status={"code": SUCCESS_CODE, "message": SUCCESS_MESSAGE},
        data=DocumentsData(documents=[DocumentDTO.from_domain(d) for d in docs]),
    )


@router.post(
    "",
    response_model=DocumentObjectResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
    response_model_by_alias=True,
)
def upload_document(
    file: UploadFile = File(...),
    svc: DocumentManagementService = Depends(get_document_service),
) -> DocumentObjectResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename is required")

    try:
        doc = svc.upload_document(original_filename=file.filename, file_obj=file.file)
        return DocumentObjectResponse(
            status={"code": SUCCESS_CODE, "message": SUCCESS_MESSAGE},
            data=DocumentDTO.from_domain(doc),
        )
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
