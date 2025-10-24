"""
Test script to demonstrate colorful logging
"""
from logger import get_logger

# Get the logger
logger = get_logger()

print("\n" + "="*80)
print("🎨 TESTING COLORFUL LOGGING OUTPUT")
print("="*80 + "\n")

# Test all log levels with context data
logger.debug(
    "Debug message - used for detailed troubleshooting",
    extra={"user_id": 123, "action": "view_page"}
)

logger.info(
    "Application started successfully",
    extra={"version": "1.0.0", "port": 8000, "environment": "production"}
)

logger.warning(
    "Low stock alert detected",
    extra={"product": "Laptop", "current_stock": 3, "threshold": 10}
)

logger.error(
    "Database connection failed",
    extra={"host": "localhost", "port": 5432, "error": "connection timeout", "retry_count": 3}
)

logger.critical(
    "System failure - immediate attention required!",
    extra={"service": "payment_processor", "impact": "high", "affected_users": 1500}
)

print("\n" + "="*80)
print("✨ Color Legend:")
print("  🔍 DEBUG (Cyan)    - Detailed debugging information")
print("  ✅ INFO (Green)    - Normal operations and confirmations")
print("  ⚠️  WARNING (Yellow) - Something unexpected but handled")
print("  ❌ ERROR (Red)     - Something broke but app still runs")
print("  🚨 CRITICAL (Magenta+Bold) - System failure, immediate action needed")
print("="*80 + "\n")

print("💡 Context data is shown in cyan below each log message")
print("📁 Logs are also saved to: logs/ecommerce.log (without colors)\n")
