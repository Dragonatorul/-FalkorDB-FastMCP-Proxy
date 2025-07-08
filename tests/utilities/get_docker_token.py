#!/usr/bin/env python3
"""
Get a valid Bearer token from the running Docker container's RSA keypair.
"""
import docker
import json
import sys

def get_docker_token():
    """Execute Python code inside Docker container to get a valid token"""
    try:
        client = docker.from_env()
        container = client.containers.get('fastmcp-proxy')
        
        # Python code to generate token using container's keypair
        python_code = '''
import sys
sys.path.append("/app/src")
from fastmcp_proxy import key_pair

token = key_pair.create_token(
    subject="test-user",
    issuer="https://falkordb-fastmcp-proxy", 
    audience="falkordb-mcp-server",
    scopes=["read", "write"],
    expires_in_seconds=3600
)
print(f"Bearer {token}")
'''
        
        result = container.exec_run(f'python3 -c "{python_code}"', workdir='/app')
        if result.exit_code == 0:
            token = result.output.decode().strip()
            print(f"✅ Generated token from Docker container:")
            print(token)
            return token
        else:
            print(f"❌ Error generating token: {result.output.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error accessing Docker container: {e}")
        return None

if __name__ == "__main__":
    get_docker_token()