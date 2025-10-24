"""
🎯 BREAKOUT 1 - LOG DESIGN (10 minutes)
=====================================

Partner Discussion Points:
1. What makes a good log message?
2. When should we use each log level?
3. What context data helps with debugging?

This file contains our designed log messages BEFORE implementation.
Review with your partner and discuss the logging strategy.
"""

# ==============================================================================
# 📋 LOGGING STRATEGY OVERVIEW
# ==============================================================================

"""
Our logging approach:
1. **DEBUG**: Technical details for developers (database queries, cache hits/misses)
2. **INFO**: Normal business operations (successful requests, user actions)
3. **WARNING**: Unexpected but handled situations (slow queries, low stock, deprecated API usage)
4. **ERROR**: Errors that were caught and handled (validation errors, not found)
5. **CRITICAL**: System failures requiring immediate attention (database down, service crash)

Context Data to Capture:
- request_id: Unique identifier for tracing requests
- user_id: Who performed the action (for audit trails)
- endpoint: Which API endpoint was called
- response_time: How long the operation took
- status_code: HTTP status code returned
- error_type: Category of error (for metrics)
"""

# ==============================================================================
# 🏠 ROOT ENDPOINT ("/")
# ==============================================================================

"""
Log Design for Root Endpoint:

📊 METRICS TO TRACK:
- Total requests to root
- Response time
- User agent (to track API clients)

DISCUSSION: Should we log every request to root, or only sample?
Answer: For production, we'd sample or only log errors. For this demo, log all.
"""

# INFO - Root endpoint accessed successfully
# Context: {
#   "endpoint": "/",
#   "method": "GET",
#   "response_time": 0.001,
#   "status_code": 200,
#   "timestamp": "2025-10-23T19:45:23.123Z"
# }

# DEBUG - Root endpoint response details
# Context: {
#   "endpoint": "/",
#   "response_size": 156,  # bytes
#   "endpoints_listed": 3
# }

# ==============================================================================
# 🛍️ PRODUCTS ENDPOINT ("/products")
# ==============================================================================

"""
Log Design for Products Endpoint:

📊 METRICS TO TRACK:
- Number of products returned
- Database query time
- Cache hit/miss (if caching implemented)
- Stock levels (for low stock warnings)

DISCUSSION: What information is most valuable for debugging product issues?
Answer: Product count, query performance, stock levels, and any filters applied.
"""

# INFO - Products fetched successfully
# Context: {
#   "endpoint": "/products",
#   "method": "GET",
#   "product_count": 3,
#   "response_time": 0.052,
#   "status_code": 200,
#   "timestamp": "2025-10-23T19:45:25.456Z"
# }

# DEBUG - Database query executed for products
# Context: {
#   "endpoint": "/products",
#   "query_type": "SELECT_ALL",
#   "query_time": 0.048,
#   "table": "products"
# }

# WARNING - Slow database query detected
# Context: {
#   "endpoint": "/products",
#   "query_time": 2.5,
#   "threshold": 1.0,
#   "action_needed": "Consider adding indexes or caching"
# }
# DISCUSSION: At what threshold should we warn about slow queries?
# Answer: 1 second for this demo, but in production it depends on SLAs.

# WARNING - Low stock detected for product
# Context: {
#   "endpoint": "/products",
#   "product_id": 1,
#   "product_name": "Laptop",
#   "current_stock": 5,
#   "threshold": 10,
#   "action_needed": "Reorder inventory"
# }

# ERROR - Product not found
# Context: {
#   "endpoint": "/products/{product_id}",
#   "product_id": 999,
#   "error_type": "NOT_FOUND",
#   "status_code": 404
# }

# ==============================================================================
# 👥 USERS ENDPOINT ("/users")
# ==============================================================================

"""
Log Design for Users Endpoint:

📊 METRICS TO TRACK:
- Number of users returned
- Admin access attempts
- Query performance
- User status (active/inactive counts)

DISCUSSION: Should we log all user data access for security auditing?
Answer: YES! User data access should always be logged for compliance (GDPR, HIPAA, etc.)

SECURITY CONSIDERATION: Never log passwords, tokens, or sensitive PII.
"""

