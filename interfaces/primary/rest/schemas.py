from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


def _to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )


class StatusSchema(CamelModel):
    code: int
    message: str


T = TypeVar("T")


class ApiResponse(CamelModel, Generic[T]):
    status: StatusSchema
    data: Optional[T] = None
