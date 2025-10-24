"""
E-commerce API Logging Breakouts - Complete Implementation
===========================================================
cSpell:words ecommerce psutil

This file demonstrates the progressive completion of all three breakouts:
- Breakout 1: Log design with comments
- Breakout 2: Structured logging implementation
- Breakout 3: Health checks and Prometheus metrics

Each breakout section is clearly marked for educational purposes.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import time
import random
import uvicorn
from datetime import datetime
import uuid

# ==============================================================================
# BREAKOUT 2: Import Custom Logger
# ==============================================================================
from logger import get_logger, log_execution_time

# Initialize logger for this application
logger = get_logger()

# ==============================================================================
# BREAKOUT 3: Import Prometheus Metrics
# ==============================================================================
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    import psutil
    
    # Define Prometheus metrics
    http_requests_total = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'endpoint', 'status']
    )
    
    http_request_duration_seconds = Histogram(
        'http_request_duration_seconds',
        'HTTP request duration in seconds',
        ['method', 'endpoint']
    )
    
    system_cpu_usage = Gauge(
        'system_cpu_usage_percent',
        'System CPU usage percentage'
    )
    
    system_memory_usage = Gauge(
        'system_memory_usage_percent',
        'System memory usage percentage'
    )
    
    products_low_stock = Gauge(
        'products_low_stock_total',
        'Number of products with low stock'
    )
    
    PROMETHEUS_ENABLED = True
    logger.info("Prometheus metrics initialized successfully")
except ImportError:
    PROMETHEUS_ENABLED = False
    logger.warning("Prometheus client not installed - metrics disabled")

# ==============================================================================
# FASTAPI APP INITIALIZATION
# ==============================================================================
app = FastAPI(
    title="E-commerce API with Logging",
    description="Educational API demonstrating logging best practices",
    version="1.0.0"
)

# ==============================================================================
# MIDDLEWARE: Request Logging and Metrics
# ==============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    BREAKOUT 2: Middleware for logging all HTTP requests
    BREAKOUT 3: Also collects Prometheus metrics
    
    This middleware:
    - Generates unique request IDs for tracking
    - Logs request start and completion
    - Measures request duration
    - Records metrics to Prometheus
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Log incoming request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    # Track request timing
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log successful completion
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": f"{duration:.4f}s"
            }
        )
        
        # Update Prometheus metrics if enabled
        if PROMETHEUS_ENABLED:
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "error": str(e),
                "duration": f"{duration:.4f}s"
            },
            exc_info=True
        )
        
        # Update error metrics
        if PROMETHEUS_ENABLED:
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
        
        raise


# ==============================================================================
# BREAKOUT 1: LOG DESIGN (Documented in Comments)
# ==============================================================================
"""
LOG DESIGN FOR E-COMMERCE API
==============================

ENDPOINT: / (Root/Home)
-----------------------
INFO - "Home endpoint accessed" - {"endpoint": "/", "response_time": 0.001}

ENDPOINT: /products
-------------------
INFO - "Products retrieved successfully" - {
    "endpoint": "/products",
    "count": 3,
    "response_time": 0.05,
    "request_id": "uuid-123"
}
WARNING - "Low stock detected" - {
    "product_id": 1,
    "product_name": "Laptop",
    "current_stock": 5,
    "threshold": 10
}
ERROR - "Product database query failed" - {
    "endpoint": "/products",
    "error": "connection_timeout",
    "retry_attempted": true
}

ENDPOINT: /users
----------------
INFO - "Users retrieved successfully" - {
    "endpoint": "/users",
    "count": 3,
    "admin_check": true,
    "response_time": 0.1
}
WARNING - "Unauthorized access attempt" - {
    "endpoint": "/users",
    "user_id": "guest",
    "reason": "missing_admin_privilege"
}
INFO - "Admin access granted" - {
    "user_id": "admin_123",
    "endpoint": "/users",
    "action": "view_all_users"
}

