from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker

import config
from adapters import repository
from adapters.orm import start_mappers
from domain import model
from schemas import Message
from service_layer import services


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_mappers()
    yield
    clear_mappers()


get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = FastAPI(lifespan=lifespan)


class AllocateEndpointRequest(BaseModel):
    orderid: str
    sku: str
    qty: int


class AllocateEndpointResponse(BaseModel):
    batchref: str


@app.post(
    "/allocate",
    status_code=201,
    response_model=AllocateEndpointResponse,
    responses={400: {"model": Message}},
)
def allocate_endpoint(request: AllocateEndpointRequest):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    try:
        batchref = services.allocate(request.orderid, request.sku, request.qty, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return JSONResponse({"message": str(e)}, status_code=400)
    return {"batchref": batchref}


class AddBatchEndpointRequest(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: None | date


@app.post("/add_batch", status_code=201, response_model=Message)
def add_batch_endpoint(request: AddBatchEndpointRequest):
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    services.add_batch(request.ref, request.sku, request.qty, request.eta, repo, session)
    return {"message": "ok"}
