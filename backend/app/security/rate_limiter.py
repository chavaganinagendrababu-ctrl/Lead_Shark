import os
import time
from collections import defaultdict
from fastapi import HTTPException, status, Request

class SimpleRateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    def check_rate_limit(self, request: Request, identifier: str = None):
        # Do not rate limit automated unit test suites
        if os.getenv("TESTING") == "1" or os.getenv("ENVIRONMENT") == "testing":
            return

        # Extract client IP, checking X-Forwarded-For for proxy/Render environments
        forwarded = request.headers.get("x-forwarded-for") if request else None
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = identifier or (request.client.host if request and request.client else "unknown")

        if client_ip in ("testclient", "127.0.0.1", "localhost"):
            return

        current_time = time.time()
        window_start = current_time - 60

        # Filter out requests older than 1 minute
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > window_start]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again in a few moments."
            )

        self.requests[client_ip].append(current_time)

auth_rate_limiter = SimpleRateLimiter(requests_per_minute=20)
general_rate_limiter = SimpleRateLimiter(requests_per_minute=120)

