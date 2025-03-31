import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_redirect_to_original_url(async_client: AsyncClient, create_test_link):
    """Test redirecting to the original URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Get the redirect response
    response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_nonexistent_link(async_client: AsyncClient):
    """Test redirecting to a nonexistent link"""
    response = await async_client.get("/api/v1/links/nonexistent", follow_redirects=False)

    assert response.status_code == 404  # Not found


@pytest.mark.asyncio
async def test_redirect_updates_visit_count(async_client: AsyncClient, create_test_link):
    """Test that redirecting updates the visit count"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Get initial stats
    initial_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    initial_stats = initial_stats_response.json()
    initial_count = initial_stats["visit_count"]

    # Visit the link
    await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    # Get updated stats
    updated_stats_response = await async_client.get(f"/api/v1/links/{short_code}/stats")
    updated_stats = updated_stats_response.json()
    updated_count = updated_stats["visit_count"]

    assert updated_count == initial_count + 1
    assert updated_stats["last_visited_at"] is not None


@pytest.mark.asyncio
async def test_redirect_custom_alias(async_client: AsyncClient, create_custom_link):
    """Test redirecting using a custom alias"""
    link_data = create_custom_link
    short_code = link_data["short_code"]

    # Get the redirect response
    response = await async_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "https://example.com/custom"
