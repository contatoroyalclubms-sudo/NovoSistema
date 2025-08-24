#!/bin/bash

# Performance Testing Suite for Event Management System
# This script runs various performance tests using K6

set -e

echo "🚀 Starting Performance Test Suite for Event Management System"
echo "=============================================================="

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
ADMIN_EMAIL=${ADMIN_EMAIL:-"admin@test.com"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin123"}
RESULTS_DIR="./performance_results"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if K6 is installed
if ! command -v k6 &> /dev/null; then
    echo "❌ K6 is not installed. Please install K6 first:"
    echo "   Visit: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

# Check if API is running
echo "🔍 Checking if API is accessible at $API_URL"
if ! curl -f -s "$API_URL/health" > /dev/null 2>&1; then
    echo "❌ API is not accessible at $API_URL"
    echo "   Please start the API server first"
    exit 1
fi

echo "✅ API is accessible"

# Function to run a K6 test
run_k6_test() {
    local test_name="$1"
    local test_file="$2"
    local options="$3"
    
    echo ""
    echo "📊 Running $test_name..."
    echo "----------------------------------------"
    
    k6 run \
        --env API_URL="$API_URL" \
        --env ADMIN_EMAIL="$ADMIN_EMAIL" \
        --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
        $options \
        --out json="$RESULTS_DIR/${test_name}_results.json" \
        --out csv="$RESULTS_DIR/${test_name}_results.csv" \
        "$test_file"
    
    echo "✅ $test_name completed"
    echo "   Results saved to: $RESULTS_DIR/${test_name}_results.*"
}

# 1. Smoke Test - Quick validation
run_k6_test "smoke_test" "k6_load_tests.js" "--vus 1 --duration 30s"

# 2. Load Test - Normal load
run_k6_test "load_test" "k6_load_tests.js" "--vus 10 --duration 5m"

# 3. Stress Test - High load
run_k6_test "stress_test" "k6_load_tests.js" "--vus 50 --duration 3m"

# 4. Spike Test - Sudden traffic spikes
echo ""
echo "📈 Running Spike Test..."
echo "----------------------------------------"
k6 run \
    --env API_URL="$API_URL" \
    --env ADMIN_EMAIL="$ADMIN_EMAIL" \
    --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    --stage 30s:1 \
    --stage 1m:100 \
    --stage 30s:1 \
    --out json="$RESULTS_DIR/spike_test_results.json" \
    --out csv="$RESULTS_DIR/spike_test_results.csv" \
    "k6_load_tests.js"

echo "✅ Spike test completed"

# 5. Volume Test - Large amount of data
echo ""
echo "📦 Running Volume Test..."
echo "----------------------------------------"
k6 run \
    --env API_URL="$API_URL" \
    --env ADMIN_EMAIL="$ADMIN_EMAIL" \
    --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    --vus 20 \
    --duration 10m \
    --out json="$RESULTS_DIR/volume_test_results.json" \
    --out csv="$RESULTS_DIR/volume_test_results.csv" \
    "k6_load_tests.js"

echo "✅ Volume test completed"

# 6. Endurance Test - Long duration
echo ""
echo "⏱️ Running Endurance Test (this will take a while)..."
echo "----------------------------------------"
k6 run \
    --env API_URL="$API_URL" \
    --env ADMIN_EMAIL="$ADMIN_EMAIL" \
    --env ADMIN_PASSWORD="$ADMIN_PASSWORD" \
    --vus 10 \
    --duration 30m \
    --out json="$RESULTS_DIR/endurance_test_results.json" \
    --out csv="$RESULTS_DIR/endurance_test_results.csv" \
    "k6_load_tests.js"

echo "✅ Endurance test completed"

# Generate summary report
echo ""
echo "📋 Generating Performance Test Summary"
echo "======================================"

cat > "$RESULTS_DIR/performance_summary.md" << EOF
# Performance Test Results Summary

Generated on: $(date)
API URL: $API_URL

## Test Results Overview

### Smoke Test (1 VU, 30s)
- **Purpose**: Basic functionality validation
- **Results**: See smoke_test_results.*

### Load Test (10 VUs, 5m)
- **Purpose**: Normal expected load
- **Results**: See load_test_results.*

### Stress Test (50 VUs, 3m)
- **Purpose**: High load performance
- **Results**: See stress_test_results.*

### Spike Test (1-100-1 VUs)
- **Purpose**: Traffic spike handling
- **Results**: See spike_test_results.*

### Volume Test (20 VUs, 10m)
- **Purpose**: Large data volume handling
- **Results**: See volume_test_results.*

### Endurance Test (10 VUs, 30m)
- **Purpose**: Long-term stability
- **Results**: See endurance_test_results.*

## Key Metrics Tracked

- **Response Time**: 95th percentile < 2000ms
- **Error Rate**: < 10%
- **Throughput**: Requests per second
- **Authentication Success Rate**: > 95%
- **Check-in Success Rate**: > 90%
- **Sales Success Rate**: > 90%

## Files Generated

EOF

# List all generated files
echo "- performance_summary.md (this file)" >> "$RESULTS_DIR/performance_summary.md"
for file in "$RESULTS_DIR"/*.json "$RESULTS_DIR"/*.csv; do
    if [[ -f "$file" ]]; then
        filename=$(basename "$file")
        echo "- $filename" >> "$RESULTS_DIR/performance_summary.md"
    fi
done

echo ""
echo "🎉 All Performance Tests Completed!"
echo "=================================="
echo ""
echo "📁 Results Directory: $RESULTS_DIR"
echo "📄 Summary Report: $RESULTS_DIR/performance_summary.md"
echo ""
echo "📊 To analyze results:"
echo "   - JSON files contain detailed metrics"
echo "   - CSV files can be imported into Excel/Google Sheets"
echo "   - Use k6-to-junit for CI integration"
echo ""

# Optional: Open results directory
if command -v xdg-open &> /dev/null; then
    xdg-open "$RESULTS_DIR"
elif command -v open &> /dev/null; then
    open "$RESULTS_DIR"
fi

echo "✨ Performance testing complete!"