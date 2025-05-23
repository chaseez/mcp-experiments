"""
Simple test to verify the MCP server accepts multiple concurrent HTTP connections.
This test focuses on connection establishment rather than full MCP protocol interaction.
"""

import asyncio
import aiohttp
import time

async def test_concurrent_connections():
    """Test that multiple clients can connect to the server simultaneously"""
    print("Testing concurrent HTTP connections to MCP server...")
    print("=" * 50)
    
    start_time = time.time()
    
    async def connect_client(client_id: int):
        """Test a single client connection"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                print(f"Client {client_id}: Attempting connection...")
                
                # Connect to the SSE endpoint
                async with session.get('http://localhost:8000/sse') as response:
                    print(f"Client {client_id}: Connected! Status: {response.status}")
                    
                    # Read a few lines to confirm we're getting SSE data
                    line_count = 0
                    async for line in response.content:
                        if line_count >= 3:  # Read first few lines
                            break
                        line_count += 1
                        print(f"Client {client_id}: Received: {line.decode().strip()[:50]}...")
                    
                return f"Client {client_id}: SUCCESS - Connected and received data"
                    
        except Exception as e:
            return f"Client {client_id}: ERROR - {str(e)}"
    
    # Create 3 concurrent connection tasks
    tasks = [connect_client(i + 1) for i in range(3)]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    
    print("=" * 50)
    print(f"Test completed in {end_time - start_time:.2f}s")
    print("\nResults:")
    for result in results:
        print(f"  - {result}")
    
    # Count successes
    success_count = sum(1 for result in results if "SUCCESS" in str(result))
    print(f"\nSummary: {success_count}/3 clients connected successfully")
    
    return success_count

async def main():
    print("Starting MCP Server Multi-Client Connection Test")
    print("This test verifies the server can handle concurrent connections\n")
    
    try:
        success_count = await test_concurrent_connections()
        
        if success_count == 3:
            print("\n✅ SUCCESS: All 3 clients connected concurrently!")
            print("✅ The MCP server successfully supports multiple concurrent clients!")
        elif success_count > 0:
            print(f"\n⚠️  PARTIAL SUCCESS: {success_count}/3 clients connected")
        else:
            print("\n❌ FAILURE: No clients could connect")
            
    except Exception as e:
        print(f"\n💥 Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 