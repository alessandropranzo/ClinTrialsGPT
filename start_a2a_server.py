#!/usr/bin/env python3
"""
Startup script for ClinTrialsGPT
Choose between A2A server or Streamlit app
"""

import os
import sys
import subprocess
import argparse


def check_openai_key():
    """Check if OpenAI API key is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try to read from file
        try:
            with open("./src/openai-api-key.txt", "r") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            pass
    
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please set OPENAI_API_KEY environment variable or place your key in src/openai-api-key.txt")
        return False
    
    return True


def start_a2a_server():
    """Start the A2A server"""
    print("🚀 Starting ClinTrialsGPT A2A Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📋 Agent Card: http://localhost:8000/agent-card")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "a2a_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 A2A server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting A2A server: {e}")


def start_streamlit_app():
    """Start the Streamlit app"""
    print("🚀 Starting ClinTrialsGPT Streamlit App...")
    print("📍 App will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "clintrialsgpt.py",
            "--server.port=8501", "--server.address=0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit app: {e}")


def main():
    parser = argparse.ArgumentParser(description="ClinTrialsGPT Startup Script")
    parser.add_argument(
        "--mode", 
        choices=["a2a", "streamlit"], 
        default="a2a",
        help="Choose between A2A server (default) or Streamlit app"
    )
    parser.add_argument(
        "--check-key", 
        action="store_true",
        help="Check if OpenAI API key is configured"
    )
    
    args = parser.parse_args()
    
    print("🏥 ClinTrialsGPT")
    print("=" * 50)
    
    if args.check_key:
        if check_openai_key():
            print("✅ OpenAI API key found")
        else:
            sys.exit(1)
        return
    
    # Check API key before starting
    if not check_openai_key():
        sys.exit(1)
    
    if args.mode == "a2a":
        start_a2a_server()
    else:
        start_streamlit_app()


if __name__ == "__main__":
    main() 