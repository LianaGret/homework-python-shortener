import httpx


def test_redirect_to_original_url(test_client: httpx.Client, create_test_link):
    """Test redirecting to the original URL"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"


def test_redirect_nonexistent_link(test_client: httpx.Client):
    """Test redirecting to a nonexistent link"""
    response = test_client.get("/api/v1/links/nonexistent", follow_redirects=False)

    assert response.status_code == 404


def test_redirect_updates_visit_count(test_client: httpx.Client, create_test_link):
    """Test that redirecting updates the visit count"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    initial_stats_response = test_client.get(f"/api/v1/links/{short_code}/stats")
    initial_stats = initial_stats_response.json()
    initial_count = initial_stats["visit_count"]

    test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    updated_stats_response = test_client.get(f"/api/v1/links/{short_code}/stats")
    updated_stats = updated_stats_response.json()
    updated_count = updated_stats["visit_count"]

    assert updated_count == initial_count + 1
    assert updated_stats["last_visited_at"] is not None


def test_redirect_custom_alias(test_client: httpx.Client, create_custom_link):
    """Test redirecting using a custom alias"""
    link_data = create_custom_link
    short_code = link_data["short_code"]

    response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/custom"
