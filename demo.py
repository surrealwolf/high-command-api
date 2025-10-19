#!/usr/bin/env python3
"""
Hell Divers 2 API - Demo Script
Demonstrates the capabilities of the Hell Divers 2 scraping API
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5000/api"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

def test_health():
    """Test health check endpoint"""
    print_header("Testing Health Check")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Collector Running: {data.get('collector_running')}")
            return True
        else:
            print_error(f"API returned status code {response.status_code}")
            return False
    except requests.ConnectionError:
        print_error("Could not connect to API. Make sure it's running on port 5000")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_root():
    """Test root endpoint"""
    print_header("Testing Root Endpoint")
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            pretty_print_json(response.json())
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_war_status():
    """Test war status endpoint"""
    print_header("Testing War Status")
    try:
        response = requests.get(f"{API_BASE}/war/status")
        if response.status_code == 200:
            print_success("War status retrieved")
            pretty_print_json(response.json())
            return True
        elif response.status_code == 404:
            print_info("No war status data available yet (normal on first startup)")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_planets():
    """Test planets endpoint"""
    print_header("Testing Planets Endpoint")
    try:
        response = requests.get(f"{API_BASE}/planets")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved planet data")
            if isinstance(data, list):
                print_info(f"Total planets: {len(data)}")
                if data:
                    print_info(f"Sample planet: {data[0]}")
            else:
                pretty_print_json(data)
            return True
        elif response.status_code == 404:
            print_info("No planets data available yet")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_statistics():
    """Test statistics endpoint"""
    print_header("Testing Statistics Endpoint")
    try:
        response = requests.get(f"{API_BASE}/statistics")
        if response.status_code == 200:
            print_success("Statistics retrieved")
            pretty_print_json(response.json())
            return True
        elif response.status_code == 404:
            print_info("No statistics available yet (normal on first startup)")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_factions():
    """Test factions endpoint"""
    print_header("Testing Factions Endpoint")
    try:
        response = requests.get(f"{API_BASE}/factions")
        if response.status_code == 200:
            data = response.json()
            print_success("Factions retrieved")
            if isinstance(data, list):
                print_info(f"Total factions: {len(data)}")
            pretty_print_json(data)
            return True
        elif response.status_code == 404:
            print_info("No factions data available yet")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_biomes():
    """Test biomes endpoint"""
    print_header("Testing Biomes Endpoint")
    try:
        response = requests.get(f"{API_BASE}/biomes")
        if response.status_code == 200:
            data = response.json()
            print_success("Biomes retrieved")
            if isinstance(data, list):
                print_info(f"Total biomes: {len(data)}")
            pretty_print_json(data)
            return True
        elif response.status_code == 404:
            print_info("No biomes data available yet")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_refresh_endpoint(endpoint_path, endpoint_name):
    """Test refresh endpoints (POST requests)"""
    print_header(f"Testing {endpoint_name} Refresh")
    try:
        response = requests.post(f"{API_BASE}{endpoint_path}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"{endpoint_name} refreshed successfully")
            if 'success' in data:
                print_info(f"Success: {data['success']}")
            return True
        elif response.status_code == 500:
            print_info(f"Could not fetch {endpoint_name} from source (API may be unreachable)")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def test_docs():
    """Test documentation endpoints"""
    print_header("Testing API Documentation")
    try:
        # Test OpenAPI schema
        response = requests.get("http://localhost:5000/openapi.json")
        if response.status_code == 200:
            print_success("OpenAPI schema is available")
            print_info("Access Swagger UI at: http://localhost:5000/docs")
            print_info("Access ReDoc at: http://localhost:5000/redoc")
            return True
    except Exception as e:
        print_error(f"Error: {str(e)}")
    return False

def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Hell Divers 2 API - Demo & Test Suite             ║")
    print("║              Testing the Scraping API                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }

    # Run all tests
    tests = [
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

    for test_name, test_func in tests:
        try:
            if test_func():
                results["passed"] += 1
                results["tests"].append((test_name, "PASSED"))
            else:
                results["failed"] += 1
                results["tests"].append((test_name, "FAILED"))
        except Exception as e:
            results["failed"] += 1
            results["tests"].append((test_name, f"ERROR: {str(e)}"))
        time.sleep(0.5)  # Small delay between tests

    # Print summary
    print_header("Test Summary")
    print(f"{Colors.BOLD}Total Tests: {len(tests)}{Colors.END}")
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

    print(f"\n{Colors.YELLOW}Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")

if __name__ == "__main__":
    main()
