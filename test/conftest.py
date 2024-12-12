import os
from collections import namedtuple

import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app import Device, create_app, User
from app import db

os.environ["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@localhost/fsa_rollback_per_test_user"
)
os.environ["DEVICE_DB_URI"] = (
    "postgresql://postgres:postgres@localhost/fsa_rollback_per_test_device"
)


@pytest.fixture(scope="session")
def test_client():
    test_app = create_app()
    test_client = test_app.test_client()

    with test_app.app_context():
        yield test_client


@pytest.fixture(scope="session")
def database(test_client):
    db.create_all()

    yield db

    db.drop_all()


TxInfo = namedtuple("TxInfo", "connection,transaction")


@pytest.fixture(autouse=True)
def enable_transactional_tests(database):
    """
    Set up a transaction for each bind_key. The transaction will be rolled back at the end of each test.
    This allows each test to begin with a clean database.

    Helpful links:
    https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    https://github.com/sqlalchemy/sqlalchemy/discussions/12176#discussioncomment-11549627
    """
    tx_per_bind = {}
    for bind_key, engine in database.engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        tx_per_bind[bind_key] = TxInfo(connection, transaction)

    binds = {}
    for mapper in database.Model.registry.mappers:
        bind_key = getattr(mapper.class_, "__bind_key__", None)
        binds[mapper] = tx_per_bind[bind_key].connection

    database.session = scoped_session(
        session_factory=sessionmaker(
            binds=binds,
            join_transaction_mode="create_savepoint",
        )
    )

    yield

    database.session.close()
    for tx in tx_per_bind.values():
        tx.transaction.rollback()
        tx.connection.close()


@pytest.fixture
def userA():
    user = User(id=1, name="Alice")
    db.session.add(user)
    db.session.commit()

    yield user


@pytest.fixture
def userB():
    user = User(id=1, name="Bob")
    db.session.add(user)
    db.session.commit()

    yield user


@pytest.fixture
def small_device():
    device = Device(id=1, memory=1024)
    db.session.add(device)
    db.session.commit()

    yield device


@pytest.fixture
def large_device():
    device = Device(id=1, memory=1024 * 1024)
    db.session.add(device)
    db.session.commit()

    yield device
