from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from sqlalchemy.orm import selectinload

from org_struct_back.service.models import NodeModel
from org_struct_back.storage.database import Database
from org_struct_back.storage.entities import NodeEntity
from org_struct_back.storage.node_repository import NodeRepository


class NodeService(ABC):
    @abstractmethod
    def get_by_id(self, node_id: UUID, depth: int) -> NodeModel | None:
        pass

    @abstractmethod
    def find_by_name(self, node_name: str, depth: int) -> NodeModel | None:
        pass

    @abstractmethod
    def create(self, node_name: str, parent_id: UUID | None) -> NodeModel:
        pass

    @abstractmethod
    def get_root_node(self) -> NodeEntity | None:
        pass

    @abstractmethod
    def get_root_nodes(self) -> list[NodeEntity]:
        pass


class NodeServiceImpl(NodeService):
    def __init__(self, repository: NodeRepository, db: Database) -> None:
        self._repository = repository
        self._db = db

    def get_by_id(self, node_id: UUID, depth: int) -> NodeModel | None:
        with self._db() as session:
            node_entity = self._repository.get_by_id(session, node_id, depth)
            return NodeModel.model_validate(node_entity)

    def find_by_name(self, name: str, depth: int) -> NodeModel | None:
        with self._db() as session:
            node_entity = self._repository.get_by_name(session, name, depth)
            return NodeModel.model_validate(node_entity)

    def create(self, name: str, parent_id: UUID | None) -> NodeModel:
        with self._db() as session:
            node_entity = NodeEntity(id=uuid4(), name=name, parent_id=parent_id)
            self._repository.create(session, node_entity)
            session.commit()
            return NodeModel.model_validate(node_entity)

    def get_root_node(self) -> NodeEntity | None:
        with self._db() as session:
            return session.query(NodeEntity)\
                .options(selectinload(NodeEntity.children).selectinload(NodeEntity.children))\
                .filter(NodeEntity.parent_id == None)\
                .first()

    def get_root_nodes(self) -> list[NodeEntity]:
        with self._db() as session:
            return session
