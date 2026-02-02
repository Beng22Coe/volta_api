from fastapi import FastAPI
from daladala_live.core.database import database
from daladala_live.users.router import router as users_router
from daladala_live.auth.router import router as auth_router
from daladala_live.vehicles.router import router as vehicles_router
from daladala_live.vehicles.ws import router as vehicles_ws_router
from daladala_live.nodes.router import router as nodes_router


app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(vehicles_ws_router)
app.include_router(nodes_router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
