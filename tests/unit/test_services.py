import pytest

from src.adapters.repository import IRepository
from src.domain.model import Batch
from src.service_layer import services
from src.service_layer.unit_of_work import IUnitOfWork


class FakeRepository(IRepository):
    def __init__(self, batches: list[Batch]):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[Batch]:
        return list(self._batches)


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("batch1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("order1", "COMPLICATED-LAMP", 10, uow)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "A-REAL-SKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NON-EXISTENT-SKU"):
        services.allocate("order1", "NON-EXISTENT-SKU", 10, uow)


def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch("batch1", "OMINOUS-MIRROR", 100, None, uow)
    services.allocate("order1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed
