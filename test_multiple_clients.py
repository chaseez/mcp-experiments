"""
Test script to verify multiple concurrent client connections to the MCP server.
This script will create multiple clients that connect simultaneously and query the database.
"""

import asyncio
import time
import sys
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async def test_client(client_id: int, query: str):
    """Test a single client connection and database query"""
    print(f"Client {client_id}: Starting connection...")
    
    try:
        # Connect to the SSE endpoint
        async with sse_client("http://localhost:8000/sse") as streams:
            read_stream, write_stream = streams
            
            async with ClientSession(read_stream, write_stream) as session:
                print(f"Client {client_id}: Connected successfully")
                
                # Test calling the query_databricks tool
                start_time = time.time()
                result = await session.call_tool("query_databricks", {"query": query})
                end_time = time.time()
                
                print(f"Client {client_id}: Query completed in {end_time - start_time:.2f}s")
                print(f"Client {client_id}: Result preview: {str(result)[:100]}...")
                
                return f"Client {client_id}: SUCCESS"
            
    except Exception as e:
        error_msg = f"Client {client_id}: ERROR - {str(e)}"
        print(error_msg)
        return error_msg

async def test_concurrent_clients():
    """Test multiple clients connecting concurrently"""
    print("Starting concurrent client test...")
    print("=" * 60)
    
    # Define different queries for each client to test various scenarios
    queries = [
        "SELECT COUNT(*) as verified_count FROM bronze.leaseend_db_public.deal_states WHERE _fivetran_deleted = false LIMIT 5",
        "SELECT DISTINCT state FROM bronze.leaseend_db_public.deal_states ORDER BY state LIMIT 10", 
        "SELECT deal_id, state, updated_date_utc FROM bronze.leaseend_db_public.deal_states ORDER BY updated_date_utc DESC LIMIT 3"
    ]
    
    # Create tasks for 3 concurrent clients
    tasks = []
    for i in range(3):
        task = asyncio.create_task(test_client(i + 1, queries[i]))
        tasks.append(task)
    
    # Wait for all clients to complete
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    print("=" * 60)
    print(f"All clients completed in {end_time - start_time:.2f}s")
    print("\nResults:")
    for result in results:
        print(f"  - {result}")
    
    # Check if all were successful
    success_count = sum(1 for result in results if "SUCCESS" in str(result))
    print(f"\nSummary: {success_count}/3 clients succeeded")
    
    return success_count == 3

if __name__ == "__main__":
    print("Multiple Client Connection Test")
    print("Testing 3 concurrent connections to MCP server...")
    
    try:
        # Run the concurrent test
        success = asyncio.run(test_concurrent_clients())
        
        if success:
            print("\n✅ All clients connected and queried successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some clients failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1) 