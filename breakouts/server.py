"""
E-commerce API with Structlog - Complete Implementation
========================================================
cSpell:words ecommerce psutil structlog

This server uses STRUCTLOG instead of custom logger.
Compare with starter_code.py to see the differences!

Key Differences:
1. Uses structlog library instead of custom logger module
2. Context binding instead of extra={} parameters
3. Processor-based formatting instead of custom formatters
4. More production-ready and feature-rich

All endpoints and functionality are IDENTICAL to starter_code.py
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import time
import random
import uvicorn
from datetime import datetime
import uuid

# ==============================================================================
# IMPORT STRUCTLOG LOGGER
# ==============================================================================
from structlog_logger import get_logger, setup_structlog, log_execution_time

# Setup structlog on module import
setup_structlog(use_json=False, log_to_console=True, log_to_file=True)

# Get logger instance
log = get_logger("ecommerce_api")

# ==============================================================================
# PROMETHEUS METRICS (Same as starter_code.py)
# ==============================================================================
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
    import psutil
    
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
    log.info("Prometheus metrics initialized successfully")
except ImportError:
    PROMETHEUS_ENABLED = False
    log.warning("Prometheus client not installed - metrics disabled")

# ==============================================================================
# FASTAPI APP INITIALIZATION
# ==============================================================================
app = FastAPI(
    title="E-commerce API with Structlog",
    description="Educational API demonstrating structlog best practices",
    version="2.0.0"  # v2.0 uses structlog!
)

# ==============================================================================
# MIDDLEWARE: Request Logging with Structlog
# ==============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    STRUCTLOG DIFFERENCE: We use .bind() to add context instead of extra={}
    
    Comparison:
    Custom Logger: logger.info("message", extra={"key": "value"})
    Structlog:     log.bind(key="value").info("message")
    
    Benefit: Bound context persists across multiple log calls!
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # STRUCTLOG FEATURE: Bind context to create a new logger with context
    request_log = log.bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Log incoming request (context automatically included!)
    request_log.info(f"Request started: {request.method} {request.url.path}")
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log completion with additional context
        request_log.info(
            f"Request completed: {request.method} {request.url.path}",
            status_code=response.status_code,
            duration=f"{duration:.4f}s"
        )
        
        # Update Prometheus metrics
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
        
        # Log error with exception info
        request_log.error(
            f"Request failed: {request.method} {request.url.path}",
            error=str(e),
            duration=f"{duration:.4f}s",
            exc_info=True
        )
        
        if PROMETHEUS_ENABLED:
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
        
        raise


# ==============================================================================
# API ENDPOINTS (Same as starter_code.py)
# ==============================================================================

@app.get("/")
def read_root():
    """
    Home endpoint
    
    STRUCTLOG DIFFERENCE: Notice how we don't need extra={}
    Just pass key=value parameters directly!
    """
    log.info(
        "Home endpoint accessed",
        endpoint="/",
        available_endpoints=["/products", "/users", "/error", "/health", "/ready", "/startup", "/grafana/dashboard"]
    )
    
    return {
        "message": "E-commerce API with Structlog + Grafana",
        "version": "2.0.0",
        "logger": "structlog",
        "monitoring": {
            "grafana": "http://localhost:3000",
            "prometheus": "http://localhost:9090",
            "dashboard_info": "/grafana/dashboard"
        },
        "endpoints": [
            "/products - Get all products",
            "/users - Get all users (admin)",
            "/error - Trigger error for testing",
            "/health - Liveness probe",
            "/ready - Readiness probe",
            "/startup - Startup probe",
            "/metrics - Prometheus metrics (if enabled)",
            "/grafana/dashboard - Grafana setup info",
            "/grafana/health - Grafana health check",
            "/grafana/search - Grafana metrics search",
            "/grafana/query - Grafana data query",
            "/grafana/annotations - Grafana annotations"
        ]
    }


@app.get("/products")
def get_products():
    """
    Get all products
    
    STRUCTLOG FEATURE: Context binding for multiple related logs
    """
    log.debug("Starting product retrieval from database")
    
    # Simulate database query
    time.sleep(0.05)
    
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 5},
        {"id": 2, "name": "Mouse", "price": 29.99, "stock": 50},
        {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 25}
    ]
    
    # Check for low stock
    low_stock_threshold = 10
    low_stock_count = 0
    
    for product in products:
        if product["stock"] < low_stock_threshold:
            low_stock_count += 1
            
            # STRUCTLOG: Clean syntax for warnings with context
            log.warning(
                f"Low stock alert: {product['name']}",
                product_id=product["id"],
                product_name=product["name"],
                current_stock=product["stock"],
                threshold=low_stock_threshold
            )
    
    if PROMETHEUS_ENABLED:
        products_low_stock.set(low_stock_count)
    
    log.info(
        "Products retrieved successfully",
        endpoint="/products",
        count=len(products),
        low_stock_items=low_stock_count
    )
    
    return {"products": products, "total": len(products)}


@app.get("/users")
def get_users():
    """
    Get all users (admin only)
    
    STRUCTLOG FEATURE: Audit logging with structured data
    """
    log.debug("Admin endpoint accessed", endpoint="/users")
    
    # Simulate admin check
    is_admin = random.random() > 0.1
    
    if not is_admin:
        # STRUCTLOG: Audit trail with context
        log.warning(
            "Unauthorized access attempt to admin endpoint",
            endpoint="/users",
            user_id="guest_user",
            reason="missing_admin_privilege",
            action="access_denied",
            security_event=True  # Flag for SIEM systems
        )
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Log successful admin access
    log.info(
        "Admin access granted",
        endpoint="/users",
        user_id="admin_123",
        action="view_all_users",
        audit=True  # Audit trail marker
    )
    
    time.sleep(0.1)
    
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "active": True},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "active": True},
        {"id": 3, "name": "Bob Wilson", "email": "bob@example.com", "active": False}
    ]
    
    log.info(
        "Users retrieved successfully",
        endpoint="/users",
        count=len(users),
        admin_check=True
    )
    
    return {"users": users, "total": len(users)}


@app.get("/error")
def trigger_error():
    """
    Trigger error for testing
    
    STRUCTLOG FEATURE: Excellent exception logging with exc_info=True
    """
    log.warning("Error endpoint accessed - intentional error will be triggered")
    
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        # STRUCTLOG: Beautiful exception formatting
        log.error(
            "Division by zero error triggered",
            endpoint="/error",
            error_type="ZeroDivisionError",
            error_message=str(e),
            test_scenario=True,
            exc_info=True  # Structlog formats this beautifully!
        )
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error: Division by zero"
        )


# ==============================================================================
# HEALTH CHECK ENDPOINTS
# ==============================================================================

@app.get("/health")
def health_check():
    """Liveness probe"""
    log.info(
        "Liveness probe checked",
        endpoint="/health",
        status="healthy",
        timestamp=datetime.now().isoformat()
    )
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ready")
def readiness_check():
    """Readiness probe with random failures"""
    is_ready = random.random() > 0.1
    
    if not is_ready:
        log.warning(
            "Readiness check failed",
            endpoint="/ready",
            database="disconnected",
            cache="disconnected",
            status="not_ready"
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "Dependencies unavailable",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    log.info(
        "Readiness probe passed",
        endpoint="/ready",
        database="connected",
        cache="connected",
        status="ready"
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
    """Startup probe"""
    log.info(
        "Startup probe checked",
        endpoint="/startup",
        initialization="complete",
        status="ready"
    )
    
    return {
        "status": "ready",
        "initialization": "complete",
        "timestamp": datetime.now().isoformat()
    }


# ==============================================================================
# PROMETHEUS METRICS ENDPOINT
# ==============================================================================

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """Prometheus metrics endpoint"""
    if not PROMETHEUS_ENABLED:
        log.warning("Metrics endpoint accessed but Prometheus not enabled")
        raise HTTPException(
            status_code=503,
            detail="Prometheus metrics not available"
        )
    
    try:
        system_cpu_usage.set(psutil.cpu_percent(interval=0.1))
        system_memory_usage.set(psutil.virtual_memory().percent)
        
        log.debug(
            "System metrics updated",
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent
        )
    except Exception as e:
        log.error("Failed to update system metrics", error=str(e))
    
    log.info("Metrics endpoint accessed")
    return generate_latest()


# ==============================================================================
# GRAFANA INTEGRATION ENDPOINTS
# ==============================================================================

@app.get("/grafana/health")
def grafana_health():
    """
    Grafana health check endpoint
    Used by Grafana to verify the data source is available
    """
    log.info("Grafana health check")
    return {"status": "ok", "message": "E-commerce API is healthy"}


@app.post("/grafana/search")
def grafana_search(request: Request):
    """
    Grafana search endpoint
    Returns available metrics for querying
    """
    log.info("Grafana search request")
    
    available_metrics = [
        "http_requests_total",
        "http_request_duration_seconds",
        "system_cpu_usage_percent",
        "system_memory_usage_percent",
        "products_low_stock_total",
        "request_rate",
        "error_rate",
        "latency_p95",
        "latency_p99"
    ]
    
    return available_metrics


@app.post("/grafana/query")
async def grafana_query(request: Request):
    """
    Grafana query endpoint
    Returns time-series data for visualization
    """
    body = await request.json()
    log.info("Grafana query request", query=body)
    
    # Example response format for Grafana
    # In production, this would query actual metrics
    return {
        "target": body.get("target", "unknown"),
        "datapoints": [
            [100, int(time.time() * 1000)],
            [105, int((time.time() - 60) * 1000)],
            [95, int((time.time() - 120) * 1000)]
        ]
    }


@app.post("/grafana/annotations")
async def grafana_annotations(request: Request):
    """
    Grafana annotations endpoint
    Returns events/annotations for the dashboard
    """
    body = await request.json()
    log.info("Grafana annotations request", query=body)
    
    # Example annotations (deployments, alerts, etc.)
    return [
        {
            "annotation": "deployment",
            "time": int(time.time() * 1000),
            "title": "API Deployment",
            "tags": ["deployment", "production"],
            "text": "Deployed version 2.0.0 with structlog"
        }
    ]


@app.get("/grafana/dashboard")
def get_grafana_info():
    """
    Get Grafana dashboard information and quick links
    """
    log.info("Grafana dashboard info requested")
    
    return {
        "message": "Grafana Integration Active",
        "grafana_url": "http://localhost:3000",
        "prometheus_url": "http://localhost:9090",
        "credentials": {
            "username": "admin",
            "password": "admin123",
            "note": "Change password after first login!"
        },
        "dashboards": {
            "ecommerce_api": "E-commerce API Monitoring Dashboard",
            "url": "http://localhost:3000/d/ecommerce-api-dashboard"
        },
        "data_sources": {
            "prometheus": "http://prometheus:9090",
            "loki": "http://loki:3100"
        },
        "setup_instructions": {
            "1": "Run: docker-compose up -d",
            "2": "Access Grafana: http://localhost:3000",
            "3": "Login with admin/admin123",
            "4": "View dashboard: E-commerce API Monitoring"
        }
    }


# ==============================================================================
# GLOBAL EXCEPTION HANDLER
# ==============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structlog"""
    log.critical(
        "Unhandled exception in application",
        path=request.url.path,
        method=request.method,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
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
    # ANSI colors for banner
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    print(f"\n{CYAN}{'=' * 80}{RESET}")
    print(f"{BOLD}{MAGENTA}🚀 E-COMMERCE API - STRUCTLOG IMPLEMENTATION{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}\n")
    
    print(f"{GREEN}✅ Using:{RESET} {WHITE}Structlog (Production-grade logging library){RESET}")
    print(f"{GREEN}✅ Compare with:{RESET} {WHITE}starter_code.py (Custom logger){RESET}")
    
    print(f"\n{BOLD}{BLUE}📋 STRUCTLOG FEATURES:{RESET}")
    print(f"{GREEN}   ✓{RESET} Context binding with .bind()")
    print(f"{GREEN}   ✓{RESET} Processor-based formatting")
    print(f"{GREEN}   ✓{RESET} {YELLOW}Colorful{RESET} structured logging")
    print(f"{GREEN}   ✓{RESET} Thread-safe context management")
    print(f"{GREEN}   ✓{RESET} JSON output for log aggregation")
    print(f"{GREEN}   ✓{RESET} Beautiful exception formatting")
    print(f"{GREEN}   ✓{RESET} Production-ready and battle-tested")
    
    print(f"\n{BOLD}{BLUE}🔗 API ENDPOINTS:{RESET}")
    print(f"{CYAN}   •{RESET} Home:           {WHITE}http://localhost:8001{RESET}")
    print(f"{CYAN}   •{RESET} API Docs:       {WHITE}http://localhost:8001/docs{RESET}")
    print(f"{CYAN}   •{RESET} Products:       {WHITE}http://localhost:8001/products{RESET}")
    print(f"{CYAN}   •{RESET} Users:          {WHITE}http://localhost:8001/users{RESET}")
    print(f"{CYAN}   •{RESET} Error Test:     {WHITE}http://localhost:8001/error{RESET}")
    print(f"{CYAN}   •{RESET} Health:         {WHITE}http://localhost:8001/health{RESET}")
    print(f"{CYAN}   •{RESET} Readiness:      {WHITE}http://localhost:8001/ready{RESET}")
    print(f"{CYAN}   •{RESET} Startup:        {WHITE}http://localhost:8001/startup{RESET}")
    if PROMETHEUS_ENABLED:
        print(f"{CYAN}   •{RESET} Metrics:        {WHITE}http://localhost:8001/metrics{RESET}")
    print(f"{CYAN}   •{RESET} Grafana Info:   {WHITE}http://localhost:8001/grafana/dashboard{RESET}")
    
    print(f"\n{BOLD}{BLUE}📊 MONITORING STACK:{RESET}")
    print(f"{GREEN}   ✓{RESET} Grafana:        {WHITE}http://localhost:3000{RESET} {YELLOW}(admin/admin123){RESET}")
    print(f"{GREEN}   ✓{RESET} Prometheus:     {WHITE}http://localhost:9090{RESET}")
    print(f"{GREEN}   ✓{RESET} Loki:           {WHITE}http://localhost:3100{RESET}")
    print(f"{MAGENTA}   ℹ{RESET}  Start stack:   {YELLOW}docker-compose up -d{RESET}")
    
    print(f"\n{BOLD}{MAGENTA}📝 LOG FILE:{RESET} {YELLOW}logs/structlog_ecommerce.log{RESET}")
    print(f"{CYAN}{'=' * 80}{RESET}")
    print(f"\n{BOLD}{GREEN}🎯 Starting server on port 8001...{RESET}\n")
    
    log.info(
        "Application startup initiated",
        version="2.0.0",
        logger="structlog",
        prometheus_enabled=PROMETHEUS_ENABLED,
        host="127.0.0.1",
        port=8001
    )
    
    # Run on port 8001 to avoid conflict with starter_code.py on 8000
    uvicorn.run(app, host="127.0.0.1", port=8001)
