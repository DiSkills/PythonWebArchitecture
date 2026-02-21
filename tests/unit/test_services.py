import pytest

from src.adapters.repository import FakeRepository
from src.service_layer import services


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("batch1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("order1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "A-REAL-SKU", 100, None, repo, session)

    with pytest.raises(services.InvalidSku, match="Invalid sku NON-EXISTENT-SKU"):
        services.allocate("order1", "NON-EXISTENT-SKU", 10, repo, FakeSession())


def test_allocate_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "OMINOUS-MIRROR", 100, None, repo, session)

    session = FakeSession()
    services.allocate("order1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True
