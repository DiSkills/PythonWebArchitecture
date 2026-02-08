import pytest

from adapters.repository import FakeRepository
from domain import model
from service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine("order1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "batch1"


def test_error_for_invalid_sku():
    line = model.OrderLine("order1", "NON-EXISTENT-SKU", 10)
    batch = model.Batch("batch1", "A-REAL-SKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NON-EXISTENT-SKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine("order1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("batch1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True