ENDPOINT: /error
----------------
ERROR - "Division by zero error triggered" - {
    "endpoint": "/error",
    "error_type": "ZeroDivisionError",
    "error_message": "division by zero",
    "stack_trace": "..."
}
CRITICAL - "Unhandled exception in endpoint" - {
    "endpoint": "/error",
    "exception": "...",
    "request_id": "uuid-123"
}

ENDPOINT: /health (Liveness Probe)
----------------------------------
INFO - "Health check passed" - {
    "endpoint": "/health",
    "status": "healthy",
    "timestamp": "2025-10-23T10:00:00"
}

ENDPOINT: /ready (Readiness Probe)
----------------------------------
INFO - "Readiness check passed" - {
    "endpoint": "/ready",
    "database": "connected",
    "cache": "connected",
    "status": "ready"
}
WARNING - "Readiness check failed" - {
    "endpoint": "/ready",
    "database": "disconnected",
    "status": "not_ready"
}

ENDPOINT: /startup (Startup Probe)
----------------------------------
INFO - "Startup check completed" - {
    "endpoint": "/startup",
    "initialization": "complete",
    "status": "ready"
}

GENERAL ERROR HANDLING
----------------------
ERROR - "HTTP Exception occurred" - {
    "status_code": 500,
    "detail": "Internal server error",
    "path": "/error"
}
"""


# ==============================================================================
# BREAKOUT 2 & 3: API ENDPOINTS WITH LOGGING
# ==============================================================================

@app.get("/")
def read_root():
    """
    Home endpoint - lists available endpoints
    
    BREAKOUT 2: Logs basic endpoint access
    """
    logger.info(
        "Home endpoint accessed",
        extra={
            "endpoint": "/",
            "available_endpoints": ["/products", "/users", "/error", "/health", "/ready", "/startup"]
        }
    )
    
    return {
        "message": "E-commerce API Demo with Logging",
        "version": "1.0.0",
        "endpoints": [
            "/products - Get all products",
            "/users - Get all users (admin)",
            "/error - Trigger error for testing",
            "/health - Liveness probe",
            "/ready - Readiness probe",
            "/startup - Startup probe",
            "/metrics - Prometheus metrics (if enabled)"
        ]
    }


@app.get("/products")
def get_products():
    """
    Get all products with inventory information
    
    BREAKOUT 2: Logs product retrieval with context
    BREAKOUT 3: Updates low stock metrics
    """
    logger.debug("Starting product retrieval from database")
    
    # Simulate database query
    time.sleep(0.05)
    
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 5},
        {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
        {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 25}
    ]
    
    # Check for low stock items (BREAKOUT 2: WARNING level logging)
    low_stock_threshold = 10
    low_stock_count = 0
    
    for product in products:
        if product["stock"] < low_stock_threshold:
            low_stock_count += 1
            logger.warning(
                f"Low stock alert: {product['name']}",
                extra={
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "current_stock": product["stock"],
                    "threshold": low_stock_threshold
                }
            )
    
    # Update Prometheus metric for low stock items
    if PROMETHEUS_ENABLED:
        products_low_stock.set(low_stock_count)
    
    # Log successful retrieval
    logger.info(
        "Products retrieved successfully",
        extra={
            "endpoint": "/products",
            "count": len(products),
            "low_stock_items": low_stock_count
        }
    )
    
    return {"products": products, "total": len(products)}


@app.get("/users")
def get_users():
    """
    Get all users (admin only endpoint)
    
    BREAKOUT 2: Demonstrates audit logging for sensitive operations
    """
    logger.debug("Admin endpoint accessed: /users")
    
    # Simulate admin check (10% chance of unauthorized access for demo)
    is_admin = random.random() > 0.1
    
    if not is_admin:
        logger.warning(
            "Unauthorized access attempt to admin endpoint",
            extra={
                "endpoint": "/users",
                "user_id": "guest_user",
                "reason": "missing_admin_privilege",
                "action": "access_denied"
            }
        )
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    # Log admin access (audit trail)
    logger.info(
        "Admin access granted to user endpoint",
        extra={
            "endpoint": "/users",
            "user_id": "admin_123",
            "action": "view_all_users",
            "audit": True
        }
    )
    
    # Simulate database query
    time.sleep(0.1)
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "active": True},
        {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "active": False}
    ]
    
    logger.info(
        "Users retrieved successfully",
        extra={
            "endpoint": "/users",
            "count": len(users),
            "admin_check": True
        }
    )
    
    return {"users": users, "total": len(users)}


@app.get("/error")
def trigger_error():
    """
    Trigger an error for testing error handling and logging
    
    BREAKOUT 2: Demonstrates ERROR level logging with exception details
    """
    logger.warning(
        "Error endpoint accessed - intentional error will be triggered",
        extra={"endpoint": "/error", "test_mode": True}
    )
    
    try:
        # Intentionally trigger division by zero
        result = 10 / 0
    except ZeroDivisionError as e:
        # Log the specific error with full context
        logger.error(
            "Division by zero error triggered",
            extra={
                "endpoint": "/error",
                "error_type": "ZeroDivisionError",
                "error_message": str(e),
                "test_scenario": True
            },
            exc_info=True  # Include stack trace
        )
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error: Division by zero"
        )


# ==============================================================================
# BREAKOUT 3: HEALTH CHECK ENDPOINTS
# ==============================================================================

@app.get("/health")
def health_check():
    """
    Liveness probe - checks if the application is alive
    
    BREAKOUT 3: Simple health check that always returns healthy
    Used by Kubernetes/Docker to restart unhealthy containers
    """
    logger.info(
        "Liveness probe checked",
        extra={
            "endpoint": "/health",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ready")
def readiness_check():
    """
    Readiness probe - checks if the application is ready to serve traffic
    
    BREAKOUT 3: Checks dependencies (simulated) before accepting traffic
    Used by load balancers to determine if the instance can handle requests
    """
    # Simulate dependency checks (database, cache, etc.)
    # In production, you would actually check real dependencies
    is_ready = random.random() > 0.1  # 90% success rate for demo
    
    if not is_ready:
        logger.warning(
            "Readiness check failed - dependencies not ready",
            extra={
                "endpoint": "/ready",
                "database": "disconnected",
                "cache": "disconnected",
                "status": "not_ready"
            }
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "Dependencies unavailable",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    logger.info(
        "Readiness probe passed",
        extra={
            "endpoint": "/ready",
            "database": "connected",
            "cache": "connected",
            "status": "ready"
        }
    )
    
    return {
        "status": "ready",
        "dependencies": {
            "database": "connected",
            "cache": "connected"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/startup")
def startup_check():
    """
    Startup probe - checks if the application has completed initialization
    
    BREAKOUT 3: Verifies the application is fully initialized
    Used to delay traffic until startup tasks are complete
    """
    logger.info(
        "Startup probe checked",
        extra={
            "endpoint": "/startup",
            "initialization": "complete",
            "status": "ready"
        }
    )
    
    return {
        "status": "ready",
        "initialization": "complete",
        "timestamp": datetime.now().isoformat()
    }


# ==============================================================================
# BREAKOUT 3: PROMETHEUS METRICS ENDPOINT
# ==============================================================================

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """
    Prometheus metrics endpoint
    
    BREAKOUT 3: Exposes metrics in Prometheus format
    Scraped by Prometheus for monitoring and alerting
    """
    if not PROMETHEUS_ENABLED:
        logger.warning("Metrics endpoint accessed but Prometheus not enabled")
        raise HTTPException(
            status_code=503,
            detail="Prometheus metrics not available - install prometheus-client"
        )
    
    # Update system metrics before returning
    try:
        system_cpu_usage.set(psutil.cpu_percent(interval=0.1))
        system_memory_usage.set(psutil.virtual_memory().percent)
        
        logger.debug(
            "System metrics updated",
            extra={
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent
            }
        )
    except Exception as e:
        logger.error(f"Failed to update system metrics: {e}")
    
    logger.info("Metrics endpoint accessed")
    return generate_latest()


# ==============================================================================
# GLOBAL EXCEPTION HANDLER
# ==============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    BREAKOUT 2: Global exception handler for unhandled errors
    Ensures all errors are logged with full context
    """
    logger.critical(
        "Unhandled exception in application",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "path": request.url.path
        }
    )


