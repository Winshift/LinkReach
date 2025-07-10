#!/usr/bin/env python3
"""
LinkedIn Connections Filter - Startup Script
"""

import uvicorn
import os
import sys
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is not set")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    return True

def main():
    """Main startup function"""
    print("🚀 Starting LinkedIn Connections Filter...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ Error: main.py not found")
        print("Please ensure you're in the correct directory")
        sys.exit(1)
    
    print("✅ Environment check passed")
    print("🌐 Starting server at http://localhost:8000")
    print("📖 API documentation available at http://localhost:8000/api/docs")
    print("🔄 Press Ctrl+C to stop the server")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 