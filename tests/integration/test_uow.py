from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.domain import model
from src.service_layer.unit_of_work import SqlAlchemyUnitOfWork


def insert_batch(session: Session, ref: str, sku: str, qty: int, eta: None | date):
    session.execute(
        text("INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES (:ref, :sku, :qty, :eta)"),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session: Session, orderid: str, sku: str):
    [[orderlineid]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(
        text("SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id WHERE orderline_id=:orderlineid"),
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, 'batch1', 'HIPSTER-WORKBENCH', 100, None)
    session.commit()

    with (uow := SqlAlchemyUnitOfWork(session_factory)):
        batch = uow.batches.get('batch1')
        line = model.OrderLine('order1', 'HIPSTER-WORKBENCH', 10)
        batch.allocate(line)
        uow.commit()

    batchref = get_allocated_batch_ref(session, 'order1', 'HIPSTER-WORKBENCH')
    assert batchref == 'batch1'


def test_rolls_back_uncommitted_work_by_default(session_factory):
    with (uow := SqlAlchemyUnitOfWork(session_factory)):
        insert_batch(uow.session, 'batch1', 'MEDIUM-PLINTH', 100, None)
    session = session_factory()
    rows = session.execute(text('SELECT * FROM "batches"'))
    assert list(rows) == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    with pytest.raises(MyException):
        with (uow := SqlAlchemyUnitOfWork(session_factory)):
            insert_batch(uow.session, 'batch1', 'MEDIUM-PLINTH', 100, None)
            raise MyException()
    session = session_factory()
    rows = session.execute(text('SELECT * FROM "batches"'))
    assert list(rows) == []
