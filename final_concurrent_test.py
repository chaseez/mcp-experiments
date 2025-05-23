"""
Final test demonstrating 3 concurrent clients connecting to the MCP server.
"""

import asyncio
import aiohttp
import time

async def test_client_connection(client_id: int):
    """Test individual client connection"""
    try:
        print(f"🔄 Client {client_id}: Starting connection test...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/sse', timeout=aiohttp.ClientTimeout(total=3)) as response:
                
                if response.status == 200:
                    print(f"✅ Client {client_id}: Successfully connected! (Status: {response.status})")
                    
                    # Read first line to confirm we get SSE data
                    async for line in response.content:
                        if line:
                            print(f"📡 Client {client_id}: Received data: {line.decode().strip()[:60]}...")
                            break
                    
                    return True
                else:
                    print(f"❌ Client {client_id}: Failed with status {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Client {client_id}: Error - {e}")
        return False

async def main():
    print("🚀 Testing Multiple Concurrent Connections to MCP Server")
    print("=" * 60)
    
    # Launch 3 concurrent clients
    print("📡 Launching 3 concurrent client connections...")
    
    start_time = time.time()
    tasks = [test_client_connection(i + 1) for i in range(3)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print("=" * 60)
    print(f"⏱️  Test completed in {end_time - start_time:.2f} seconds")
    
    # Count successful connections
    successful = sum(results)
    total = len(results)
    
    print(f"\n📊 RESULTS:")
    print(f"   • Total clients tested: {total}")
    print(f"   • Successful connections: {successful}")
    print(f"   • Success rate: {successful/total*100:.1f}%")
    
    if successful == total:
        print(f"\n🎉 SUCCESS! All {total} clients connected concurrently!")
        print("✅ The MCP server successfully supports multiple concurrent clients!")
    else:
        print(f"\n⚠️  {successful}/{total} clients connected successfully")

if __name__ == "__main__":
    asyncio.run(main()) 