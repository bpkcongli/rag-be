from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from infrastructure.config.settings import get_settings
from interfaces.primary.rest.routers.documents import router as documents_router
from interfaces.primary.rest.schemas import ApiResponse, StatusSchema


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)
    app.include_router(documents_router)

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
