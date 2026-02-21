from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import clear_mappers

from src.adapters.orm import start_mappers
from src.domain import model
from src.schemas import Message
from src.service_layer import services
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork


@asynccontextmanager
async def lifespan(_: FastAPI):
    start_mappers()
    yield
    clear_mappers()


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
    try:
        batchref = services.allocate(request.orderid, request.sku, request.qty, SqlAlchemyUnitOfWork())
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
    services.add_batch(request.ref, request.sku, request.qty, request.eta, SqlAlchemyUnitOfWork())
    return {"message": "ok"}
