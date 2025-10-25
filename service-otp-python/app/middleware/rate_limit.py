import time
from typing import Dict

# ✅ In-memory storage cho rate limiting
request_counters: Dict[str, dict] = {}

RATE_LIMIT = 5  # Max 5 requests
RATE_WINDOW = 60  # Per 60 seconds

def is_allowed(user_id: str) -> bool:
    """
    Check if user is allowed to make request (rate limiting)
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if allowed, False if rate limit exceeded
    """
    current_time = time.time()
    
    if user_id not in request_counters:
        # First request for this user
        request_counters[user_id] = {
            "count": 1,
            "reset_time": current_time + RATE_WINDOW
        }
        return True
    
    record = request_counters[user_id]
    
    # Check if window has expired
    if current_time > record["reset_time"]:
        # Reset counter
        request_counters[user_id] = {
            "count": 1,
            "reset_time": current_time + RATE_WINDOW
        }
        return True
    
    # Check if limit exceeded
    if record["count"] >= RATE_LIMIT:
        print(f"[RATE LIMIT] User {user_id} exceeded limit: {record['count']}/{RATE_LIMIT}")
        return False
    
    # Increment counter
    record["count"] += 1
    return True

def get_rate_limit_status(user_id: str) -> dict:
    """Get current rate limit status for user"""
    now = time.time()
    
    record = request_counters.get(user_id)
    
    if record is None:
        return {
            "user_id": user_id,
            "attempts_used": 0,
            "attempts_remaining": RATE_LIMIT,
            "reset_time": None,
            "blocked": False
        }
    
    if now > record["reset_time"]:
        return {
            "user_id": user_id,
            "attempts_used": 0,
            "attempts_remaining": RATE_LIMIT,
            "reset_time": None,
            "blocked": False,
            "status": "reset"
        }
    
    attempts_remaining = max(0, RATE_LIMIT - record["count"])
    time_until_reset = max(0, record["reset_time"] - now)
    
    return {
        "user_id": user_id,
        "attempts_used": record["count"],
        "attempts_remaining": attempts_remaining,
        "blocked": attempts_remaining == 0,
        "reset_in_seconds": int(time_until_reset),
        "reset_time": record["reset_time"]
    }

def reset_rate_limit(user_id: str) -> bool:
    """Reset rate limit for specific user"""
    if user_id in request_counters:
        del request_counters[user_id]
        return True
    return False

def clear_all_rate_limits() -> int:
    """Clear all rate limit records"""
    count = len(request_counters)
    request_counters.clear()
    return count