from datetime import date

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class ErrorMessage(BaseModel):
    detail: str


class APIRequestAllocate(BaseModel):
    orderid: str
    sku: str
    qty: int


class APIResponseAllocate(BaseModel):
    batchref: str


class APIRequestAddBatch(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: None | date
