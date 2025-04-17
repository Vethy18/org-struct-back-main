from typing import Annotated
from uuid import UUID
import os

from fastapi import APIRouter, Query, Response, status
from fastapi.responses import FileResponse

from org_struct_back.api.dtos import Error, Meta, NodeCreateDto, NodeDto, ResponseWrapper
from org_struct_back.app.ioc_service import Inject
from org_struct_back.service.domain import NodeService
from org_struct_back.storage.entities import NodeEntity

node_router = APIRouter(prefix="/api/v1/nodes", tags=["Nodes"])


@node_router.get("")
def get_by_name(
    name: Annotated[str, Query(min_length=1)],
    depth: Annotated[int, Query(ge=1, le=100)],
    service: Annotated[NodeService, Inject(NodeService)],
    response: Response,
) -> ResponseWrapper[NodeDto]:
    node_model = service.find_by_name(name, depth)
    if node_model is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Not found")])
    return ResponseWrapper(meta=Meta(success=True), data=NodeDto.model_validate(node_model))


@node_router.post("")
def post(
    node_create: NodeCreateDto,
    service: Annotated[NodeService, Inject(NodeService)],
    response: Response,
) -> ResponseWrapper[NodeDto]:
    node_model = service.create(node_create.name, node_create.parent_id)
    if node_model is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Creation failed")])
    return ResponseWrapper(meta=Meta(success=True), data=NodeDto.model_validate(node_model))


@node_router.get("/{node_id}")
def get_by_id(
    node_id: UUID,
    depth: Annotated[int, Query(ge=1, le=100)],
    service: Annotated[NodeService, Inject(NodeService)],
    response: Response,
) -> ResponseWrapper[NodeDto]:
    node_model = service.get_by_id(node_id, depth)
    if node_model is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Not found")])
    return ResponseWrapper(meta=Meta(success=True), data=NodeDto.model_validate(node_model))


@node_router.get("/orgs/all")
def get_all_orgs(
    service: Annotated[NodeService, Inject(NodeService)],
) -> list[dict]:
    roots: list[NodeEntity] = service.get_root_nodes()

    def serialize(node: NodeEntity) -> dict:
        return {
            "id": str(node.id),
            "name": node.name,
            "children": [serialize(child) for child in node.children.values()],
        }

    return [serialize(root) for root in roots]


@node_router.get("/orgs/download", response_model=None)
def download_original_file():
    file_path = os.getenv("OSB_STRUCT_READER_CSV_PATH")
    if not file_path or not os.path.exists(file_path):
        return {"detail": "File not found"}
    return FileResponse(
        path=file_path,
        filename="orgs.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
