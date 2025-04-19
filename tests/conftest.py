import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Use environment variables for test database configuration
TEST_POSTGRES_SERVER = os.getenv("TEST_POSTGRES_SERVER", "test_db")
TEST_POSTGRES_USER = os.getenv("TEST_POSTGRES_USER", "postgres")
TEST_POSTGRES_PASSWORD = os.getenv("TEST_POSTGRES_PASSWORD", "postgres")
TEST_POSTGRES_DB = os.getenv("TEST_POSTGRES_DB", "test_ecommerce")

# Construct the PostgreSQL database URL
TEST_SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{TEST_POSTGRES_USER}:{TEST_POSTGRES_PASSWORD}@{TEST_POSTGRES_SERVER}/{TEST_POSTGRES_DB}"
)

# Create engine and session for testing
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    # Reduce connection pooling for testing
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=5,
    max_overflow=10,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a new database session for a test.

    This fixture does the following:
    1. Create all tables in the test database
    2. Create a new database session
    3. Yield the session for the test
    4. Rollback any changes and close the session
    5. Drop all tables after the test
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Rollback any changes and close the session
        db.rollback()
        db.close()

    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with a test database.

    This overrides the get_db dependency with our test database session.
    """

    # Override the get_db dependency with our test db
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Remove the override after the test
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def superuser_token_headers(client):
    """
    Create a superuser and return a token for that user.
    """
    from app.core.security import create_access_token
    from app.db.init_db import create_superuser

    # Create a superuser in the test database
    superuser_email = "admin@example.com"  # Use a test admin email
    create_superuser(TestingSessionLocal())

    # Create a token for the superuser
    user = TestingSessionLocal().query(User).filter(User.email == superuser_email).first()
    access_token = create_access_token(str(user.id))

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def normal_user_token_headers(client, db):
    """
    Create a normal user and return a token for that user.
    """
    from app.core.security import create_access_token, get_password_hash
    from app.models.user import User

    # Create a normal user in the test database
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()

    # Create a token for the user
    access_token = create_access_token(str(user.id))

    return {"Authorization": f"Bearer {access_token}"}