# INFO - Users fetched successfully (AUDIT LOG)
# Context: {
#   "endpoint": "/users",
#   "method": "GET",
#   "user_count": 3,
#   "active_users": 2,
#   "inactive_users": 1,
#   "response_time": 0.102,
#   "status_code": 200,
#   "requested_by": "admin_user_id",  # Who accessed user data
#   "timestamp": "2025-10-23T19:45:30.789Z"
# }

# WARNING - Unauthorized access attempt to users endpoint
# Context: {
#   "endpoint": "/users",
#   "attempted_by": "user_123",
#   "user_role": "customer",
#   "required_role": "admin",
#   "action": "ACCESS_DENIED",
#   "status_code": 403
# }
# DISCUSSION: How should we handle unauthorized access?
# Answer: Log it, return 403, and potentially alert security team if repeated attempts.

# DEBUG - User query performance metrics
# Context: {
#   "endpoint": "/users",
#   "query_time": 0.095,
#   "cache_hit": False,
#   "database_load": 0.45  # percentage
# }

# ERROR - Database connection failed for users
# Context: {
#   "endpoint": "/users",
#   "error_type": "DATABASE_CONNECTION_ERROR",
#   "retry_count": 3,
#   "status_code": 500,
#   "action": "Using fallback cache"
# }

# ==============================================================================
# ❌ ERROR ENDPOINT ("/error")
# ==============================================================================

"""
Log Design for Error Testing Endpoint:

📊 METRICS TO TRACK:
- Error types encountered
- Error frequency
- Error resolution time
- Impact (how many users affected)

DISCUSSION: Why have an endpoint that deliberately triggers errors?
Answer: For testing error handling, monitoring, and alerting systems.
"""

# WARNING - Error endpoint accessed (testing)
# Context: {
#   "endpoint": "/error",
#   "method": "GET",
#   "purpose": "Testing error handling",
#   "timestamp": "2025-10-23T19:45:35.123Z"
# }

# ERROR - Division by zero error triggered
# Context: {
#   "endpoint": "/error",
#   "error_type": "DIVISION_BY_ZERO",
#   "error_message": "division by zero",
#   "stack_trace": "...",  # Include full stack trace
#   "status_code": 500,
#   "handled": True
# }

# CRITICAL - Unhandled exception in error endpoint
# Context: {
#   "endpoint": "/error",
#   "error_type": "UNHANDLED_EXCEPTION",
#   "error_message": "Something went very wrong",
#   "status_code": 500,
#   "action_needed": "IMMEDIATE_ATTENTION_REQUIRED"
# }
# DISCUSSION: What's the difference between ERROR and CRITICAL?
# Answer: ERROR = handled gracefully, CRITICAL = system instability, requires immediate action.

# ==============================================================================
# 🏥 HEALTH CHECK ENDPOINTS
# ==============================================================================

"""
Log Design for Health Checks:

📊 METRICS TO TRACK:
- Health check pass/fail status
- Response times
- Dependency status (database, cache, external APIs)
- System resources (CPU, memory, disk)

DISCUSSION: Should health checks log on every request?
Answer: Usually NO for production (too noisy). Log only failures or sample successes.
For this demo, we'll log all for learning purposes.
"""

# INFO - Health check passed
# Context: {
#   "endpoint": "/health",
#   "status": "healthy",
#   "checks": {
#       "api": "OK",
#       "database": "OK",
#       "cache": "OK"
#   },
#   "response_time": 0.005,
#   "timestamp": "2025-10-23T19:45:40.001Z"
# }

# ERROR - Health check failed
# Context: {
#   "endpoint": "/health",
#   "status": "unhealthy",
#   "checks": {
#       "api": "OK",
#       "database": "FAILED",
#       "cache": "OK"
#   },
#   "failed_components": ["database"],
#   "error_message": "Database connection timeout",
#   "action_needed": "Check database connectivity"
# }

