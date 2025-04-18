import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Use an in-memory SQLite database for tests
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for a test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with a test database.
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
    superuser_email = settings.ADMIN_EMAIL
    create_superuser(TestingSessionLocal())

    # Create a token for the superuser
    access_token = create_access_token(superuser_email)

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
