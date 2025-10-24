"""
🔥 CHAOS TESTING SCRIPT FOR E-COMMERCE API
==========================================

This script generates 100 random requests (both good and bad) to test:
- Logging at all levels
- Error handling
- Request ID tracking
- Performance under load
- Exception handling

Usage:
    1. Start the server: python starter_code.py
    2. In another terminal: python chaos_test.py
    3. Watch the colorful logs!
"""

import httpx
import random
import time
from typing import Dict, List
import asyncio
from datetime import datetime

# ANSI colors for pretty output
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
BOLD = '\033[1m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"

# Track statistics
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "by_endpoint": {},
    "by_status": {},
    "start_time": None,
    "end_time": None
}


class ChaosRequester:
    """
    Chaos testing client that makes random good and bad requests.
    """
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=10.0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    # ==============================================================================
    # GOOD REQUESTS (Should succeed with 200/503)
    # ==============================================================================
    
    def good_home_request(self) -> Dict:
        """Request the home endpoint."""
        print(f"{GREEN}✓ Requesting home endpoint...{RESET}")
        response = self.client.get(f"{self.base_url}/")
        return {"endpoint": "/", "status": response.status_code, "success": True}
    
    def good_products_request(self) -> Dict:
        """Request products endpoint."""
        print(f"{GREEN}✓ Requesting products...{RESET}")
        response = self.client.get(f"{self.base_url}/products")
        return {"endpoint": "/products", "status": response.status_code, "success": True}
    
    def good_users_request(self) -> Dict:
        """Request users endpoint (may fail with 403 due to random admin check)."""
        print(f"{GREEN}✓ Requesting users (admin endpoint)...{RESET}")
        response = self.client.get(f"{self.base_url}/users")
        success = response.status_code in [200, 403]  # Both are "expected"
        return {"endpoint": "/users", "status": response.status_code, "success": success}
    
    def good_health_request(self) -> Dict:
        """Request health check endpoint."""
        print(f"{GREEN}✓ Checking health...{RESET}")
        response = self.client.get(f"{self.base_url}/health")
        return {"endpoint": "/health", "status": response.status_code, "success": True}
    
    def good_ready_request(self) -> Dict:
        """Request readiness check (may return 503 due to random failure)."""
        print(f"{GREEN}✓ Checking readiness...{RESET}")
        response = self.client.get(f"{self.base_url}/ready")
        success = response.status_code in [200, 503]  # Both are "expected"
        return {"endpoint": "/ready", "status": response.status_code, "success": success}
    
    def good_startup_request(self) -> Dict:
        """Request startup check endpoint."""
        print(f"{GREEN}✓ Checking startup...{RESET}")
        response = self.client.get(f"{self.base_url}/startup")
        return {"endpoint": "/startup", "status": response.status_code, "success": True}
    
    def good_error_request(self) -> Dict:
        """Request error endpoint (intentionally triggers error)."""
        print(f"{YELLOW}⚠ Triggering intentional error...{RESET}")
        response = self.client.get(f"{self.base_url}/error")
        # Error endpoint should return 500
        return {"endpoint": "/error", "status": response.status_code, "success": response.status_code == 500}
    
    def good_metrics_request(self) -> Dict:
        """Request Prometheus metrics endpoint."""
        print(f"{GREEN}✓ Fetching metrics...{RESET}")
        try:
            response = self.client.get(f"{self.base_url}/metrics")
            success = response.status_code in [200, 503]  # 503 if Prometheus not installed
            return {"endpoint": "/metrics", "status": response.status_code, "success": success}
        except Exception as e:
            return {"endpoint": "/metrics", "status": 503, "success": True, "error": str(e)}
    
    # ==============================================================================
    # BAD REQUESTS (Should fail gracefully with proper error logging)
    # ==============================================================================
    
    def bad_nonexistent_endpoint(self) -> Dict:
        """Request a non-existent endpoint."""
        fake_endpoints = ["/api/orders", "/admin/users", "/api/cart", "/api/checkout", "/dashboard"]
        endpoint = random.choice(fake_endpoints)
        print(f"{RED}✗ Requesting non-existent endpoint: {endpoint}{RESET}")
        response = self.client.get(f"{self.base_url}{endpoint}")
        return {"endpoint": endpoint, "status": response.status_code, "success": response.status_code == 404}
    
    def bad_method_not_allowed(self) -> Dict:
        """Use wrong HTTP method."""
        endpoints = ["/", "/products", "/users", "/health"]
        endpoint = random.choice(endpoints)
        method = random.choice(["POST", "PUT", "DELETE", "PATCH"])
        print(f"{RED}✗ Using {method} on {endpoint} (should be GET)...{RESET}")
        
        try:
            if method == "POST":
                response = self.client.post(f"{self.base_url}{endpoint}")
            elif method == "PUT":
                response = self.client.put(f"{self.base_url}{endpoint}")
            elif method == "DELETE":
                response = self.client.delete(f"{self.base_url}{endpoint}")
            else:  # PATCH
                response = self.client.patch(f"{self.base_url}{endpoint}")
            
            return {"endpoint": endpoint, "status": response.status_code, "success": response.status_code == 405}
        except Exception as e:
            return {"endpoint": endpoint, "status": 0, "success": False, "error": str(e)}
    
    def bad_malformed_request(self) -> Dict:
        """Send request with weird headers or query params."""
        endpoint = random.choice(["/products", "/users", "/health"])
        weird_params = {
            "sql_injection": "'; DROP TABLE users; --",
            "xss": "<script>alert('xss')</script>",
            "buffer_overflow": "A" * 10000,
            "unicode": "你好🔥💻",
            "null_byte": "test\x00injection"
        }
        param_key = random.choice(list(weird_params.keys()))
        param_value = weird_params[param_key]
        
        print(f"{RED}✗ Sending malformed request with {param_key}...{RESET}")
        try:
            response = self.client.get(
                f"{self.base_url}{endpoint}",
                params={param_key: param_value}
            )
            return {"endpoint": endpoint, "status": response.status_code, "success": True}
        except Exception as e:
            return {"endpoint": endpoint, "status": 0, "success": False, "error": str(e)}
    
    def bad_rapid_fire_requests(self) -> Dict:
        """Send multiple rapid requests to simulate load."""
        endpoint = random.choice(["/products", "/users", "/health"])
        print(f"{YELLOW}⚡ Rapid-fire: 5 quick requests to {endpoint}...{RESET}")
        
        results = []
        for i in range(5):
            try:
                response = self.client.get(f"{self.base_url}{endpoint}")
                results.append(response.status_code)
            except Exception as e:
                results.append(0)
        
        return {
            "endpoint": endpoint,
            "status": results[0] if results else 0,
            "success": all(r == 200 or r == 403 or r == 503 for r in results),
            "rapid_fire": True,
            "results": results
        }
    
    def bad_timeout_simulation(self) -> Dict:
        """Simulate a slow client (tests server timeout handling)."""
        endpoint = "/health"
        print(f"{YELLOW}⏱ Simulating slow request...{RESET}")
        
        try:
            # Use very short timeout to potentially cause timeout
            slow_client = httpx.Client(timeout=0.001)
            response = slow_client.get(f"{self.base_url}{endpoint}")
            slow_client.close()
            return {"endpoint": endpoint, "status": response.status_code, "success": True}
        except httpx.TimeoutException:
            print(f"{YELLOW}  → Request timed out (expected){RESET}")
            return {"endpoint": endpoint, "status": 0, "success": True, "timeout": True}
        except Exception as e:
            return {"endpoint": endpoint, "status": 0, "success": False, "error": str(e)}


