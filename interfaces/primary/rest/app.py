from __future__ import annotations

import gc
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from infrastructure.config.settings import get_settings
from infrastructure.secondary.embedding.sentence_transformer_embedding import (
    SentenceTransformerEmbeddingModel,
)
from infrastructure.secondary.llm.transformers_causal_llm import TransformersCausalLLM
from infrastructure.secondary.reranking.cross_encoder_reranker import CrossEncoderReranker
from interfaces.primary.rest.routers.documents import router as documents_router
from interfaces.primary.rest.routers.generate_answer import router as generate_answer_router
from interfaces.primary.rest.schemas import ApiResponse, StatusSchema


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: load once
        app.state.embedding_model = SentenceTransformerEmbeddingModel(
            settings.embedding_model_name, device="cpu"
        )
        app.state.reranker = CrossEncoderReranker(settings.reranker_model_name, device="cpu")
        app.state.llm = TransformersCausalLLM(settings.llm_model_name, device=settings.llm_device)

        try:
            yield
        finally:
            # Shutdown: release memory (best-effort)
            for attr in ("embedding_model", "reranker", "llm"):
                if hasattr(app.state, attr):
                    try:
                        delattr(app.state, attr)
                    except Exception:
                        pass

            gc.collect()

            # Reset CUDA memory if applicable
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
            except Exception:
                pass

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(documents_router)
    app.include_router(generate_answer_router)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Keep a consistent envelope for errors too.
        code = 1000200000 + int(exc.status_code)
        payload = ApiResponse[None](status=StatusSchema(code=code, message=str(exc.detail)))
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(by_alias=True, exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        code = 1000200400
        payload = ApiResponse[None](status=StatusSchema(code=code, message="Validation error"))
        return JSONResponse(
            status_code=422,
            content=payload.model_dump(by_alias=True, exclude_none=True),
        )

    return app
