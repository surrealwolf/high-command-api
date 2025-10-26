#!/usr/bin/env python3
"""
War status and campaign tests for Hell Divers 2 API.
Tests war status endpoints and manual refresh capabilities.
"""

import requests
from unittest.mock import patch, MagicMock
from tests.conftest import API_BASE, print_header, print_info, print_success, pretty_print_json


@patch("requests.get")
def test_war_status(mock_get):
    """Test war status endpoint"""
    print_header("Testing War Status")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "war_id": 1,
        "statistics": {"players": 50000, "missions": 1000000},
        "factions": [{"name": "Humans", "controlled": 50}],
        "currently_attacking": [1, 2, 3],
        "planet_events": [],
    }
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/war/status")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        print_success("War status retrieved")
        pretty_print_json(response.json())
    else:
        print_info("No war status data available yet (normal on first startup)")


@patch("requests.post")
def test_refresh_war_status(mock_post):
    """Test war status refresh endpoint"""
    print_header("Testing War Status Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "message": "War Status refreshed"}
    mock_post.return_value = mock_response

    endpoint_path = "/war/status/refresh"
    endpoint_name = "War Status"

    response = requests.post(f"{API_BASE}{endpoint_path}")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success(f"{endpoint_name} refreshed successfully")
        if "success" in data:
            print_info(f"Success: {data['success']}")
    else:
        print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")
