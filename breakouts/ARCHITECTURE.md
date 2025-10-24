# 🏗️ Grafana Monitoring Architecture

## System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTIONS                                 │
└─────────────────────────────────────────────────────────────────────────┘
            │                    │                      │
            │ Browse             │ API Calls            │ Run Tests
            ↓                    ↓                      ↓
   ┌────────────────┐   ┌────────────────┐    ┌─────────────────┐
   │   Grafana UI   │   │   server.py    │    │ chaos_test_     │
   │  localhost:3000│   │ localhost:8001 │    │   server.py     │
   │                │   │                │    │                 │
   │ • Dashboards   │   │ • REST API     │    │ • 100 requests  │
   │ • Panels       │   │ • /products    │    │ • Good/Bad mix  │
   │ • Queries      │   │ • /users       │    │ • Statistics    │
   │ • Alerts       │   │ • /health      │    │                 │
   └───────┬────────┘   └────┬───────────┘    └────────┬────────┘
           │                 │                          │
           │ Query           │ Expose /metrics          │ HTTP Requests
           │                 │                          │
           ↓                 ↓                          ↓
   ┌────────────────────────────────────────────────────────────┐
   │                    DATA LAYER                              │
   └────────────────────────────────────────────────────────────┘
           │                                    │
           │                                    │
  ┌────────↓─────────┐              ┌──────────↓────────┐
  │   Prometheus     │              │      Loki         │
  │ localhost:9090   │              │  localhost:3100   │
  │                  │              │                   │
  │ • Metrics Store  │              │ • Log Store       │
  │ • Time Series DB │              │ • Log Aggregation │
  │ • PromQL         │              │ • LogQL           │
  │ • Scraping       │              │                   │
  └────────▲─────────┘              └──────────▲────────┘
           │                                    │
           │ Scrape                             │ Ship Logs
           │ Every 15s                          │
           │                                    │
  ┌────────┴─────────┐              ┌──────────┴────────┐
  │  /metrics        │              │    Promtail       │
  │  Endpoint        │              │  localhost:9080   │
  │                  │              │                   │
  │ • Counter        │              │ • File Watcher    │
  │ • Gauge          │              │ • JSON Parser     │
  │ • Histogram      │              │ • Label Extractor │
  └──────────────────┘              └──────────▲────────┘
                                               │
                                               │ Read Files
                                               │
                                    ┌──────────┴────────┐
                                    │   logs/           │
                                    │ *.log files       │
                                    │                   │
                                    │ • JSON structured │
                                    │ • Rotating        │
                                    └───────────────────┘
