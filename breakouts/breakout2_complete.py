"""
🎯 BREAKOUT 2 - E-COMMERCE API WITH STRUCTURED LOGGING
=======================================================

This is the complete implementation of the e-commerce API with structured logging.

Partner Discussion Points:
1. Compare this to starter_code.py - what changed?
2. How does logging help with debugging?
3. What happens when an error occurs - trace it through the logs

Run this file: python breakout2_complete.py
Then test the API and watch the logs!
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import time
import random
import uvicorn
from datetime import datetime
import uuid

# Import our custom logger
from logger import setup_ecommerce_logger, get_logger, log_execution_time

# ==============================================================================
# 🚀 APPLICATION SETUP
# ==============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce API Demo",
    description="E-commerce API with structured logging for learning purposes",
    version="1.0.0"
)

# Setup logger (call this ONCE at startup)
# DISCUSSION: Where should we call this? Why here?
# Answer: At module level, before any routes are defined.
# This ensures the logger is ready before any endpoint is called.
setup_ecommerce_logger()
logger = get_logger()

# Log application startup
# DISCUSSION: Why log startup?
# Answer: Helps track when the application was restarted, useful for debugging
# deployment issues or unexpected restarts.
logger.info(
    "E-commerce API starting up",
    extra={
        "event": "startup",
        "version": "1.0.0",
        "environment": "development"  # In production, read from env variable
    }
)


# ==============================================================================
# 🔧 MIDDLEWARE FOR REQUEST/RESPONSE LOGGING
# ==============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log every incoming request and outgoing response.
    
    DISCUSSION: What is middleware?
    Answer: Code that runs BEFORE and AFTER every request.
    Think of it as a wrapper around all your endpoints.
    
    Perfect for:
    - Logging all requests
    - Adding request IDs
    - Measuring response times
    - Authentication/Authorization
    - Rate limiting
    
    DISCUSSION: Why log in middleware instead of in each endpoint?
    Answer: DRY principle! Write once, applies to all endpoints.
    Ensures consistent logging across the entire API.
    """
    # Generate unique request ID for tracing
    # DISCUSSION: Why use a request ID?
    # Answer: In distributed systems, a request might touch multiple services.
    # Request ID lets you trace the entire journey through logs.
    request_id = str(uuid.uuid4())
    
    # Record request start time
    start_time = time.perf_counter()
    
    # Log incoming request
    logger.info(
        "Request received",
        extra={
            "event": "request_received",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    )
    
    # Process the request
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time = time.perf_counter() - start_time
        
        # Log successful response
        logger.info(
            "Request completed",
            extra={
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time": f"{response_time:.4f}s"
            }
        )
        
        # DISCUSSION: When should we warn about slow requests?
        # Answer: Define based on your SLA. For this demo, 1 second.
        if response_time > 1.0:
            logger.warning(
                "Slow request detected",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "response_time": f"{response_time:.4f}s",
                    "threshold": "1.0s",
                    "action_needed": "Investigate performance"
                }
            )
        
        # Add request ID to response headers (useful for support/debugging)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate response time even for errors
        response_time = time.perf_counter() - start_time
        
        # Log the error
        logger.error(
            "Request failed with exception",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "response_time": f"{response_time:.4f}s"
            },
            exc_info=True  # Include full stack trace
        )
        
        # Re-raise so FastAPI can handle it
        raise


# ==============================================================================
# 🏠 ROOT ENDPOINT
# ==============================================================================

@app.get("/", tags=["Root"])
async def read_root():
    """
    Home endpoint - lists available endpoints.
    
    DISCUSSION: Should we log every call to root endpoint?
    Answer: In production, maybe not (too noisy). For this demo, yes!
    The middleware already logs it, so we just add business-level logging.
    """
    # Log business event (INFO level - normal operation)
    logger.info(
        "Root endpoint accessed - listing available endpoints",
        extra={
            "event": "root_access",
            "endpoints_count": 3
        }
    )
    
    return {
        "message": "E-commerce API Demo",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/products", "description": "Get all products"},
            {"path": "/users", "description": "Get all users (admin only)"},
            {"path": "/error", "description": "Trigger error for testing"}
        ]
    }


# ==============================================================================
# 🛍️ PRODUCTS ENDPOINT
# ==============================================================================

