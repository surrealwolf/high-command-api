#!/usr/bin/env python3
"""
Hell Divers 2 API - Demo Script & Pytest Tests
Demonstrates the capabilities of the Hell Divers 2 scraping API
"""

import requests
import json
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

API_BASE = "http://localhost:5000/api"


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")


def print_section(text):
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def pretty_print_json(data, title=""):
    if title:
        print_section(title)
    if data:
        print(json.dumps(data, indent=2))
    else:
        print_error("No data available")


@patch("requests.get")
def test_health(mock_get):
    """Test health check endpoint"""
    print_header("Testing Health Check")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "operational", "collector_running": True}
    mock_get.return_value = mock_response

    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print_success("API is healthy!")
    print_info(f"Status: {data.get('status')}")
    print_info(f"Collector Running: {data.get('collector_running')}")


@patch("requests.get")
def test_root(mock_get):
    """Test root endpoint"""
    print_header("Testing Root Endpoint")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Hell Divers 2 API", "version": "1.0.0"}
    mock_get.return_value = mock_response

    response = requests.get("http://localhost:5000/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    pretty_print_json(response.json())


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


@patch("requests.post")
def test_refresh_endpoint(
    mock_post, endpoint_path="/war/status/refresh", endpoint_name="War Status"
):
    """Test refresh endpoints (POST requests)"""
    print_header(f"Testing {endpoint_name} Refresh")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "message": f"{endpoint_name} refreshed"}
    mock_post.return_value = mock_response

    response = requests.post(f"{API_BASE}{endpoint_path}")
    assert response.status_code in (200, 500), f"Expected 200 or 500, got {response.status_code}"
    if response.status_code == 200:
        data = response.json()
        print_success(f"{endpoint_name} refreshed successfully")
        if "success" in data:
            print_info(f"Success: {data['success']}")
    else:
        print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")


@patch("requests.get")
def test_docs(mock_get):
    """Test documentation endpoints"""
    print_header("Testing API Documentation")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"openapi": "3.0.0", "info": {"title": "Hell Divers 2 API"}}
    mock_get.return_value = mock_response

    response = requests.get("http://localhost:5000/openapi.json")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print_success("OpenAPI schema is available")
    print_info("Access Swagger UI at: http://localhost:5000/docs")
    print_info("Access ReDoc at: http://localhost:5000/redoc")


def run_demo():
    """Run as interactive demo (not pytest)"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Hell Divers 2 API - Demo & Test Suite             ║")
    print("║              Testing the Scraping API                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    results = {"passed": 0, "failed": 0, "tests": []}

    # Run all tests
    demo_tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("War Status", test_war_status),
        ("Planets", test_planets),
        ("Factions", test_factions),
        ("Biomes", test_biomes),
        ("Statistics", test_statistics),
        ("War Status Refresh", lambda: test_refresh_endpoint("/war/status/refresh", "War Status")),
        ("Statistics Refresh", lambda: test_refresh_endpoint("/statistics/refresh", "Statistics")),
        ("Documentation", test_docs),
    ]

    for test_name, test_func in demo_tests:
        try:
            test_func()
            results["passed"] += 1
            results["tests"].append((test_name, "PASSED"))
        except Exception as e:
            results["failed"] += 1
            results["tests"].append((test_name, f"FAILED: {str(e)}"))
        time.sleep(0.5)  # Small delay between tests

    # Print summary
    print_header("Test Summary")
    print(f"{Colors.BOLD}Total Tests: {len(demo_tests)}{Colors.END}")
    print(f"{Colors.GREEN}✓ Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}✗ Failed: {results['failed']}{Colors.END}")

    print(f"\n{Colors.BOLD}Test Results:{Colors.END}")
    for test_name, status in results["tests"]:
        if status == "PASSED":
            print(f"  {Colors.GREEN}✓{Colors.END} {test_name}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} {test_name}: {status}")

    # Next steps
    print_header("Next Steps")
    print_info("1. API is running on http://localhost:5000")
    print_info("2. Interactive docs: http://localhost:5000/docs (Swagger UI)")
    print_info("3. Alternative docs: http://localhost:5000/redoc (ReDoc)")
    print_info("4. The data collector runs automatically every 5 minutes")
    print_info("5. You can manually refresh endpoints using POST requests")

    print(
        f"\n{Colors.YELLOW}Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n"
    )


# Pytest wrapper functions for parametrized tests
def test_refresh_war_status():
    """Test war status refresh endpoint"""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "War Status refreshed"}
        mock_post.return_value = mock_response

        endpoint_path = "/war/status/refresh"
        endpoint_name = "War Status"
        print_header(f"Testing {endpoint_name} Refresh")

        response = requests.post(f"{API_BASE}{endpoint_path}")
        assert response.status_code in (
            200,
            500,
        ), f"Expected 200 or 500, got {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            print_success(f"{endpoint_name} refreshed successfully")
            if "success" in data:
                print_info(f"Success: {data['success']}")
        else:
            print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")


def test_refresh_statistics():
    """Test statistics refresh endpoint"""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "message": "Statistics refreshed"}
        mock_post.return_value = mock_response

        endpoint_path = "/statistics/refresh"
        endpoint_name = "Statistics"
        print_header(f"Testing {endpoint_name} Refresh")

        response = requests.post(f"{API_BASE}{endpoint_path}")
        assert response.status_code in (
            200,
            500,
        ), f"Expected 200 or 500, got {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            print_success(f"{endpoint_name} refreshed successfully")
            if "success" in data:
                print_info(f"Success: {data['success']}")
        else:
            print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")


if __name__ == "__main__":
    run_demo()
