# 🚀 E-commerce API Logging Breakouts

This repository contains a FastAPI-based e-commerce API with structured logging exercises. Complete these breakouts to learn about logging best practices, monitoring, and observability.

## 📋 Prerequisites

- Python 3.8+
- FastAPI
- uvicorn
- Basic understanding of Python logging

## 🏪 API Overview

The e-commerce API includes:

- **Products endpoint**: `/products` - Get all products
- **Users endpoint**: `/users` - Get all users (admin)
- **Error endpoint**: `/error` - Trigger errors for testing
- **Health checks**: `/health`, `/ready`, `/startup`

---

## # Breakout 1 - 10 minutes: Design Your Logs

**Objective**: Design the logs you want to display for this e-commerce store.

### 📝 Task

Write out the log messages you want to capture in commented code format. Consider:

- **What events should be logged?**
- **What information is important to capture?**
- **What log levels should be used?**
- **What context data is needed?**

### 💡 Example Structure

```python
# Example log design for products endpoint:
# INFO - "Products requested successfully" - {"endpoint": "/products", "count": 3, "response_time": 0.05}
# ERROR - "Product not found" - {"endpoint": "/products/999", "product_id": 999, "error": "not_found"}
# WARNING - "Slow database query" - {"endpoint": "/products", "query_time": 2.5, "threshold": 1.0}
```

### 🎯 Deliverable

Create a comment block in your code with your designed log messages for each endpoint.

---

## # Breakout 2 - 30 minutes: Set Up Structured Logging

**Objective**: Implement structured logging for all endpoints.

### 📝 Tasks

1. **Create a logger.py file** with:

   - Specific logger name (not root logger)
   - Text format with timestamp, level, message, and extra context
   - Log to a file (e.g., `ecommerce.log`)
   - Prevent other loggers from cluttering your logs

2. **Add logging to all endpoints**:

   - Use different log levels (info, warning, error, debug)
   - Include relevant context data (user_id, product_id, etc.)
   - Log both successful operations and errors
   - Use structured logging with extra fields

3. **Test your logging**:
   - Make API calls to see logs in action
   - Test error conditions
   - Verify different log levels
   - Check the log file output

### 🎯 Deliverable

- Working `logger.py` file
- All endpoints with appropriate logging
- Log file with structured entries

### 📚 Reference

Look at `../logging demo/logger.py` for inspiration.

---

## # Breakout 3 - 30 minutes: Health Checks + Monitoring

**Objective**: Add logging to health check endpoints and visualize logs with Prometheus and Grafana.

### 📝 Tasks

1. **Add logging to health check endpoints**:

   - `/health` - Liveness probe logging
   - `/ready` - Readiness probe logging
   - `/startup` - Startup probe logging
   - Include appropriate log levels and context

2. **Set up Prometheus metrics**:

   - Add Prometheus client to your app
   - Create metrics endpoints
   - Track request counts, response times, errors

3. **Set up Grafana visualization**:
   - Install and configure Grafana
   - Connect to Prometheus data source
   - Create dashboards for your metrics
   - Visualize log data and system health

### 🎯 Deliverable

- Health check endpoints with logging
- Prometheus metrics collection
- Grafana dashboard showing your API metrics
- Documentation of your monitoring setup

### 📚 Reference

Look at `../logging demo/` for Prometheus and Grafana examples.

---

## 🚀 Getting Started

1. **Clone and setup**:

   ```bash
   cd breakouts
   pip install fastapi uvicorn
   ```

2. **Run the starter code**:

   ```bash
   python3 starter_code.py
   ```

3. **Test the API**:
   - Visit: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Test endpoints: `/products`, `/users`, `/error`

## 📊 Success Criteria

### Breakout 1 ✅

- [ ] Designed log messages for all endpoints
- [ ] Documented log levels and context data
- [ ] Considered error scenarios and warnings

### Breakout 2 ✅

- [ ] Created working logger.py file
- [ ] Added logging to all endpoints
- [ ] Generated structured log file
- [ ] Tested different scenarios

### Breakout 3 ✅

- [ ] Health check endpoints with logging
- [ ] Prometheus metrics working
- [ ] Grafana dashboard created
- [ ] Monitoring system operational

## 🎯 Learning Objectives

By completing these breakouts, you will understand:

- **Logging best practices** for production applications
- **Structured logging** with context and metadata
- **Health check patterns** for monitoring
- **Observability** with Prometheus and Grafana
- **Error handling** and debugging techniques

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

**Happy Logging! 📊✨**
