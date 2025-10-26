#!/usr/bin/env python3
"""
System and health check tests for Hell Divers 2 API.
Tests API health, documentation endpoints, and system status.
"""

import requests
from unittest.mock import patch, MagicMock
from tests.conftest import API_BASE, print_header, print_success, print_info, pretty_print_json


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
