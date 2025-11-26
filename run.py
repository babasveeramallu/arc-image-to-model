#!/usr/bin/env python3
"""
Arc - AI Wall Scanner
Simple launcher script
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from app.main import app
    import uvicorn
    import socket
    
    def find_free_port(start_port=8000):
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        return 8000
    
    port = int(os.getenv("PORT", find_free_port(8000)))
    
    print("🏠 Starting Arc - AI Wall Scanner")
    print(f"📡 Server will be available at: http://localhost:{port}")
    print("📱 Open this URL in your browser to start scanning")
    print("🔧 Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try installing dependencies: pip install -r requirements_minimal.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)