@app.get("/products", tags=["Products"])
@log_execution_time  # Decorator to track execution time
async def get_products():
    """
    Get all products with inventory levels.
    
    DISCUSSION: What should we log for a products endpoint?
    Answer: 
    1. Number of products returned
    2. Query performance
    3. Low stock warnings
    4. Any filtering applied
    """
    # Log business event - query starting
    logger.debug(
        "Fetching products from database",
        extra={
            "event": "db_query_start",
            "query_type": "SELECT_ALL",
            "table": "products"
        }
    )
    
    # Simulate database query
    query_start = time.perf_counter()
    time.sleep(0.05)  # Simulate DB latency
    query_time = time.perf_counter() - query_start
    
    # Mock products data
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 5},
        {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
        {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 25}
    ]
    
    # Log query performance
    logger.debug(
        "Database query completed",
        extra={
            "event": "db_query_complete",
            "query_type": "SELECT_ALL",
            "query_time": f"{query_time:.4f}s",
            "rows_returned": len(products)
        }
    )
    
    # DISCUSSION: When should we warn about query performance?
    # Answer: Based on your SLA. For this demo, queries > 0.1s get a warning.
    if query_time > 0.1:
        logger.warning(
            "Slow database query detected",
            extra={
                "event": "slow_query",
                "query_time": f"{query_time:.4f}s",
                "threshold": "0.1s",
                "query_type": "SELECT_ALL",
                "table": "products",
                "action_needed": "Consider adding indexes or caching"
            }
        )
    
    # Check for low stock and log warnings
    # DISCUSSION: Why log low stock as WARNING instead of INFO?
    # Answer: It requires action (reordering inventory). WARNING = needs attention.
    low_stock_threshold = 10
    for product in products:
        if product["stock"] < low_stock_threshold:
            logger.warning(
                f"Low stock alert for product: {product['name']}",
                extra={
                    "event": "low_stock",
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "current_stock": product["stock"],
                    "threshold": low_stock_threshold,
                    "action_needed": "Reorder inventory"
                }
            )
    
    # Log successful operation
    logger.info(
        "Products fetched successfully",
        extra={
            "event": "products_fetched",
            "product_count": len(products),
            "total_value": sum(p["price"] * p["stock"] for p in products),
            "low_stock_count": sum(1 for p in products if p["stock"] < low_stock_threshold)
        }
    )
    
    return {"products": products, "total": len(products)}


# ==============================================================================
# 👥 USERS ENDPOINT
# ==============================================================================

