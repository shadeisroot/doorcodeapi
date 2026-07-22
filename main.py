from fastapi import FastAPI
from app.routers import doorcode

app = FastAPI(title="Door Code API")

app.include_router(doorcode.router, prefix="/codes", tags=["codes"])