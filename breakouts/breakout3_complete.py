"""
🎯 BREAKOUT 3 - HEALTH CHECKS + MONITORING WITH PROMETHEUS
===========================================================

This adds health check endpoints and Prometheus metrics collection.

Partner Discussion Points:
1. What is the difference between /health, /ready, and /startup?
2. Why do we need metrics in addition to logs?
3. How would Grafana visualize this data?

Key Concepts:
- Liveness probes (is the app alive?)
- Readiness probes (can it serve traffic?)
- Startup probes (has it finished starting?)
- Prometheus metrics (counters, gauges, histograms)
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
import time
import random
import uvicorn
from datetime import datetime
import uuid
from typing import Dict, Any
import psutil  # For system metrics

# Import our custom logger
from logger import setup_ecommerce_logger, get_logger, log_execution_time

# Prometheus client for metrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ==============================================================================
# 🚀 APPLICATION SETUP
# ==============================================================================

app = FastAPI(
    title="E-commerce API with Monitoring",
    description="E-commerce API with health checks and Prometheus metrics",
    version="1.0.0"
)

setup_ecommerce_logger()
logger = get_logger()

logger.info(
    "E-commerce API with monitoring starting up",
    extra={"event": "startup", "version": "1.0.0"}
)


# ==============================================================================
# 📊 PROMETHEUS METRICS
# ==============================================================================

"""
DISCUSSION: What are Prometheus metrics?
Answer: Numeric measurements over time. Unlike logs (events), metrics track:
- How many requests per second
- Average response time
- Error rates
- System resources (CPU, memory)

DISCUSSION: Why use metrics AND logs?
Answer: 
- Logs: Tell you WHAT happened (event details, context)
- Metrics: Tell you HOW MUCH/HOW OFTEN (trends, patterns)
Both are needed for complete observability!
"""

# Counter: Always goes up (requests, errors, etc.)
# DISCUSSION: When to use a Counter?
# Answer: For events that accumulate (requests, sales, errors)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress'
)

# Histogram: Measures distribution (response times, request sizes)
# DISCUSSION: Why use Histogram instead of averaging?
# Answer: Histograms show distribution. Average can hide problems!
# Example: Average 100ms looks good, but if 90% are 50ms and 10% are 1000ms, you have a problem!
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Gauge: Can go up or down (CPU usage, active connections, queue size)
# DISCUSSION: When to use a Gauge?
# Answer: For values that fluctuate (temperature, memory usage, active users)
app_info = Gauge(
    'app_info',
    'Application information',
    ['version', 'environment']
)

system_cpu_usage = Gauge('system_cpu_usage', 'CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage', 'Memory usage percentage')
active_database_connections = Gauge('active_database_connections', 'Active DB connections')

# Error counters
http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['endpoint', 'error_type']
)

# Business metrics
products_low_stock = Gauge('products_low_stock', 'Number of products with low stock')
user_access_attempts = Counter('user_access_attempts', 'User endpoint access attempts', ['result'])

# Set app info
app_info.labels(version='1.0.0', environment='development').set(1)


# ==============================================================================
# 🔧 MIDDLEWARE WITH METRICS
# ==============================================================================

@app.middleware("http")
async def metrics_and_logging_middleware(request: Request, call_next):
    """
    Enhanced middleware that collects both logs and metrics.
    
    DISCUSSION: Why collect metrics in middleware?
    Answer: Same reason we log here - applies to ALL endpoints automatically.
    One place to maintain instead of repeating code in every endpoint.
    """
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    
    # Increment in-progress gauge
    http_requests_in_progress.inc()
    
    # Update system metrics
    try:
        system_cpu_usage.set(psutil.cpu_percent())
        system_memory_usage.set(psutil.virtual_memory().percent)
        # Simulate database connections (in real app, get from connection pool)
        active_database_connections.set(random.randint(5, 20))
    except Exception as e:
        logger.error(f"Failed to collect system metrics: {e}")
    
    logger.info(
        "Request received",
        extra={
            "event": "request_received",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    try:
        response = await call_next(request)
        response_time = time.perf_counter() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(response_time)
        
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
        
        if response_time > 1.0:
            logger.warning(
                "Slow request detected",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "response_time": f"{response_time:.4f}s"
                }
            )
        
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        response_time = time.perf_counter() - start_time
        
        # Record error metrics
        http_errors_total.labels(
            endpoint=request.url.path,
            error_type=type(e).__name__
        ).inc()
        
        logger.error(
            "Request failed",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__,
                "response_time": f"{response_time:.4f}s"
            },
            exc_info=True
        )
        raise
        
    finally:
        # Decrement in-progress gauge
        http_requests_in_progress.dec()


# ==============================================================================
# 🏥 HEALTH CHECK ENDPOINTS
# ==============================================================================

"""
DISCUSSION: What are health checks and why do we need them?
Answer: Health checks let orchestration systems (Kubernetes, Docker, AWS ECS)
know if your app is healthy. They're used to:
1. Restart unhealthy instances
2. Route traffic only to healthy instances
3. Know when an app is ready to serve traffic

