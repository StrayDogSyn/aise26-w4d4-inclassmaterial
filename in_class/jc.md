# Log Analysis with jq

This document contains useful `jq` commands for analyzing the structured JSON logs from your FastAPI server.

## Basic Setup

First, make sure you have `jq` installed:

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Windows (with Chocolatey)
choco install jq
```

## Basic Log Analysis Commands

### 1. View All Logs

```bash
cat library.log | jq .
```

### 2. Pretty Print Logs

```bash
cat library.log | jq -r '.'
```

### 3. Filter by Log Level

```bash
# Show only INFO logs
cat library.log | jq 'select(.level == "INFO")'

# Show only ERROR logs
cat library.log | jq 'select(.level == "ERROR")'

# Show only WARNING logs
cat library.log | jq 'select(.level == "WARNING")'
```

### 4. Filter by Time Range

```bash
# Logs from the last hour (adjust timestamp as needed)
cat library.log | jq 'select(.timestamp > "2024-01-15T10:00:00")'

# Logs from a specific time period
cat library.log | jq 'select(.timestamp >= "2024-01-15T09:00:00" and .timestamp <= "2024-01-15T11:00:00")'
```

## Advanced Analysis

### 5. Count Log Levels

```bash
# Count occurrences of each log level
cat library.log | jq -r '.level' | sort | uniq -c

# Or using jq alone
cat library.log | jq -s 'group_by(.level) | map({level: .[0].level, count: length})'
```

### 6. Extract Unique Messages

```bash
# Show all unique log messages
cat library.log | jq -r '.message' | sort | uniq

# Count occurrences of each message
cat library.log | jq -r '.message' | sort | uniq -c | sort -nr
```

### 7. Find Error Patterns

```bash
# Show all ERROR messages
cat library.log | jq 'select(.level == "ERROR") | .message'

# Find logs containing specific keywords
cat library.log | jq 'select(.message | contains("User not found"))'

# Find logs containing "404" or "500"
cat library.log | jq 'select(.message | contains("404") or contains("500"))'
```

### 8. Analyze Request Patterns

```bash
# Show all endpoint hits
cat library.log | jq 'select(.message | contains("Hit root endpoint"))'

# Find all user-related logs
cat library.log | jq 'select(.message | contains("User not found") or contains("users"))'

# Find all book-related logs
cat library.log | jq 'select(.message | contains("books"))'
```

## Server Performance Analysis

### 9. Monitor Server Startup

```bash
# Show server startup logs
cat library.log | jq 'select(.message | contains("Starting server"))'
```

### 10. Track Endpoint Usage

```bash
# Count hits to root endpoint
cat library.log | jq -s 'map(select(.message == "Hit root endpoint")) | length'

# Show all endpoint access patterns
cat library.log | jq 'select(.message | contains("Hit") or contains("endpoint"))'
```

## Chaos Testing Analysis

### 11. Analyze Chaos Test Results

```bash
# Show all error logs from chaos testing
cat library.log | jq 'select(.level == "ERROR" or .level == "WARNING")'

# Find 404 errors (invalid users/books)
cat library.log | jq 'select(.message | contains("User not found"))'

# Find 500 errors (mock errors)
cat library.log | jq 'select(.message | contains("Mock error"))'
```

### 12. Performance Metrics

```bash
# Show logs with timing information (if you add response times to logs)
cat library.log | jq 'select(.response_time)'

# Find slow requests (if response_time is logged)
cat library.log | jq 'select(.response_time and .response_time > 1.0)'
```

## Real-time Monitoring

### 13. Live Log Monitoring

```bash
# Watch logs in real-time
tail -f library.log | jq .

# Monitor only errors in real-time
tail -f library.log | jq 'select(.level == "ERROR")'

# Monitor specific patterns
tail -f library.log | jq 'select(.message | contains("User not found"))'
```

## Data Export and Reporting

### 14. Export to CSV

```bash
# Export logs to CSV format
cat library.log | jq -r '[.timestamp, .level, .message] | @csv' > logs.csv
```

### 15. Generate Summary Report

```bash
# Create a summary report
cat library.log | jq -s '
{
  total_logs: length,
  levels: group_by(.level) | map({level: .[0].level, count: length}),
  unique_messages: [.[] | .message] | unique | length,
  time_range: {
    earliest: min_by(.timestamp).timestamp,
    latest: max_by(.timestamp).timestamp
  }
}'
```

### 16. Find Most Common Errors

```bash
# Show most frequent error messages
cat library.log | jq -r 'select(.level == "ERROR") | .message' | sort | uniq -c | sort -nr | head -10
```

## Custom Analysis Examples

### 17. Analyze by Time Intervals

```bash
# Group logs by hour
cat library.log | jq -s 'group_by(.timestamp | split("T")[1] | split(":")[0]) | map({hour: .[0].timestamp | split("T")[1] | split(":")[0], count: length})'
```

### 18. Find Anomalies

```bash
# Find logs with unusual patterns
cat library.log | jq 'select(.message | length > 100)'

# Find logs with special characters or unusual content
cat library.log | jq 'select(.message | contains("🚀") or contains("💥"))'
```

## Tips for Effective Log Analysis

1. **Use `jq` with `less` for large files:**

   ```bash
   cat library.log | jq . | less
   ```

2. **Combine with other tools:**

   ```bash
   # Count total lines
   cat library.log | wc -l

   # Find specific patterns with grep + jq
   cat library.log | grep "ERROR" | jq .
   ```

3. **Save filtered results:**

   ```bash
   # Save error logs to separate file
   cat library.log | jq 'select(.level == "ERROR")' > errors.json
   ```

4. **Create aliases for common commands:**
   ```bash
   alias log-errors='cat library.log | jq "select(.level == \"ERROR\")"'
   alias log-info='cat library.log | jq "select(.level == \"INFO\")"'
   alias log-warnings='cat library.log | jq "select(.level == \"WARNING\")"'
   ```

## Example Workflow

```bash
# 1. Check if server is running and logging
cat library.log | jq 'select(.message | contains("Starting server"))'

# 2. Run your chaos test
python chaos.py

# 3. Analyze the results
cat library.log | jq 'select(.level == "ERROR" or .level == "WARNING")'

# 4. Count success vs error rates
cat library.log | jq -s 'group_by(.level) | map({level: .[0].level, count: length})'

# 5. Find specific error patterns
cat library.log | jq 'select(.message | contains("User not found"))'
```
