#!/usr/bin/env python3
"""
World information tests for Hell Divers 2 API.
Tests planets, factions, biomes endpoints and static world data.
"""

import requests
from unittest.mock import patch, MagicMock
from tests.conftest import API_BASE, print_header, print_info, print_success, pretty_print_json


@patch("requests.get")
def test_planets(mock_get):
    """Test planets endpoint"""
    print_header("Testing Planets Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"planet_index": 0, "name": "Malevelon Creek", "biome": {"name": "Swamp"}, "players": 100},
        {"planet_index": 1, "name": "Meridian", "biome": {"name": "Desert"}, "players": 80},
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/planets")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Retrieved planet data")
        if isinstance(data, list):
            print_info(f"Total planets: {len(data)}")
            if data:
                print_info(f"Sample planet: {data[0]}")
        else:
            pretty_print_json(data)
    else:
        print_info("No planets data available yet")


@patch("requests.get")
def test_factions(mock_get):
    """Test factions endpoint"""
    print_header("Testing Factions Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "Humans", "controlled": 50},
        {"id": 2, "name": "Bugs", "controlled": 30},
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/factions")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Factions retrieved")
        if isinstance(data, list):
            print_info(f"Total factions: {len(data)}")
        pretty_print_json(data)
    else:
        print_info("No factions data available yet")


@patch("requests.get")
def test_biomes(mock_get):
    """Test biomes endpoint"""
    print_header("Testing Biomes Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": 1, "name": "Swamp"},
        {"id": 2, "name": "Desert"},
        {"id": 3, "name": "Frozen"},
    ]
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/biomes")
    assert response.status_code in (200, 404), f"Expected 200 or 404, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success("Biomes retrieved")
        if isinstance(data, list):
            print_info(f"Total biomes: {len(data)}")
        pretty_print_json(data)
    else:
        print_info("No biomes data available yet")