Three types:
1. Liveness: Is the app alive? (If no, restart it)
2. Readiness: Is the app ready for traffic? (If no, don't send traffic)
3. Startup: Has the app finished starting? (For slow startups)
"""

@app.get("/health", tags=["Health Checks"])
async def health_check():
    """
    Liveness probe - Is the application alive?
    
    DISCUSSION: What makes an app "alive"?
    Answer: Can it respond to requests? If this endpoint times out or errors,
    the app should be restarted.
    
    This should be FAST and SIMPLE. Don't check external dependencies here!
    Just verify the app process is running and responsive.
    """
    # Log the health check
    # DISCUSSION: Should we log every health check?
    # Answer: In production, NO (too noisy - Kubernetes checks every few seconds).
    # For this demo, yes. In production, only log failures.
    logger.debug(
        "Health check requested",
        extra={"event": "health_check", "check_type": "liveness"}
    )
    
    # Simple check - if we can return a response, we're alive
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api": "OK"
        }
    }
    
    logger.debug(
        "Health check passed",
        extra={"event": "health_check_passed", "status": "healthy"}
    )
    
    return health_status


@app.get("/ready", tags=["Health Checks"])
async def readiness_check():
    """
    Readiness probe - Is the application ready to serve traffic?
    
    DISCUSSION: What makes an app "ready"?
    Answer: Can it handle real requests? This SHOULD check dependencies:
    - Database connection
    - Cache connection
    - Required external APIs
    
    If any dependency is down, return 503 (Service Unavailable).
    Load balancers will stop sending traffic until it's ready again.
    """
    logger.debug(
        "Readiness check requested",
        extra={"event": "readiness_check", "check_type": "readiness"}
    )
    
    # Check dependencies
    checks = {
        "api": "OK",
        "database": "OK",  # In real app: try to query database
        "cache": "OK"      # In real app: try to connect to Redis/Memcached
    }
    
    # Simulate occasional database issue
    if random.random() < 0.1:  # 10% chance of failure
        checks["database"] = "DEGRADED"
        logger.warning(
            "Readiness check degraded - database slow",
            extra={
                "event": "readiness_degraded",
                "failed_components": ["database"],
                "action": "Still serving traffic but monitoring"
            }
        )
    
    # Check system resources
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    # Warn if resources are high
    if cpu_usage > 80 or memory_usage > 80:
        logger.warning(
            "High resource usage detected",
            extra={
                "event": "high_resource_usage",
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "action_needed": "Consider scaling"
            }
        )
    
    # Determine overall readiness
    is_ready = all(status == "OK" for status in checks.values())
    
    readiness_status = {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "resources": {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage
        }
    }
    
    if is_ready:
        logger.info(
            "Readiness check passed",
            extra={"event": "readiness_passed", "checks": checks}
        )
        return readiness_status
    else:
        logger.error(
            "Readiness check failed",
            extra={
                "event": "readiness_failed",
                "failed_checks": [k for k, v in checks.items() if v != "OK"]
            }
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=readiness_status
        )


@app.get("/startup", tags=["Health Checks"])
async def startup_check():
    """
    Startup probe - Has the application finished starting up?
    
    DISCUSSION: Why separate from readiness?
    Answer: Some apps take a long time to start (loading ML models, warming caches).
    Startup probe gives more time, and doesn't fail liveness checks during startup.
    
    Once startup succeeds, it's not checked again. Then liveness/readiness take over.
    """
    logger.info(
        "Startup check requested",
        extra={"event": "startup_check", "check_type": "startup"}
    )
    
    # Check if critical components are initialized
    # In a real app, you'd check:
    # - Database migrations completed
    # - Required data loaded
    # - ML models loaded
    # - Caches warmed up
    
    startup_checks = {
        "database_migrations": "COMPLETE",
        "data_loaded": "COMPLETE",
        "cache_warmed": "COMPLETE",
        "dependencies_initialized": "COMPLETE"
    }
    
    startup_time = 2.5  # Simulate startup time
    
    startup_status = {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
        "startup_time_seconds": startup_time,
        "checks": startup_checks
    }
    
    logger.info(
        "Startup check completed",
        extra={
            "event": "startup_complete",
            "startup_time": startup_time,
            "checks": startup_checks
        }
    )
    
    return startup_status


# ==============================================================================
# 📊 PROMETHEUS METRICS ENDPOINT
# ==============================================================================

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.
    
    DISCUSSION: What is this endpoint for?
    Answer: Prometheus scrapes this endpoint periodically (every 15s typically)
    to collect metrics. It then stores them in a time-series database.
    
    Grafana can then query Prometheus to visualize the metrics on dashboards.
    
    DISCUSSION: Should this endpoint be public?
    Answer: Usually NO! In production, restrict to internal network or
    require authentication. You don't want to expose system metrics publicly.
    """
    logger.debug(
        "Metrics endpoint accessed",
        extra={"event": "metrics_scrape", "scraper": "prometheus"}
    )
    
    # Generate Prometheus format metrics
    metrics_output = generate_latest()
    
    return PlainTextResponse(
        content=metrics_output,
        media_type=CONTENT_TYPE_LATEST
    )


# ==============================================================================
# 🛍️ APPLICATION ENDPOINTS (from Breakout 2)
# ==============================================================================

@app.get("/", tags=["Root"])
async def read_root():
    """Home endpoint."""
    logger.info("Root endpoint accessed", extra={"event": "root_access"})
    return {
        "message": "E-commerce API with Monitoring",
        "version": "1.0.0",
        "health_endpoints": [
            {"path": "/health", "description": "Liveness probe"},
            {"path": "/ready", "description": "Readiness probe"},
            {"path": "/startup", "description": "Startup probe"},
            {"path": "/metrics", "description": "Prometheus metrics"}
        ],
        "api_endpoints": [
            {"path": "/products", "description": "Get all products"},
            {"path": "/users", "description": "Get all users"},
            {"path": "/error", "description": "Trigger error"}
        ]
    }


@app.get("/products", tags=["Products"])
@log_execution_time
async def get_products():
    """Get all products."""
    logger.debug("Fetching products", extra={"event": "db_query_start"})
    time.sleep(0.05)
    
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 5},
        {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
        {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 25}
    ]
    
    # Update low stock metric
    low_stock_count = sum(1 for p in products if p["stock"] < 10)
    products_low_stock.set(low_stock_count)
    
    for product in products:
        if product["stock"] < 10:
            logger.warning(
                f"Low stock: {product['name']}",
                extra={
                    "event": "low_stock",
                    "product_id": product["id"],
                    "stock": product["stock"]
                }
            )
    
    logger.info(
        "Products fetched",
        extra={"event": "products_fetched", "count": len(products)}
    )
    
    return {"products": products, "total": len(products)}


