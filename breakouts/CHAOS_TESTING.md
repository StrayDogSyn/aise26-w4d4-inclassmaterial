# 🔥 Chaos Testing Guide

## What is Chaos Testing?

Chaos testing (also called chaos engineering) is a practice where you intentionally introduce failures and unexpected conditions to test your system's resilience, error handling, and logging.

## Features of chaos_test.py

### Good Requests (70% of traffic)
- ✅ Home endpoint (`/`)
- ✅ Products listing (`/products`)
- ✅ Users endpoint (`/users`) - may fail with 403 due to random admin check
- ✅ Health check (`/health`)
- ✅ Readiness check (`/ready`) - may return 503 randomly
- ✅ Startup check (`/startup`)
- ✅ Error endpoint (`/error`) - intentionally triggers errors
- ✅ Metrics endpoint (`/metrics`)

### Bad Requests (30% of traffic)
- ❌ Non-existent endpoints (404 errors)
- ❌ Wrong HTTP methods (405 errors)
- ❌ Malformed requests (SQL injection, XSS, buffer overflow attempts)
- ⚡ Rapid-fire requests (load testing)
- ⏱ Timeout simulations

## How to Use

### Step 1: Start the Server
```bash
python starter_code.py
```

The server will start on `http://localhost:8000` with colorful logging enabled.

### Step 2: Run Chaos Test (in another terminal)
```bash
python chaos_test.py
```

This will:
1. Send 100 random requests (mix of good and bad)
2. Display progress with colors
3. Show final statistics

## What to Watch For

### In the Server Terminal
You'll see colorful logs showing:
- 🔍 **DEBUG** (Cyan) - Detailed operations
- ✅ **INFO** (Green) - Normal operations
- ⚠️ **WARNING** (Yellow) - Unexpected but handled (low stock, unauthorized access)
- ❌ **ERROR** (Red) - Errors with full context
- 🚨 **CRITICAL** (Magenta+Bold) - Critical failures

### Context Data
Each log will show structured data like:
```json
{
  "request_id": "uuid-123",
  "endpoint": "/products",
  "status_code": 200,
  "duration": "0.05s"
}
```

### In the Chaos Test Terminal
You'll see:
- Green ✓ for successful "good" requests
- Red ✗ for intentional "bad" requests
- Yellow ⚡ for rapid-fire tests
- Final statistics showing:
  - Total requests sent
  - Success/failure rates
  - Breakdown by endpoint
  - Breakdown by status code
  - Requests per second

## Expected Behavior

### Successful Scenarios
- `200 OK` - Normal successful requests
- `403 Forbidden` - Users endpoint without admin (expected)
- `404 Not Found` - Non-existent endpoints (expected)
- `405 Method Not Allowed` - Wrong HTTP method (expected)
- `500 Internal Server Error` - Error endpoint (expected)
- `503 Service Unavailable` - Ready check fails randomly (expected)

### What Gets Logged
- All requests are logged with unique request IDs
- Middleware tracks request duration
- Errors include full context and stack traces
- Admin access attempts are audited
- Low stock warnings are triggered
- System metrics are updated (if Prometheus enabled)

## Learning Objectives

1. **Error Handling**: See how the server handles various error conditions gracefully
2. **Structured Logging**: Observe context data in every log message
3. **Request Tracking**: Follow requests through the system with request IDs
4. **Performance Monitoring**: See execution times for each endpoint
5. **Security**: Watch how malicious requests are handled and logged
6. **Load Testing**: See how the server performs under rapid requests

## Customization

You can modify `chaos_test.py` to:
- Change the number of requests (default: 100)
- Adjust good/bad ratio (default: 70/30)
- Add new attack vectors
- Change request delays
- Target specific endpoints more frequently

## Tips

1. **Watch Both Terminals**: Keep server and chaos test visible side-by-side
2. **Check Log File**: After testing, examine `logs/ecommerce.log` for the full history
3. **Vary the Load**: Run multiple chaos tests simultaneously for stress testing
4. **Analyze Patterns**: Look for patterns in when/why failures occur

## Example Output

### Server Log Example
```text
2025-10-23 10:15:23 | ✅ INFO     | ecommerce_api | log_requests:114 | Request started: GET /products
  💡 Context: {
    "request_id": "abc-123-def",
    "method": "GET",
    "path": "/products",
    "client_ip": "127.0.0.1"
  }

2025-10-23 10:15:23 | ⚠️ WARNING  | ecommerce_api | get_products:345 | Low stock alert: Laptop
  💡 Context: {
    "product_id": 1,
    "product_name": "Laptop",
    "current_stock": 5,
    "threshold": 10
  }
```

### Chaos Test Output Example
```text
[42/100] ✓ Requesting products...
  → Status: 200 ✓

[43/100] ✗ Requesting non-existent endpoint: /api/orders
  → Status: 404 ✓

[44/100] ⚡ Rapid-fire: 5 quick requests to /health...
  → Status: 200 ✓
```

## Troubleshooting

**Server not running?**
```bash
# Start the server first
python starter_code.py
```

**ImportError: No module named 'httpx'?**
```bash
# Install dependencies
pip install -r requirements.txt
```

**Want to see DEBUG logs?**
Edit `logger.py` and change:
```python
LOG_LEVEL = logging.DEBUG  # Was logging.INFO
```

---

**Happy Chaos Testing! 🔥**