def print_banner():
    """Print a stylish banner."""
    print(f"\n{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{MAGENTA}🔥 CHAOS TESTING - E-COMMERCE API{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}\n")
    print(f"{YELLOW}⚡ Sending 100 random requests (good and bad)...{RESET}")
    print(f"{YELLOW}⚡ Watch the server terminal for colorful logs!{RESET}\n")


def update_stats(result: Dict):
    """Update statistics based on result."""
    stats["total_requests"] += 1
    
    if result.get("success", False):
        stats["successful"] += 1
    else:
        stats["failed"] += 1
    
    endpoint = result.get("endpoint", "unknown")
    stats["by_endpoint"][endpoint] = stats["by_endpoint"].get(endpoint, 0) + 1
    
    status = result.get("status", 0)
    stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    
    # If rapid fire, add extra counts
    if result.get("rapid_fire", False):
        stats["total_requests"] += 4  # Already counted 1, add 4 more


def print_stats():
    """Print final statistics."""
    duration = (stats["end_time"] - stats["start_time"]).total_seconds()
    
    print(f"\n{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{GREEN}📊 CHAOS TEST RESULTS{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}\n")
    
    print(f"{BOLD}Total Statistics:{RESET}")
    print(f"  Total Requests:    {MAGENTA}{stats['total_requests']}{RESET}")
    print(f"  Successful:        {GREEN}{stats['successful']}{RESET}")
    print(f"  Failed:            {RED}{stats['failed']}{RESET}")
    print(f"  Duration:          {CYAN}{duration:.2f}s{RESET}")
    print(f"  Requests/second:   {YELLOW}{stats['total_requests'] / duration:.2f}{RESET}")
    
    print(f"\n{BOLD}Requests by Endpoint:{RESET}")
    for endpoint, count in sorted(stats["by_endpoint"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {endpoint:<20} {count:>3} requests")
    
    print(f"\n{BOLD}Responses by Status Code:{RESET}")
    for status, count in sorted(stats["by_status"].items(), key=lambda x: x[1], reverse=True):
        if status == 200:
            color = GREEN
            label = "OK"
        elif status == 403:
            color = YELLOW
            label = "Forbidden"
        elif status == 404:
            color = YELLOW
            label = "Not Found"
        elif status == 405:
            color = YELLOW
            label = "Method Not Allowed"
        elif status == 500:
            color = RED
            label = "Internal Server Error"
        elif status == 503:
            color = YELLOW
            label = "Service Unavailable"
        else:
            color = RESET
            label = "Other"
        
        print(f"  {color}{status} {label:<25}{RESET} {count:>3} responses")
    
    print(f"\n{CYAN}{'=' * 80}{RESET}")
    print(f"{GREEN}✅ Chaos test complete! Check the server logs for details.{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}\n")


def main():
    """Run the chaos test."""
    print_banner()
    
    # Check if server is running
    try:
        httpx.get(BASE_URL, timeout=2.0)
    except Exception as e:
        print(f"{RED}❌ Error: Server is not running at {BASE_URL}{RESET}")
        print(f"{YELLOW}   Start the server first: python starter_code.py{RESET}\n")
        return
    
    stats["start_time"] = datetime.now()
    
    with ChaosRequester() as chaos:
        # Define all possible requests (good and bad)
        good_requests = [
            chaos.good_home_request,
            chaos.good_products_request,
            chaos.good_users_request,
            chaos.good_health_request,
            chaos.good_ready_request,
            chaos.good_startup_request,
            chaos.good_error_request,
            chaos.good_metrics_request,
        ]
        
        bad_requests = [
            chaos.bad_nonexistent_endpoint,
            chaos.bad_method_not_allowed,
            chaos.bad_malformed_request,
            chaos.bad_rapid_fire_requests,
            chaos.bad_timeout_simulation,
        ]
        
        # Run 100 random requests
        for i in range(100):
            print(f"\n{BOLD}[{i+1}/100]{RESET} ", end="")
            
            # 70% good requests, 30% bad requests
            if random.random() < 0.7:
                request_func = random.choice(good_requests)
            else:
                request_func = random.choice(bad_requests)
            
            try:
                result = request_func()
                update_stats(result)
                
                # Show result
                if result.get("success", False):
                    print(f"  {GREEN}→ Status: {result.get('status', 'N/A')} ✓{RESET}")
                else:
                    print(f"  {RED}→ Status: {result.get('status', 'N/A')} ✗{RESET}")
                
            except Exception as e:
                print(f"  {RED}→ Exception: {str(e)}{RESET}")
                stats["failed"] += 1
            
            # Random delay between requests (0-500ms)
            time.sleep(random.uniform(0, 0.5))
    
    stats["end_time"] = datetime.now()
    print_stats()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠ Test interrupted by user{RESET}\n")
        stats["end_time"] = datetime.now()
        print_stats()
    except Exception as e:
        print(f"\n{RED}❌ Fatal error: {str(e)}{RESET}\n")