# ==============================================================================
# APPLICATION STARTUP
# ==============================================================================

if __name__ == "__main__":
    # ANSI color codes for beautiful terminal output
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    # Stylish startup banner
    print(f"\n{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{MAGENTA}🚀 E-COMMERCE API - COMPLETE LOGGING IMPLEMENTATION{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}\n")
    
    print(f"{GREEN}✅ BREAKOUT 1:{RESET} {WHITE}Log Design - See comments above each endpoint{RESET}")
    print(f"{GREEN}✅ BREAKOUT 2:{RESET} {WHITE}Structured Logging - Implemented with logger.py{RESET}")
    print(f"{GREEN}✅ BREAKOUT 3:{RESET} {WHITE}Health Checks + Metrics - Prometheus integration{RESET}")
    
    print(f"\n{BOLD}{BLUE}📋 FEATURES IMPLEMENTED:{RESET}")
    print(f"{GREEN}   ✓{RESET} Custom logger module (logger.py)")
    print(f"{GREEN}   ✓{RESET} {YELLOW}Colorful{RESET} structured logging with context")
    print(f"{GREEN}   ✓{RESET} Request ID tracking")
    print(f"{GREEN}   ✓{RESET} Performance timing")
    print(f"{GREEN}   ✓{RESET} Health check endpoints")
    if PROMETHEUS_ENABLED:
        print(f"{GREEN}   ✓{RESET} Prometheus metrics")
    else:
        print(f"{YELLOW}   ⚠{RESET} Prometheus metrics (install prometheus-client)")
    print(f"{GREEN}   ✓{RESET} Global exception handling")
    print(f"{GREEN}   ✓{RESET} Audit logging for sensitive operations")
    print(f"{GREEN}   ✓{RESET} Log level demonstration (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    
    print(f"\n{BOLD}{BLUE}🔗 API ENDPOINTS:{RESET}")
    print(f"{CYAN}   •{RESET} Home:           {WHITE}http://localhost:8000{RESET}")
    print(f"{CYAN}   •{RESET} API Docs:       {WHITE}http://localhost:8000/docs{RESET}")
    print(f"{CYAN}   •{RESET} Products:       {WHITE}http://localhost:8000/products{RESET}")
    print(f"{CYAN}   •{RESET} Users:          {WHITE}http://localhost:8000/users{RESET}")
    print(f"{CYAN}   •{RESET} Error Test:     {WHITE}http://localhost:8000/error{RESET}")
    print(f"{CYAN}   •{RESET} Health:         {WHITE}http://localhost:8000/health{RESET}")
    print(f"{CYAN}   •{RESET} Readiness:      {WHITE}http://localhost:8000/ready{RESET}")
    print(f"{CYAN}   •{RESET} Startup:        {WHITE}http://localhost:8000/startup{RESET}")
    if PROMETHEUS_ENABLED:
        print(f"{CYAN}   •{RESET} Metrics:        {WHITE}http://localhost:8000/metrics{RESET}")
    
    print(f"\n{BOLD}{MAGENTA}📝 LOG FILE LOCATION:{RESET} {YELLOW}logs/ecommerce.log{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}")
    print(f"\n{BOLD}{GREEN}🎯 Starting server...{RESET}\n")
    
    logger.info(
        "Application startup initiated",
        extra={
            "version": "1.0.0",
            "prometheus_enabled": PROMETHEUS_ENABLED,
            "host": "127.0.0.1",
            "port": 8000
        }
    )
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
