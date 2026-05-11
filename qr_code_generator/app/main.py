from contextlib import asynccontextmanager

from fastapi import FastAPI

from .blob_storage import ensure_container
from .database import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_container()
    yield


app = FastAPI(title="QR Code Generator Prototype", lifespan=lifespan)
app.include_router(router)
