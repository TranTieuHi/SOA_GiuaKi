import asyncio
import aiohttp
import json
from datetime import datetime

BASE_AUTH_URL = "http://localhost:8000/api"
BASE_TUITION_URL = "http://localhost:8001/api"

# Test data
USER1 = {"username": "johndoe", "password": "password123"}
USER2 = {"username": "janedoe", "password": "password456"}
STUDENT_ID = "ST2025005"

async def login(session, user_credentials):
    """Login and get token"""
    async with session.post(
        f"{BASE_AUTH_URL}/auth/login",
        json=user_credentials
    ) as response:
        data = await response.json()
        return data.get("token")

async def pay_tuition(session, token, student_id, user_name):
    """Pay tuition for student"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"🔄 [{user_name}] Attempting payment at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    
    try:
        async with session.post(
            f"{BASE_TUITION_URL}/payments/pay",
            json={"student_id": student_id},
            headers=headers
        ) as response:
            data = await response.json()
            status = response.status
            
            if status == 200:
                print(f"✅ [{user_name}] Payment SUCCESS at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                print(f"   Payment ID: {data.get('payment_id')}")
            else:
                print(f"❌ [{user_name}] Payment FAILED at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
                print(f"   Reason: {data.get('detail', 'Unknown error')}")
            
            return status, data
    except Exception as e:
        print(f"❌ [{user_name}] Exception: {e}")
        return 500, {"error": str(e)}

async def test_race_condition():
    """
    Test race condition: 2 users pay for same student simultaneously
    """
    print("=" * 70)
    print("🧪 TESTING RACE CONDITION - Optimistic Locking")
    print("=" * 70)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Login both users
        print("\n📝 Step 1: Login both users...")
        token1, token2 = await asyncio.gather(
            login(session, USER1),
            login(session, USER2)
        )
        
        if not token1 or not token2:
            print("❌ Login failed!")
            return
        
        print(f"✅ User 1 token: {token1[:30]}...")
        print(f"✅ User 2 token: {token2[:30]}...")
        
        # Step 2: Reset student payment status (for testing)
        print(f"\n📝 Step 2: Reset student {STUDENT_ID} payment status...")
        # You can add API call here to reset student status
        
        # Step 3: Concurrent payment attempts
        print(f"\n💰 Step 3: Both users pay for student {STUDENT_ID} SIMULTANEOUSLY...")
        print("⏱️  Starting concurrent requests...\n")
        
        # Create tasks that start at exactly the same time
        tasks = [
            pay_tuition(session, token1, STUDENT_ID, "User 1"),
            pay_tuition(session, token2, STUDENT_ID, "User 2")
        ]
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        print("\n" + "=" * 70)
        print("📊 RESULTS:")
        print("=" * 70)
        
        success_count = sum(1 for r in results if r[0] == 200)
        fail_count = len(results) - success_count
        
        print(f"✅ Successful payments: {success_count}")
        print(f"❌ Failed payments: {fail_count}")
        
        if success_count == 1 and fail_count == 1:
            print("\n🎉 OPTIMISTIC LOCKING WORKS CORRECTLY!")
            print("   One payment succeeded, one was rejected.")
        elif success_count == 2:
            print("\n⚠️  WARNING: RACE CONDITION DETECTED!")
            print("   Both payments succeeded - locking failed!")
        else:
            print("\n❓ UNEXPECTED RESULT - Check logs")

if __name__ == "__main__":
    asyncio.run(test_race_condition())