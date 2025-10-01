#!/usr/bin/env python3
"""
Example usage script for asmblr_backend API.
Demonstrates how to interact with the backend from a client application.
"""

import requests
import json
import time
from typing import Dict, Any


class AsmblrBackendClient:
    """Simple client for interacting with asmblr_backend API."""
    
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the backend is healthy."""
        response = requests.get(f"{self.base_url}/api/health")
        return response.json()
    
    def execute_command_sync(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a command synchronously."""
        payload = {
            "command": command,
            "params": params or {},
            "async": False
        }
        response = requests.post(f"{self.base_url}/api/commands/execute", json=payload)
        return response.json()
    
    def execute_command_async(self, command: str, params: Dict[str, Any] = None) -> str:
        """Execute a command asynchronously and return command ID."""
        payload = {
            "command": command,
            "params": params or {},
            "async": True
        }
        response = requests.post(f"{self.base_url}/api/commands/execute", json=payload)
        result = response.json()
        return result['data']['command_id']
    
    def get_command_status(self, command_id: str) -> Dict[str, Any]:
        """Get the status of an async command."""
        response = requests.get(f"{self.base_url}/api/commands/status/{command_id}")
        return response.json()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        response = requests.get(f"{self.base_url}/api/system/info")
        return response.json()


def main():
    """Demonstrate backend usage."""
    client = AsmblrBackendClient()
    
    print("🚀 asmblr_backend Example Usage")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Health Check:")
    try:
        health = client.health_check()
        print(f"   Status: {health['data']['status']}")
        print(f"   Version: {health['data']['version']}")
        print(f"   Environment: {health['data']['environment']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # 2. Synchronous command execution
    print("\n2. Synchronous Command Execution:")
    try:
        result = client.execute_command_sync("echo 'Hello {name}!'", {"name": "asmblr_backend"})
        if result['success']:
            print(f"   ✅ Command executed successfully")
            print(f"   Output: {result['data']['stdout'].strip()}")
            print(f"   Return code: {result['data']['return_code']}")
        else:
            print(f"   ❌ Command failed: {result['message']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Asynchronous command execution
    print("\n3. Asynchronous Command Execution:")
    try:
        command_id = client.execute_command_async("sleep 2 && echo 'Async task completed!'")
        print(f"   📋 Command queued with ID: {command_id}")
        
        # Poll for completion
        for i in range(10):
            status = client.get_command_status(command_id)
            if status['success']:
                cmd_status = status['data']['status']
                print(f"   Status: {cmd_status}")
                
                if cmd_status == 'completed':
                    print(f"   ✅ Output: {status['data']['stdout'].strip()}")
                    break
                elif cmd_status in ['error', 'timeout']:
                    print(f"   ❌ Command failed: {status['data'].get('error', 'Unknown error')}")
                    break
                else:
                    time.sleep(0.5)
            else:
                print(f"   ❌ Status check failed: {status['message']}")
                break
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. System information
    print("\n4. System Information:")
    try:
        sys_info = client.get_system_info()
        if sys_info['success']:
            data = sys_info['data']
            print(f"   🖥️  Platform: {data['platform']['system']} {data['platform']['release']}")
            print(f"   🐍 Python: {data['platform']['python_version']}")
            print(f"   💾 CPU: {data['resources']['cpu_count']} cores, {data['resources']['cpu_percent']:.1f}% usage")
            print(f"   🧠 Memory: {data['resources']['memory']['percent']:.1f}% used")
        else:
            print(f"   ❌ Failed to get system info: {sys_info['message']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✨ Example completed!")
    print("\n📚 Next steps:")
    print("   - Check the README.md for full API documentation")
    print("   - Explore the /api/health/detailed endpoint for more system info")
    print("   - Try the file operations and data processing modules")
    print("   - Add your own custom API modules")


if __name__ == "__main__":
    main()
