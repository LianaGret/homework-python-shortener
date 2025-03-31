import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_link_creation(async_client: AsyncClient):
    """Test creating multiple links concurrently"""

    # Create 10 links concurrently
    async def create_link(i):
        return await async_client.post(
            "/api/v1/links/shorten", json={"original_url": f"https://example.com/concurrent/{i}"}
        )

    tasks = [create_link(i) for i in range(10)]
    responses = await asyncio.gather(*tasks)

    # Verify all links were created successfully
    for response in responses:
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert data["original_url"].startswith("https://example.com/concurrent/")


@pytest.mark.asyncio
async def test_concurrent_visits(async_client: AsyncClient, create_test_link):
    """Test visiting a link concurrently"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Get initial stats
    initial_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    initial_stats = initial_stats_response.json()
    initial_count = initial_stats["visit_count"]

    # Visit the link concurrently 10 times
    async def visit_link():
        return await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    visit_count = 10
    tasks = [visit_link() for _ in range(visit_count)]
    responses = await asyncio.gather(*tasks)

    # Verify all visits were successful
    for response in responses:
        assert response.status_code == 307

    # Get updated stats
    updated_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    updated_stats = updated_stats_response.json()

    # Verify the visit count increased by the expected amount
    assert updated_stats["visit_count"] == initial_count + visit_count
