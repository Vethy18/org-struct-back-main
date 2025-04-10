from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_keyed_dict


class Base(DeclarativeBase):
    pass


class NodeEntity(Base):
    __tablename__ = "node"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("node.id"))
    name: Mapped[str] = mapped_column(nullable=False)

    children: Mapped[dict[str, "NodeEntity"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="parent",
        collection_class=attribute_keyed_dict("name"),
    )
    parent: Mapped[Optional["NodeEntity"]] = relationship(back_populates="children", remote_side=id)
