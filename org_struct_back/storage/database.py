from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from org_struct_back.pkg.struct_reader import StructReader
from org_struct_back.settings.database_settings import DatabaseSettings
from org_struct_back.storage.entities import Base, NodeEntity


class Database(ABC):
    @abstractmethod
    def __call__(self) -> Generator[Session, Any]:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass


class DatabaseImpl(Database):
    def __init__(self, settings: DatabaseSettings, reader: StructReader) -> None:
        self._engine = create_engine(settings.connection_string, echo=False)
        self._scoped_session = scoped_session(sessionmaker(bind=self._engine))
        Base.metadata.create_all(self._engine)

        node_entity = reader.parse()
        if node_entity is not None:
            self._fill_database(node_entity)

    @contextmanager
    def __call__(self) -> Generator[Session, Any]:
        session = self._scoped_session()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def shutdown(self) -> None:
        self._scoped_session.remove()
        self._engine.dispose()

    def _fill_database(self, node_entity: NodeEntity) -> None:
        with self() as session:
            session.add(node_entity)
            session.commit()
            for child_name in node_entity.children:
                self._fill_database(node_entity.children[child_name])
