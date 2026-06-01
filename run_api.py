#!/usr/bin/env python
"""
Run the FastAPI backend server
"""

import sys
from pathlib import Path
import os

# Change to backend directory
backend_path = Path(__file__).parent / "backend"
os.chdir(backend_path)

# Add backend to path
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path.parent))

if __name__ == "__main__":
    import uvicorn
    
    # Run with reload disabled for Windows compatibility
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )
