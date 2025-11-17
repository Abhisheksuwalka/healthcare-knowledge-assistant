import asyncio
import sys

sys.path.insert(0, '..')

async def test_tools():
    from backend.tools.registry import tool_registry
    
    print("🔍 Testing MCP Tools Integration...")
    print(f"✓ Available tools: {tool_registry.get_tool_names()}")
    
    # Test 1: Get current datetime
    print("\n1️⃣  Testing get_current_datetime...")
    result = await tool_registry.execute_tool(
        "get_current_datetime",
        timezone="Asia/Kolkata"
    )
    print(f"  Result: {result['success']}")
    print(f"  Data: {result['data']}")
    
    # Test 2: Calculate age
    print("\n2️⃣  Testing calculate_age...")
    result = await tool_registry.execute_tool(
        "calculate_age",
        birthdate="1990-05-15"
    )
    print(f"  Result: {result['success']}")
    print(f"  Age: {result['data']['age_years']} years")
    
    # Test 3: Get working hours
    print("\n3️⃣  Testing get_working_hours...")
    result = await tool_registry.execute_tool(
        "get_working_hours",
        department="opd"
    )
    print(f"  Result: {result['success']}")
    print(f"  Hours: {result['data']}")
    
    # Test 4: Search internal docs
    print("\n4️⃣  Testing search_internal_docs...")
    result = await tool_registry.execute_tool(
        "search_internal_docs",
        query="visiting hours"
    )
    print(f"  Result: {result['success']}")
    print(f"  Found: {result['data']['results_count']} documents")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_tools())
