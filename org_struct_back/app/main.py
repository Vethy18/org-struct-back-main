from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from org_struct_back.api.node_router import node_router
from org_struct_back.app.dependency import build_container
from org_struct_back.settings.server_settings import ServerSettings
from org_struct_back.storage.database import Database

container = build_container()
settings: ServerSettings = container.resolve(ServerSettings)
db: Database = container.resolve(Database)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, Any]:
    yield
    db.shutdown()


app = FastAPI(title=settings.name, lifespan=lifespan)

app.state.ioc_container = container

app.include_router(node_router)
