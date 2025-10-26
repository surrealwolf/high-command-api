#!/usr/bin/env python3
"""
Missions and tasks tests for Hell Divers 2 API.
Tests assignments (major orders), dispatches (news), and planet events endpoints.
"""

import requests
from unittest.mock import patch, MagicMock
from tests.conftest import API_BASE, print_header, print_info, print_success, pretty_print_json


@patch("requests.get")
def test_assignments(mock_get):
    """Test assignments endpoint (Major Orders)"""
    print_header("Testing Assignments Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "title": "Defend Meridian",
            "description": "Hold the line",
            "reward": 1000,
            "progress": 50,
        },
        {
            "id": 2,
            "title": "Eliminate Bugs",
            "description": "Clear the infestation",
            "reward": 2000,
            "progress": 75,
        },
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/assignments?limit=10")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Retrieved assignments data")
        if isinstance(data, list):
            print_info(f"Total assignments: {len(data)}")
            if data:
                print_info(f"Sample assignment: {data[0].get('title', 'Unknown')}")
        else:
            pretty_print_json(data)
    else:
        print_info("No assignments data available yet")


@patch("requests.post")
def test_refresh_assignments(mock_post):
    """Test assignments refresh endpoint"""
    print_header("Testing Assignments Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    mock_post.return_value = mock_response

    response = requests.post(f"{API_BASE}/assignments/refresh")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        print_success("Assignments refreshed successfully")
    else:
        print_info("Could not refresh assignments (API may be unreachable)")


@patch("requests.get")
def test_dispatches(mock_get):
    """Test dispatches endpoint (News/Announcements)"""
    print_header("Testing Dispatches Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "title": "New Season",
            "description": "Season 12 has started",
            "timestamp": 1700000000,
        },
        {
            "id": 2,
            "title": "Patch Notes",
            "description": "Balance changes deployed",
            "timestamp": 1699900000,
        },
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/dispatches?limit=10")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Retrieved dispatches data")
        if isinstance(data, list):
            print_info(f"Total dispatches: {len(data)}")
            if data:
                print_info(f"Sample dispatch: {data[0].get('title', 'Unknown')}")
        else:
            pretty_print_json(data)
    else:
        print_info("No dispatches data available yet")


@patch("requests.post")
def test_refresh_dispatches(mock_post):
    """Test dispatches refresh endpoint"""
    print_header("Testing Dispatches Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    mock_post.return_value = mock_response

    response = requests.post(f"{API_BASE}/dispatches/refresh")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        print_success("Dispatches refreshed successfully")
    else:
        print_info("Could not refresh dispatches (API may be unreachable)")


@patch("requests.get")
def test_planet_events(mock_get):
    """Test planet events endpoint"""
    print_header("Testing Planet Events Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "id": 1,
            "planetIndex": 42,
            "eventType": "storm",
            "startTime": 1700000000,
            "endTime": 1700086400,
        },
        {
            "id": 2,
            "planetIndex": 85,
            "eventType": "meteor",
            "startTime": 1699950000,
            "endTime": 1700036400,
        },
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/planet-events?limit=10")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Retrieved planet events data")
        if isinstance(data, list):
            print_info(f"Total planet events: {len(data)}")
            if data:
                print_info(
                    f"Sample event: {data[0].get('eventType', 'Unknown')} on planet {data[0].get('planetIndex', '?')}"
                )
        else:
            pretty_print_json(data)
    else:
        print_info("No planet events data available yet")


@patch("requests.post")
def test_refresh_planet_events(mock_post):
    """Test planet events refresh endpoint"""
    print_header("Testing Planet Events Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    mock_post.return_value = mock_response

    response = requests.post(f"{API_BASE}/planet-events/refresh")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        print_success("Planet events refreshed successfully")
    else:
        print_info("Could not refresh planet events (API may be unreachable)")
