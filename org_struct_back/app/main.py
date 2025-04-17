from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from org_struct_back.api.node_router import node_router
from org_struct_back.app.dependency import build_container
from org_struct_back.settings.server_settings import ServerSettings
from org_struct_back.storage.database import Database
from org_struct_back.settings.struct_reader_settings import StructReaderSettings
from org_struct_back.pkg.struct_reader import StructReaderImpl
from org_struct_back.service.domain import NodeService
from org_struct_back.storage.entities import NodeEntity

container = build_container()
settings: ServerSettings = container.resolve(ServerSettings)
db: Database = container.resolve(Database)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[Any, Any]:
    reader_settings = container.resolve(StructReaderSettings)
    reader = StructReaderImpl(reader_settings)
    root_node = reader.parse()

    def print_tree(node: NodeEntity, indent=0):
        print(" " * indent + f"- {node.name}")
        for child in node.children.values():
            print_tree(child, indent + 2)

    def count_nodes(node: NodeEntity) -> int:
        return 1 + sum(count_nodes(child) for child in node.children.values())

    if root_node:
        print("\n=== ORGANIZATIONAL STRUCTURE START ===")
        print_tree(root_node)
        total = count_nodes(root_node)
        print(f"Total parsed nodes from Excel: {total}")
        print("=== ORGANIZATIONAL STRUCTURE END ===\n")

        service: NodeService = container.resolve(NodeService)

        # Optional check to avoid re-adding if already populated
        with db() as session:
            existing = session.query(NodeEntity).count()
            if existing >= total:
                print("[!] Data may already be populated. Skipping insert.")
            else:
                print("[+] Persisting to database...")

                def persist_tree(node: NodeEntity, parent_id=None):
                    new_node = service.create(node.name, parent_id)
                    for child in node.children.values():
                        persist_tree(child, new_node.id)

                persist_tree(root_node)
    else:
        print("\n[!] No root node was parsed — please check the Excel path or format.\n")

    yield
    db.shutdown()


app = FastAPI(title=settings.name, lifespan=lifespan)
app.state.ioc_container = container
app.include_router(node_router)
