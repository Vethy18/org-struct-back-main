from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Meta(BaseModel):
    success: bool


class Error(BaseModel):
    messsage: str
    code: str


class ResponseWrapper[T: BaseModel](BaseModel):
    data: T | list[T] | None = None
    meta: Meta
    errors: list[Error] = []


class NodeDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    parent_id: UUID | None
    children: dict[str, "NodeDto"]


class NodeCreateDto(BaseModel):
    name: str
    parent_id: UUID | None
