from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from org_struct_back.storage.entities import NodeEntity


class NodeRepository(ABC):
    @abstractmethod
    def get_by_id(self, session: Session, node_id: UUID, depth: int) -> NodeEntity | None:
        pass

    @abstractmethod
    def get_by_name(self, session: Session, name: str, depth: int) -> NodeEntity | None:
        pass

    @abstractmethod
    def create(self, session: Session, node: NodeEntity) -> None:
        pass


class NodeRepositoryImpl(NodeRepository):
    def get_by_id(self, session: Session, node_id: UUID, depth: int) -> NodeEntity | None:
        node_entity = session.scalars(
            select(NodeEntity)
            .options(selectinload(NodeEntity.children, recursion_depth=depth))
            .filter(NodeEntity.id == node_id)
        ).one()
        return node_entity

    def get_by_name(self, session: Session, name: str, depth: int) -> NodeEntity | None:
        node_entity = session.scalars(
            select(NodeEntity)
            .options(selectinload(NodeEntity.children, recursion_depth=depth))
            .filter(NodeEntity.name == name)
        ).one()
        return node_entity

    def create(self, session: Session, node: NodeEntity) -> None:
        session.add(node)
