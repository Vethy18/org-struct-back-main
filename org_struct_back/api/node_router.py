from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from org_struct_back.api.dtos import Error, Meta, NodeCreateDto, NodeDto, ResponseWrapper
from org_struct_back.app.ioc_service import Inject
from org_struct_back.service.domain import NodeService

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
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Sorry")])

    node_dto = NodeDto.model_validate(node_model)

    response.status_code = status.HTTP_200_OK
    return ResponseWrapper(meta=Meta(success=True), data=node_dto)


@node_router.post("")
def post(
    node_create: NodeCreateDto,
    service: Annotated[NodeService, Inject(NodeService)],
    response: Response,
) -> ResponseWrapper[NodeDto]:
    node_model = service.create(node_create.name, node_create.parent_id)
    if node_model is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Sorry")])

    node_dto = NodeDto.model_validate(node_model)

    response.status_code = status.HTTP_200_OK
    return ResponseWrapper(meta=Meta(success=True), data=node_dto)


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
        return ResponseWrapper(meta=Meta(success=False), errors=[Error(code="000", messsage="Sorry")])

    node_dto = NodeDto.model_validate(node_model)

    response.status_code = status.HTTP_200_OK
    return ResponseWrapper(meta=Meta(success=True), data=node_dto)