@app.get("/users", tags=["Users"])
@log_execution_time
async def get_users():
    """Get all users."""
    is_admin = random.choice([True, True, True, False])
    
    # Track access attempts
    user_access_attempts.labels(result="success" if is_admin else "denied").inc()
    
    if not is_admin:
        logger.warning("Unauthorized user access attempt", extra={"event": "unauthorized_access"})
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logger.info("User data accessed", extra={"event": "user_data_access"})
    time.sleep(0.1)
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "active": True},
        {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "active": False}
    ]
    
    return {"users": users, "total": len(users)}


@app.get("/error", tags=["Testing"])
async def trigger_error():
    """Trigger error for testing."""
    logger.warning("Error endpoint accessed", extra={"event": "error_endpoint_access"})
    
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero", extra={"event": "division_by_zero"}, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ==============================================================================
# 🏃 RUN THE APPLICATION
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 E-COMMERCE API WITH HEALTH CHECKS & MONITORING")
    print("=" * 80)
    print("\n📋 Breakout 3 Complete - Features:")
    print("   ✅ Liveness probe: /health")
    print("   ✅ Readiness probe: /ready")
    print("   ✅ Startup probe: /startup")
    print("   ✅ Prometheus metrics: /metrics")
    print("   ✅ System resource monitoring (CPU, memory)")
    print("   ✅ Business metrics (low stock, user access)")
    print("   ✅ Request metrics (count, duration, errors)")
    print("\n🔗 Endpoints:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - Health: http://localhost:8000/health")
    print("   - Ready: http://localhost:8000/ready")
    print("   - Metrics: http://localhost:8000/metrics")
    print("\n📊 Next Steps for Prometheus + Grafana:")
    print("   1. Install Prometheus: brew install prometheus (Mac)")
    print("   2. Configure prometheus.yml to scrape http://localhost:8000/metrics")
    print("   3. Start Prometheus: prometheus --config.file=prometheus.yml")
    print("   4. Install Grafana: brew install grafana (Mac)")
    print("   5. Add Prometheus as data source in Grafana")
    print("   6. Create dashboard with these metrics:")
    print("      - http_requests_total (request rate)")
    print("      - http_request_duration_seconds (response times)")
    print("      - http_errors_total (error rate)")
    print("      - system_cpu_usage (CPU usage)")
    print("      - products_low_stock (inventory alerts)")
    print("\n💡 Partner Discussion:")
    print("   - Hit /ready multiple times - see it sometimes fail?")
    print("   - Visit /metrics - understand the Prometheus format")
    print("   - Compare /health vs /ready - what's the difference?")
    print("   - How would you alert on high error rates?")
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
