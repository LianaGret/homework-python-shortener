import os
import random
import string
import time
from typing import AsyncGenerator, Generator

import docker
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from service.core.config import settings
from service.db.postgres import get_db
from service.main import app


# Test database URL
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")

# Override the database URL for tests
settings.DATABASE_URL = TEST_DATABASE_URL

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


# Dependency override for database session
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# Fixture for the test client
@pytest.fixture(scope="session")
def test_client() -> Generator:
    with TestClient(app) as client:
        yield client


# Fixture for async test client
@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Fixture to set up and tear down the test database
@pytest.fixture(scope="session")
async def setup_test_db():
    # Set up Docker client
    client = docker.from_env()

    # Generate a unique container name
    container_name = f"test_postgres_{generate_random_string(8)}"

    # Start PostgreSQL container
    postgres = client.containers.run(
        "postgres:15",
        name=container_name,
        environment={"POSTGRES_USER": "postgres", "POSTGRES_PASSWORD": "postgres", "POSTGRES_DB": "test_db"},
        ports={"5432/tcp": 5432},
        detach=True,
        remove=True,
    )

    # Wait for PostgreSQL to be ready
    time.sleep(5)

    # Run migrations
    os.system(
        "goose -dir ./migrations postgres 'host=localhost user=postgres password=postgres dbname=test_db sslmode=disable' up"
    )

    yield

    # Stop and remove the container
    postgres.stop()


# Fixture to set up and tear down the test database for each test
@pytest.fixture(autouse=True)
async def setup_and_teardown_tables():
    # Create tables
    async with test_engine.begin() as conn:
        # Clear existing data
        await conn.execute(text("TRUNCATE TABLE link_visits CASCADE"))
        await conn.execute(text("TRUNCATE TABLE links CASCADE"))

    yield

    # Clean up after test
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE link_visits CASCADE"))
        await conn.execute(text("TRUNCATE TABLE links CASCADE"))


# Helper function to generate random strings
def generate_random_string(length=8):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


# Fixture to create a test link
@pytest.fixture
async def create_test_link(async_client):
    response = await async_client.post("/api/v1/links/shorten", json={"original_url": "https://example.com"})
    return response.json()


# Fixture to create a test link with custom alias
@pytest.fixture
async def create_custom_link(async_client):
    custom_alias = generate_random_string(8)
    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/custom", "custom_alias": custom_alias}
    )
    return response.json()


# Fixture to create a test link with expiration
@pytest.fixture
async def create_expiring_link(async_client):
    # Create a link that expires in 1 hour
    import datetime

    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()

    response = await async_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/expiring", "expires_at": expires_at}
    )
    return response.json()
