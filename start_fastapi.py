#!/usr/bin/env python3
"""
FastAPI启动脚本
"""

import uvicorn
from api.app import app

if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=5556,
        reload=True,
        log_level="info"
    )
