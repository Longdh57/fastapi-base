import logging
from pydantic import BaseModel, conint
from abc import ABC, abstractmethod
from typing import Optional, Generic, Sequence, Type, TypeVar

from sqlalchemy import asc, desc
from sqlalchemy.orm import Query
from pydantic.generics import GenericModel
from contextvars import ContextVar

from app.schemas.sche_base import ResponseSchemaBase, MetadataSchema
from app.helpers.exception_handler import CustomException

T = TypeVar("T")
C = TypeVar("C")

logger = logging.getLogger()


class PaginationParams(BaseModel):
    page_size: Optional[conint(gt=0, lt=1001)] = 10
    page: Optional[conint(gt=0)] = 1
    sort_by: Optional[str] = 'id'
    order: Optional[str] = 'desc'


class BasePage(ResponseSchemaBase, GenericModel, Generic[T], ABC):
    data: Sequence[T]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    @abstractmethod
    def create(cls: Type[C], code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> C:
        pass  # pragma: no cover


class Page(BasePage[T], Generic[T]):
    metadata: MetadataSchema

    @classmethod
    def create(cls, code: str, message: str, data: Sequence[T], metadata: MetadataSchema) -> "Page[T]":
        return cls(
            code=code,
            message=message,
            data=data,
            metadata=metadata
        )


PageType: ContextVar[Type[BasePage]] = ContextVar("PageType", default=Page)


def paginate(model, query: Query, params: Optional[PaginationParams]) -> BasePage:
    code = '200'
    message = 'Success'

    try:
        total = query.count()

        if params.order:
            direction = desc if params.order == 'desc' else asc
            query = query.order_by(direction(getattr(model, params.sort_by)))

        data = query.limit(params.page_size).offset(params.page_size * (params.page-1)).all()

        metadata = MetadataSchema(
            current_page=params.page,
            page_size=params.page_size,
            total_items=total
        )

    except Exception as e:
        raise CustomException(http_code=500, code='500', message=str(e))

    return PageType.get().create(code, message, data, metadata)
