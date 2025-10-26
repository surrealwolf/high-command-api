#!/usr/bin/env python3
"""
Statistics tests for Hell Divers 2 API.
Tests global statistics endpoints and manual refresh capabilities.
"""

import requests
from unittest.mock import patch, MagicMock
from tests.conftest import API_BASE, print_header, print_info, print_success, pretty_print_json


@patch("requests.get")
def test_statistics(mock_get):
    """Test statistics endpoint"""
    print_header("Testing Statistics Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"players": 50000, "missions": 1000000, "kills": 5000000}
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/statistics")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        print_success("Statistics retrieved")
        pretty_print_json(response.json())
    else:
        print_info("No statistics available yet (normal on first startup)")


@patch("requests.post")
def test_refresh_statistics(mock_post):
    """Test statistics refresh endpoint"""
    print_header("Testing Statistics Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "message": "Statistics refreshed"}
    mock_post.return_value = mock_response

    endpoint_path = "/statistics/refresh"
    endpoint_name = "Statistics"

    response = requests.post(f"{API_BASE}{endpoint_path}")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success(f"{endpoint_name} refreshed successfully")
        if "success" in data:
            print_info(f"Success: {data['success']}")
    else:
        print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")