@app.get("/users", tags=["Users"])
@log_execution_time
async def get_users():
    """
    Get all users (admin only endpoint).
    
    DISCUSSION: What makes user data access special?
    Answer: SECURITY and COMPLIANCE!
    - Must log WHO accessed user data (audit trail)
    - Must log WHEN it was accessed
    - Needed for GDPR, HIPAA, SOC2 compliance
    
    DISCUSSION: What should we NEVER log?
    Answer: Passwords, tokens, SSNs, credit cards, or other sensitive PII.
    """
    # SECURITY: Log user data access attempt (AUDIT LOG)
    # In production, you'd include the actual user ID of who made the request
    logger.info(
        "User data accessed",
        extra={
            "event": "user_data_access",
            "endpoint": "/users",
            "accessed_by": "admin_user",  # In production: get from JWT token
            "access_type": "READ_ALL",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # In a real app, you'd check authentication/authorization here
    # For demo purposes, we'll simulate a random auth check
    is_admin = random.choice([True, True, True, False])  # 75% success rate
    
    if not is_admin:
        # Log unauthorized access attempt
        # DISCUSSION: Why log failed auth attempts?
        # Answer: Security! Multiple failed attempts might indicate an attack.
        logger.warning(
            "Unauthorized access attempt to users endpoint",
            extra={
                "event": "unauthorized_access",
                "endpoint": "/users",
                "attempted_by": "unknown_user",
                "user_role": "not_admin",
                "required_role": "admin",
                "action": "ACCESS_DENIED"
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Simulate database query
    time.sleep(0.1)
    
    # Mock users data
    # IMPORTANT: We're not logging sensitive fields like passwords!
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "active": True},
        {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "active": False}
    ]
    
    # Count active/inactive users for metrics
    active_count = sum(1 for u in users if u["active"])
    inactive_count = len(users) - active_count
    
    # Log successful data retrieval with metrics
    logger.info(
        "Users fetched successfully",
        extra={
            "event": "users_fetched",
            "user_count": len(users),
            "active_users": active_count,
            "inactive_users": inactive_count,
            "accessed_by": "admin_user"
        }
    )
    
    return {"users": users, "total": len(users)}


# ==============================================================================
# ❌ ERROR ENDPOINT
# ==============================================================================

@app.get("/error", tags=["Testing"])
async def trigger_error():
    """
    Trigger an error for testing error handling and logging.
    
    DISCUSSION: Why have an endpoint that deliberately crashes?
    Answer: For testing!
    - Test error handling logic
    - Test logging of errors
    - Test monitoring/alerting systems
    - Ensure error messages don't leak sensitive info
    """
    # Log that this endpoint was accessed
    # DISCUSSION: Should this be WARNING instead of INFO?
    # Answer: Good question! In production, you might want to know if someone
    # is repeatedly hitting the error endpoint (could be an attack).
    logger.warning(
        "Error testing endpoint accessed",
        extra={
            "event": "error_endpoint_access",
            "purpose": "Testing error handling"
        }
    )
    
    try:
        # Deliberately cause an error
        result = 10 / 0
        
    except ZeroDivisionError as e:
        # Log the error with full context
        # DISCUSSION: Why ERROR instead of CRITICAL?
        # Answer: This is expected and handled. CRITICAL is for system failures.
        logger.error(
            "Division by zero error occurred",
            extra={
                "event": "division_by_zero",
                "error_type": "ZeroDivisionError",
                "error_message": str(e),
                "endpoint": "/error",
                "handled": True
            },
            exc_info=True  # Include stack trace
        )
        
        # Return a user-friendly error
        # DISCUSSION: Should we expose the real error to users?
        # Answer: NO! Security risk. Give generic message, log details internally.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred. Please contact support."
        )


# ==============================================================================
# 🔥 GLOBAL EXCEPTION HANDLER
# ==============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and log them.
    
    DISCUSSION: Why have a global exception handler?
    Answer: Safety net! Ensures ALL errors are logged, even unexpected ones.
    Prevents the app from crashing without leaving any trace.
    """
    # Log the unexpected error
    logger.critical(
        "Unhandled exception occurred",
        extra={
            "event": "unhandled_exception",
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "action_needed": "IMMEDIATE_ATTENTION_REQUIRED"
        },
        exc_info=True
    )
    
    # Return generic error response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "support": "Contact support with error ID from X-Request-ID header"
        }
    )


# ==============================================================================
# 🚀 APPLICATION STARTUP/SHUTDOWN
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run when application starts up.
    
    DISCUSSION: What should happen at startup?
    Answer: 
    - Initialize database connections
    - Load configuration
    - Verify dependencies are available
    - Log that the system is ready
    """
    logger.info(
        "Application startup complete",
        extra={
            "event": "startup_complete",
            "version": "1.0.0",
            "environment": "development"
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when application shuts down.
    
    DISCUSSION: What should happen at shutdown?
    Answer:
    - Close database connections gracefully
    - Finish processing in-flight requests
    - Log that system is shutting down
    """
    logger.info(
        "Application shutting down",
        extra={
            "event": "shutdown",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==============================================================================
# 🏃 RUN THE APPLICATION
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 E-COMMERCE API WITH STRUCTURED LOGGING")
    print("=" * 70)
    print("\n📋 Breakout 2 Complete - Features:")
    print("   ✅ Structured logging module (logger.py)")
    print("   ✅ Request/Response middleware with request IDs")
    print("   ✅ All endpoints instrumented with logging")
    print("   ✅ Performance tracking with @log_execution_time")
    print("   ✅ Error handling and logging")
    print("   ✅ Security audit logging for user data access")
    print("   ✅ Low stock warnings")
    print("   ✅ Slow query detection")
    print("\n🔗 API available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("📁 Logs will be written to: logs/ecommerce.log")
    print("\n🧪 Try these tests:")
    print("   1. GET http://localhost:8000/products")
    print("   2. GET http://localhost:8000/users (watch auth logging)")
    print("   3. GET http://localhost:8000/error (watch error logging)")
    print("   4. Open logs/ecommerce.log and review the structured logs")
    print("\n💡 Partner Discussion:")
    print("   - Compare logs in console vs file - what's different?")
    print("   - Find the request ID - how does it help debugging?")
    print("   - Look at execution times - which endpoint is slowest?")
    print("   - Trigger the /error endpoint - trace the error through logs")
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
