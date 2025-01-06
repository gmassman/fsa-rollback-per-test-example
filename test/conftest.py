import os
from collections import namedtuple

import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app import db, create_app, Device, User


os.environ["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@localhost/fsa_rollback_per_test_user"
)
os.environ["DEVICE_DB_URI"] = (
    "postgresql://postgres:postgres@localhost/fsa_rollback_per_test_device"
)

TEST_DB_BIND_KEYS = [None, "device_db"]  # only create required databases


@pytest.fixture(scope="session")
def test_app():
    app = create_app()

    yield app


@pytest.fixture
def test_client(test_app):
    with test_app.app_context():
        with test_app.test_client() as test_client:
            yield test_client


@pytest.fixture(scope="session")
def database(test_app):
    with test_app.app_context():
        db.create_all()

        yield db

        db.drop_all()


TxInfo = namedtuple("TxInfo", "connection,transaction")


@pytest.fixture(autouse=True)
def enable_transactional_tests(test_app, database):
    """Set up a transaction for each bind_key. The transaction will be rolled
    back at the end of each test. This allows each test to begin with a clean
    database.

    Helpful links:
    - https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    - https://github.com/sqlalchemy/sqlalchemy/discussions/12176#discussioncomment-11549627
    - https://github.com/pallets-eco/flask-sqlalchemy/issues/1171
    """

    with test_app.app_context():
        engines = db.engines

    tx_per_bind = {}
    for bind_key, engine in engines.items():
        connection = engine.connect()
        transaction = connection.begin()
        tx_per_bind[bind_key] = TxInfo(connection, transaction)

    binds = {}
    for mapper in db.Model.registry.mappers:
        bind_key = getattr(mapper.class_, "__bind_key__", None)
        if bind_key in TEST_DB_BIND_KEYS:
            binds[mapper] = tx_per_bind[bind_key].connection

    db.session = scoped_session(
        session_factory=sessionmaker(
            bind=tx_per_bind[None].connection,
            binds=binds,
            join_transaction_mode="create_savepoint",
            autoflush=False,
        )
    )

    yield

    db.session.close()
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