# INFO - Readiness check passed
# Context: {
#   "endpoint": "/ready",
#   "status": "ready",
#   "can_serve_traffic": True,
#   "active_connections": 5,
#   "max_connections": 100
# }

# WARNING - Readiness check warning (high load)
# Context: {
#   "endpoint": "/ready",
#   "status": "ready_with_warnings",
#   "active_connections": 95,
#   "max_connections": 100,
#   "cpu_usage": 0.85,
#   "memory_usage": 0.78,
#   "action": "Consider scaling"
# }

# INFO - Startup check completed
# Context: {
#   "endpoint": "/startup",
#   "status": "started",
#   "startup_time": 2.5,  # seconds
#   "initialized_components": ["database", "cache", "api"]
# }

# ==============================================================================
# 🔍 CROSS-CUTTING CONCERNS
# ==============================================================================

"""
Log Design for Middleware and General Operations:

DISCUSSION: What other things should we log that aren't specific to one endpoint?
Answers:
1. Request/Response middleware (every API call)
2. Authentication/Authorization attempts
3. Rate limiting events
4. API version usage (for deprecation planning)
"""

# INFO - Request received (from middleware)
# Context: {
#   "request_id": "req-abc-123",
#   "method": "GET",
#   "endpoint": "/products",
#   "user_agent": "Mozilla/5.0...",
#   "ip_address": "192.168.1.100",
#   "timestamp": "2025-10-23T19:45:45.001Z"
# }

# INFO - Response sent (from middleware)
# Context: {
#   "request_id": "req-abc-123",
#   "status_code": 200,
#   "response_time": 0.052,
#   "response_size": 458,  # bytes
#   "endpoint": "/products"
# }

# WARNING - Rate limit approaching
# Context: {
#   "user_id": "user_123",
#   "current_requests": 95,
#   "limit": 100,
#   "window": "1 minute",
#   "action": "Throttle warning sent"
# }

# ERROR - Rate limit exceeded
# Context: {
#   "user_id": "user_123",
#   "requests_attempted": 105,
#   "limit": 100,
#   "window": "1 minute",
#   "status_code": 429,
#   "action": "Request blocked"
# }

# ==============================================================================
# 📊 PARTNER DISCUSSION QUESTIONS
# ==============================================================================

"""
Before implementing, discuss with your partner:

1. **Log Levels**:
   - When would you use DEBUG vs INFO?
   - What situations warrant WARNING vs ERROR?
   - When should we use CRITICAL?

2. **Context Data**:
   - What context is essential for debugging?
   - What context helps with business metrics?
   - What should we NEVER log? (passwords, tokens, SSNs, etc.)

3. **Performance**:
   - Will logging slow down our API?
   - Should we log synchronously or asynchronously?
   - How do we prevent log files from filling up disk space?

4. **Security**:
   - Should we log all failed authentication attempts?
   - How do we handle PII (Personally Identifiable Information)?
   - What logs should be encrypted or access-controlled?

5. **Production Considerations**:
   - How long should we retain logs?
   - Where should logs be sent? (local file, centralized logging, both?)
   - How do we search and analyze logs at scale?

6. **Monitoring & Alerting**:
   - Which logs should trigger alerts?
   - What's the difference between logging and metrics?
   - When should we page someone at 3am?

TAKE 5 MINUTES TO DISCUSS THESE WITH YOUR PARTNER BEFORE CODING!
"""

# ==============================================================================
# ✅ BREAKOUT 1 COMPLETION CHECKLIST
# ==============================================================================

"""
[ ] Designed log messages for all endpoints
[ ] Documented log levels and rationale
[ ] Included context data for each log
[ ] Considered error scenarios and warnings
[ ] Discussed security and PII concerns
[ ] Reviewed with partner
[ ] Ready to implement in Breakout 2!
"""

print("📋 Breakout 1 Design Complete!")
print("Review this file with your partner before implementing Breakout 2.")
print("Key Takeaway: Good logging design happens BEFORE coding! 🎯")
