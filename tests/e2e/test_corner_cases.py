import httpx


def test_very_long_url(test_client: httpx.Client):
    """Test creating a link with a very long URL"""

    long_url = f"https://example.com/{'a' * 1980}"

    response = test_client.post("/api/v1/links/shorten", json={"original_url": long_url})

    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == long_url


def test_unicode_in_custom_alias(test_client: httpx.Client):
    """Test creating a link with Unicode characters in the custom alias"""

    response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/unicode", "custom_alias": "unicode😊test"}
    )

    assert response.status_code == 422


def test_maximum_length_custom_alias(test_client: httpx.Client):
    """Test creating a link with a custom alias of maximum allowed length"""

    max_length_alias = "a" * 16

    response = test_client.post(
        "/api/v1/links/shorten",
        json={"original_url": "https://example.com/max-length", "custom_alias": max_length_alias},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == max_length_alias


def test_create_many_links_same_url(test_client: httpx.Client):
    """Test creating many links for the same URL"""
    original_url = "https://example.com/many-links"

    links = []
    for _ in range(5):
        response = test_client.post("/api/v1/links/shorten", json={"original_url": original_url})

        assert response.status_code == 201
        links.append(response.json())

    short_codes = [link["short_code"] for link in links]
    assert len(short_codes) == len(set(short_codes))

    search_response = test_client.get("/api/v1/links/search", params={"original_url": original_url})

    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data["links"]) >= 5


def test_malformed_short_code(test_client: httpx.Client):
    """Test accessing a link with a malformed short code"""

    response = test_client.get("/api/v1/links/!@#$%^&*()", follow_redirects=False)
    assert response.status_code == 404


def test_empty_short_code(test_client: httpx.Client):
    """Test accessing a link with an empty short code"""
    response = test_client.get("/api/v1/links/", follow_redirects=False)
    assert response.status_code in [404, 405]
