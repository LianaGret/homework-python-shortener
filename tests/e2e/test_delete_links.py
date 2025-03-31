import httpx


def test_delete_link(test_client: httpx.Client, create_test_link):
    """Test deleting a link"""
    link_data = create_test_link
    short_code = link_data["short_code"]

    # Delete the link
    delete_response = test_client.delete(f"/api/v1/links/{short_code}")
    assert delete_response.status_code == 204  # No content

    # Verify the link is gone
    get_response = test_client.get(f"/api/v1/links/{short_code}", follow_redirects=False)
    assert get_response.status_code == 404  # Not found


def test_delete_nonexistent_link(test_client: httpx.Client):
    """Test deleting a nonexistent link"""
    delete_response = test_client.delete("/api/v1/links/nonexistent")
    assert delete_response.status_code == 404  # Not found


def test_delete_and_recreate_with_same_alias(test_client: httpx.Client):
    """Test deleting a link and then recreating it with the same custom alias"""
    # Create a link with a custom alias
    custom_alias = "deleteme"
    create_response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/delete-test", "custom_alias": custom_alias}
    )

    assert create_response.status_code == 201

    # Delete the link
    delete_response = test_client.delete(f"/api/v1/links/{custom_alias}")
    assert delete_response.status_code == 204

    # Recreate with the same alias
    recreate_response = test_client.post(
        "/api/v1/links/shorten", json={"original_url": "https://example.com/recreated", "custom_alias": custom_alias}
    )

    assert recreate_response.status_code == 201
    recreated_data = recreate_response.json()
    assert recreated_data["short_code"] == custom_alias
    assert recreated_data["original_url"] == "https://example.com/recreated"
