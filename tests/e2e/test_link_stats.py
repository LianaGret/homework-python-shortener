import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_link_stats(async_client: AsyncClient, create_test_link):
    """Test getting statistics for a link"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Get stats
    stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")

    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert stats_data["short_code"] == short_code
    assert stats_data["original_url"] == "https://example.com"
    assert "created_at" in stats_data
    assert "visit_count" in stats_data
    assert isinstance(stats_data["visit_count"], int)


@pytest.mark.asyncio
async def test_stats_after_visits(async_client: AsyncClient, create_test_link):
    """Test that statistics are updated after visits"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Get initial stats
    initial_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    initial_stats = initial_stats_response.json()
    initial_count = initial_stats["visit_count"]

    # Visit the link multiple times
    visit_count = 3
    for _ in range(visit_count):
        await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    # Get updated stats
    updated_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    updated_stats = updated_stats_response.json()

    assert updated_stats["visit_count"] == initial_count + visit_count
    assert updated_stats["last_visited_at"] is not None


@pytest.mark.asyncio
async def test_stats_for_nonexistent_link(async_client: AsyncClient):
    """Test getting statistics for a nonexistent link"""
    stats_response = await async_client.get("/api/v1/links/nonexistent/stats")
    assert stats_response.status_code == 404  # Not found
