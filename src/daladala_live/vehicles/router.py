from fastapi import APIRouter, HTTPException
from .schemas import VehicleCreate, VehicleUpdate, VehicleOut
from .service import (
    create_vehicle,
    get_vehicles,
    get_vehicle_by_id,
    update_vehicle,
    delete_vehicle,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("", response_model=VehicleOut)
async def register_vehicle(payload: VehicleCreate):
    vehicle = await create_vehicle(payload.dict())
    return vehicle


@router.get("", response_model=list[VehicleOut])
async def list_vehicles():
    return await get_vehicles()


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def read_vehicle(vehicle_id: int):
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleOut)
async def edit_vehicle(vehicle_id: int, payload: VehicleUpdate):
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    updated = await update_vehicle(vehicle_id, payload.dict(exclude_unset=True))
    return updated


@router.delete("/{vehicle_id}")
async def remove_vehicle(vehicle_id: int):
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return await delete_vehicle(vehicle_id)