```

## Component Details

### 1. Grafana (Port 3000)
```text
┌──────────────────────────────────┐
│         GRAFANA                  │
├──────────────────────────────────┤
│ Purpose:                         │
│ • Visualization & Dashboards     │
│ • Query interface                │
│ • Alerting                       │
│ • User management                │
├──────────────────────────────────┤
│ Features:                        │
│ ✓ Auto-provisioned datasources  │
│ ✓ Pre-built dashboards          │
│ ✓ Real-time updates (5s)        │
│ ✓ Multiple visualization types  │
│ ✓ Threshold alerts              │
├──────────────────────────────────┤
│ Access:                          │
│ URL: http://localhost:3000       │
│ User: admin                      │
│ Pass: admin123                   │
└──────────────────────────────────┘
```

### 2. Prometheus (Port 9090)
```text
┌──────────────────────────────────┐
│        PROMETHEUS                │
├──────────────────────────────────┤
│ Purpose:                         │
│ • Metrics collection             │
│ • Time-series database           │
│ • Scraping endpoints             │
│ • Data retention                 │
├──────────────────────────────────┤
│ Metrics Collected:               │
│ • http_requests_total            │
│ • http_request_duration_seconds  │
│ • system_cpu_usage_percent       │
│ • system_memory_usage_percent    │
│ • products_low_stock_total       │
├──────────────────────────────────┤
│ Configuration:                   │
│ • Scrape interval: 15s           │
│ • Targets: localhost:8000/8001   │
│ • Storage: TSDB                  │
│ • Query: PromQL                  │
└──────────────────────────────────┘
```

### 3. Loki (Port 3100)
```text
┌──────────────────────────────────┐
│           LOKI                   │
├──────────────────────────────────┤
│ Purpose:                         │
│ • Log aggregation                │
│ • Log storage                    │
│ • Log querying (LogQL)           │
│ • Label-based indexing           │
├──────────────────────────────────┤
│ Features:                        │
│ ✓ Like Prometheus for logs       │
│ ✓ Efficient storage              │
│ ✓ Label indexing                 │
│ ✓ JSON log parsing               │
├──────────────────────────────────┤
│ Integration:                     │
│ • Receives from Promtail         │
│ • Queries from Grafana           │
│ • Structured logs (JSON)         │
└──────────────────────────────────┘
```

### 4. Promtail (Port 9080)
```text
┌──────────────────────────────────┐
│         PROMTAIL                 │
├──────────────────────────────────┤
│ Purpose:                         │
│ • Log file watching              │
│ • Log shipping to Loki           │
│ • Log parsing & labeling         │
│ • Pipeline processing            │
├──────────────────────────────────┤
│ Process:                         │
│ 1. Watch logs/*.log files        │
│ 2. Parse JSON structure          │
│ 3. Extract labels                │
│ 4. Ship to Loki                  │
├──────────────────────────────────┤
│ Configuration:                   │
│ • Path: /var/log/app/*.log       │
│ • Format: JSON                   │
│ • Labels: level, logger          │
└──────────────────────────────────┘
```

### 5. E-commerce API (Port 8001)
```text
┌──────────────────────────────────┐
│       E-COMMERCE API             │
│         (server.py)              │
├──────────────────────────────────┤
│ Endpoints:                       │
│ • GET  /                         │
│ • GET  /products                 │
│ • GET  /users                    │
│ • GET  /health                   │
│ • GET  /ready                    │
│ • GET  /startup                  │
│ • GET  /error                    │
│ • GET  /metrics (Prometheus)     │
├──────────────────────────────────┤
│ Grafana Endpoints:               │
│ • GET  /grafana/health           │
│ • POST /grafana/search           │
│ • POST /grafana/query            │
│ • POST /grafana/annotations      │
│ • GET  /grafana/dashboard        │
├──────────────────────────────────┤
│ Logging:                         │
│ • Structlog library              │
│ • JSON format                    │
│ • Console + File                 │
│ • Context binding                │
└──────────────────────────────────┘
```

## Data Flow Diagram

### Metrics Flow
```text
API Request
    │
    ↓
[Middleware]
    │
    ├─→ Log to structlog ──→ logs/structlog_ecommerce.log
    │                               │
    ↓                               ↓
[Update Metrics]              [Promtail reads]
    │                               │
    ↓                               ↓
[Counter.inc()]               [Ships to Loki]
[Gauge.set()]                       │
[Histogram.observe()]               ↓
    │                         [Loki stores]
    ↓                               │
[Expose /metrics]                   ↓
    │                         [Grafana queries]
    ↓
[Prometheus scrapes every 15s]
    │
    ↓
[Prometheus stores in TSDB]
    │
    ↓
[Grafana queries with PromQL]
    │
    ↓
[Dashboard updates (5s refresh)]
    │
    ↓
[User sees visualization]
```

### Log Flow
```text
Application Event
    │
    ↓
[Structlog Logger]
    │
    ├─→ Console Output (colored)
    │
    └─→ File Output (JSON)
            │
            ↓
      logs/structlog_ecommerce.log
            │
            ↓
      [Promtail watches file]
            │
            ↓
      [Parse JSON structure]
            │
            ├─→ Extract: level, logger, message
            ├─→ Extract: request_id, path, method
            └─→ Extract: duration, status
                    │
                    ↓
            [Add labels for indexing]
                    │
                    ↓
            [Ship to Loki API]
                    │
                    ↓
            [Loki indexes by labels]
                    │
                    ↓
            [Loki stores log entries]
                    │
                    ↓
            [Grafana Explore tab]
                    │
                    ↓
            [LogQL queries]
                    │
                    ↓
            [User searches logs]
```

## Dashboard Panel Connections

```text
┌─────────────────────────────────────────────────────────────┐
│              E-COMMERCE API MONITORING DASHBOARD             │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ↓                                       ↓
[Prometheus Data Source]              [Loki Data Source]
        │                                       │
        ├──→ Panel 1: HTTP Request Rate        └──→ (Future: Log viewer)
        │    Query: rate(http_requests_total[1m])
        │
        ├──→ Panel 2: Total Requests
        │    Query: sum(http_requests_total)
        │
        ├──→ Panel 3: CPU Usage
        │    Query: system_cpu_usage_percent
        │
        ├──→ Panel 4: Request Duration
        │    Query: histogram_quantile(0.95, ...)
        │
        ├──→ Panel 5: Memory Usage
        │    Query: system_memory_usage_percent
        │
        ├──→ Panel 6: Low Stock Products
        │    Query: products_low_stock_total
        │
        └──→ Panel 7: Requests by Status
             Query: sum(...) by (status)
```

## Docker Network Topology

```text
┌────────────────────────────────────────────────────────┐
│         Docker Network: monitoring                     │
└────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Grafana     │ │ Prometheus   │ │    Loki      │
│ Container    │ │  Container   │ │  Container   │
│              │ │              │ │              │
│ Volume:      │ │ Volume:      │ │              │
│ grafana-data │ │ prometheus-  │ │              │
│              │ │   data       │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │ HTTP           │ HTTP           │ HTTP
       │                │                │
       └────────────────┴────────────────┘
                        │
                host.docker.internal
                        │
                        ↓
                ┌──────────────┐
                │  Host OS     │
                │              │
                │ • server.py  │
                │   :8001      │
                │ • starter_   │
                │   code.py    │
                │   :8000      │
                └──────────────┘
```

## Deployment Sequence

```text
Step 1: Start Containers
    │
    ├─→ docker-compose up -d
    │       │
    │       ├─→ Pull images (if needed)
    │       ├─→ Create network
    │       ├─→ Create volumes
    │       ├─→ Start Prometheus
    │       ├─→ Start Loki
    │       ├─→ Start Promtail
    │       └─→ Start Grafana
    │
    ↓
Step 2: Provision Grafana
    │
    ├─→ Read datasources.yml
    │   └─→ Create Prometheus datasource
    │   └─→ Create Loki datasource
    │
    ├─→ Read dashboards.yml
    │   └─→ Load ecommerce-dashboard.json
    │
    ↓
Step 3: Start Application
    │
    ├─→ python server.py
    │   └─→ Expose /metrics endpoint
    │   └─→ Write logs to files
    │
    ↓
Step 4: Data Collection Begins
    │
    ├─→ Prometheus scrapes /metrics (15s)
    ├─→ Promtail ships logs to Loki
    │
    ↓
Step 5: Visualization Ready
    │
    └─→ Open http://localhost:3000
        └─→ View dashboard
```

---

**This architecture provides production-grade observability!** 📊🏗️✨
