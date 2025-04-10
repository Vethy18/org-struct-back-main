from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NodeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    parent_id: UUID | None
    children: dict[str, "NodeModel"]
