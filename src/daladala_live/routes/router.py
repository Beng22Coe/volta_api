import math

from fastapi import APIRouter, HTTPException, Query

from .schemas import (
    RouteCreate,
    RouteListOut,
    RouteNodeCreate,
    RouteNodeListOut,
    RouteNodeOut,
    RouteNodeUpdate,
    RouteOut,
    RouteUpdate,
)
from .service import (
    create_route,
    create_route_node,
    delete_route,
    delete_route_node,
    get_route_by_id,
    get_routes,
    get_routes_count,
    get_route_node_by_id,
    get_route_nodes,
    replace_route_nodes,
    update_route,
    update_route_node,
)

router = APIRouter(prefix="/volta/api/routes", tags=["routes"])


@router.get("", response_model=RouteListOut)
async def list_routes(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
):
    skip = (page - 1) * page_size
    routes = await get_routes(skip=skip, limit=page_size, is_active=is_active)
    total = await get_routes_count(is_active=is_active)
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return RouteListOut(
        items=routes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=RouteOut, status_code=201)
async def register_route(payload: RouteCreate):
    route = await create_route(payload.model_dump())
    return route


@router.put("/{route_id}", response_model=RouteOut)
async def edit_route(route_id: int, payload: RouteUpdate):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    update_data = payload.model_dump(exclude_unset=True)
    updated = await update_route(route_id, update_data)
    return updated


@router.get("/{route_id}", response_model=RouteOut)
async def read_route(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}")
async def remove_route(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return await delete_route(route_id)


@router.get("/{route_id}/nodes", response_model=RouteNodeListOut)
async def list_route_nodes(route_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    nodes = await get_route_nodes(route_id)
    return RouteNodeListOut(items=nodes, total=len(nodes))


@router.post("/{route_id}/nodes", response_model=RouteNodeOut, status_code=201)
async def add_route_node(route_id: int, payload: RouteNodeCreate):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_node = await create_route_node(route_id, payload.model_dump())
    return route_node


@router.put("/{route_id}/nodes", response_model=RouteNodeListOut)
async def replace_route_nodes_endpoint(route_id: int, payload: list[RouteNodeCreate]):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    nodes = await replace_route_nodes(
        route_id, [item.model_dump() for item in payload]
    )
    return RouteNodeListOut(items=nodes, total=len(nodes))


@router.put("/{route_id}/nodes/{route_node_id}", response_model=RouteNodeOut)
async def edit_route_node(
    route_id: int, route_node_id: int, payload: RouteNodeUpdate
):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_node = await get_route_node_by_id(route_node_id)
    if not route_node or route_node["route_id"] != route_id:
        raise HTTPException(status_code=404, detail="Route node not found")

    updated = await update_route_node(
        route_node_id, payload.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/{route_id}/nodes/{route_node_id}")
async def remove_route_node(route_id: int, route_node_id: int):
    route = await get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_node = await get_route_node_by_id(route_node_id)
    if not route_node or route_node["route_id"] != route_id:
        raise HTTPException(status_code=404, detail="Route node not found")

    return await delete_route_node(route_node_id)
