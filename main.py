#!/usr/bin/env python3
"""Main entry point for High Command API"""
import uvicorn
import sys

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=5000,
        reload=True if "--reload" in sys.argv else False
    )
