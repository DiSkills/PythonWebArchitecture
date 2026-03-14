from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers

from src import config
from src.adapters.orm import start_mappers, metadata
from src.domain import model
from src.schemas import (
    APIResponseAllocate,
    APIRequestAllocate,
    APIRequestAddBatch,
    Message,
    ErrorMessage,
)
from src.service_layer import services
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork


@asynccontextmanager
async def lifespan(_: FastAPI):
    engine = create_engine(url=config.get_postgres_uri())
    metadata.create_all(bind=engine)
    start_mappers()
    yield
    clear_mappers()
    metadata.drop_all(bind=engine)


app = FastAPI(lifespan=lifespan)


@app.post(
    "/allocate",
    status_code=201,
    response_model=APIResponseAllocate,
    responses={400: {"model": ErrorMessage}},
)
def allocate_endpoint(request: APIRequestAllocate):
    try:
        batchref = services.allocate(
            orderid=request.orderid, sku=request.sku, qty=request.qty,
            uow=SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"batchref": batchref}


@app.post("/add_batch", status_code=201, response_model=Message)
def add_batch_endpoint(request: APIRequestAddBatch):
    services.add_batch(
        ref=request.ref, sku=request.sku, qty=request.qty, eta=request.eta,
        uow=SqlAlchemyUnitOfWork(),
    )
    return {"message": "ok"}
