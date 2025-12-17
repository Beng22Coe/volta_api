from sqlalchemy import select, update, delete
from daladala_live.core.database import database
from .models import Vehicle


# Create
async def create_vehicle(data):
    query = Vehicle.__table__.insert().values(**data)
    await database.execute(query)
    return data


# Read all
async def get_vehicles():
    query = Vehicle.__table__.select()
    return await database.fetch_all(query)


# Read single
async def get_vehicle_by_id(vehicle_id: int):
    query = Vehicle.__table__.select().where(Vehicle.id == vehicle_id)
    return await database.fetch_one(query)


# Update
async def update_vehicle(vehicle_id: int, data):
    query = update(Vehicle.__table__).where(Vehicle.id == vehicle_id).values(**data)
    await database.execute(query)
    return await get_vehicle_by_id(vehicle_id)


# Delete
async def delete_vehicle(vehicle_id: int):
    query = delete(Vehicle.__table__).where(Vehicle.id == vehicle_id)
    await database.execute(query)
    return {"deleted": vehicle_id}
