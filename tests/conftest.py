#!/usr/bin/env python3
"""
Test suite configuration and shared utilities for Hell Divers 2 API tests.
Contains common testing utilities, mock helpers, and configuration.
"""

import requests
import json
from unittest.mock import MagicMock

API_BASE = "http://localhost:5000/api"


class Colors:
    """ANSI color codes for terminal output"""
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
    """Print a header with borders"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")


def print_section(text):
    """Print a section header"""
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def pretty_print_json(data, title=""):
    """Pretty print JSON data with optional title"""
    if title:
        print_section(title)
    if data:
        print(json.dumps(data, indent=2))
    else:
        print_error("No data available")
