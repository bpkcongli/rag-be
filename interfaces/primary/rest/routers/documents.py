from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from application.dtos.document_dto import DocumentDTO
from application.services.document_management_service import DocumentManagementService
from domain.exceptions import StorageError, UnsupportedFileTypeError
from domain.valueobjects.enums import ChunkingStrategy, DocumentStatus
from interfaces.primary.rest.dependencies import get_document_service
from interfaces.primary.rest.background_jobs import run_document_indexing_job
from interfaces.primary.rest.responses import (
    DocumentObjectResponse,
    DocumentsData,
    DocumentsListResponse,
    EmptyResponse,
    SUCCESS_CODE,
    SUCCESS_MESSAGE,
)
from interfaces.primary.rest.schemas import CamelModel


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


class StartIndexingRequest(CamelModel):
    chunking_strategy: ChunkingStrategy | None = None


@router.post(
    "/{documentId}/start-indexing",
    response_model=EmptyResponse,
    response_model_exclude_none=True,
    response_model_by_alias=True,
)
def start_indexing(
    documentId: str,
    payload: StartIndexingRequest | None = None,
    background_tasks: BackgroundTasks = None,
    svc: DocumentManagementService = Depends(get_document_service),
) -> EmptyResponse:
    # default chunkingStrategy
    chunking_strategy = (
        payload.chunking_strategy if payload and payload.chunking_strategy else ChunkingStrategy.SEMANTIC_SLIDING_WINDOW
    )

    # validate doc existence
    doc = svc.repo.get_by_id(documentId)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status == DocumentStatus.INDEXING:
        raise HTTPException(status_code=409, detail="Document is currently indexing")

    # mark as INDEXING immediately
    svc.repo.update_status(document_id=documentId, status=DocumentStatus.INDEXING)

    # schedule background job
    if background_tasks is None:
        # FastAPI will normally inject this. Keep a fallback for direct calls/tests.
        background_tasks = BackgroundTasks()
    background_tasks.add_task(run_document_indexing_job, document_id=documentId, chunking_strategy=chunking_strategy)

    return EmptyResponse(status={"code": SUCCESS_CODE, "message": SUCCESS_MESSAGE})


