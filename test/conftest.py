import os

import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app, User
from app import db

os.environ[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@localhost/fsa_rollback_per_test"


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


@pytest.fixture(autouse=True)
def enable_transactional_tests(database):
    """https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites"""
    connection = database.engine.connect()
    transaction = connection.begin()

    database.session = scoped_session(
        session_factory=sessionmaker(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
    )

    yield

    database.session.close()
    transaction.rollback()
    connection.close()


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
