from fastapi import FastAPI
from app.routers import doorcode, auth

app = FastAPI(title="Door Code API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(doorcode.router, prefix="/codes", tags=["codes"])