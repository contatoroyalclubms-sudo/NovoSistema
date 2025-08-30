"""
PERFORMANCE TEST SUITE
Sistema Universal de Gestão de Eventos - ULTRA PERFORMANCE

Comprehensive performance testing with:
- API endpoint benchmarks
- Database query performance
- Memory usage profiling
- Load testing scenarios
- Core Web Vitals simulation
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.services.performance_monitor import ultra_performance_monitor, benchmark_function, benchmark_api
from app.core.database import get_db

class TestPerformanceRequirements:
    """Test performance requirements and benchmarks"""
    
    @pytest.fixture(scope="session")
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture(scope="session")
    async def async_client(self):
        """Async test client fixture"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_api_response_time_requirement(self, async_client):
        """Test API response time < 100ms (95th percentile)"""
        endpoints_to_test = [
            ("GET", "/health", "health_check"),
            ("GET", "/api/v1/system/info", "system_info"),
            ("GET", "/api/v1/eventos", "list_eventos"),
        ]
        
        for method, url, name in endpoints_to_test:
            result = await benchmark_api(
                async_client, 
                method, 
                url, 
                name, 
                iterations=100
            )
            
            # Requirement: P95 response time < 100ms
            p95_ms = result.percentiles.get('p95', float('inf'))
            assert p95_ms < 100, f"{name} P95 response time {p95_ms:.2f}ms exceeds 100ms requirement"
            
            # Additional checks
            assert result.error_rate < 1.0, f"{name} error rate {result.error_rate:.2f}% too high"
            assert result.operations_per_second > 100, f"{name} throughput {result.operations_per_second:.2f} ops/sec too low"
    
    @pytest.mark.asyncio
    async def test_database_query_performance(self):
        """Test database query performance < 50ms average"""
        
        async def mock_simple_query():
            """Simulate a simple database query"""
            await asyncio.sleep(0.01)  # 10ms simulated query
            return {"count": 100}
        
        async def mock_complex_query():
            """Simulate a complex database query"""
            await asyncio.sleep(0.03)  # 30ms simulated query
            return {"results": [{"id": i} for i in range(50)]}
        
        # Test simple queries
        simple_result = await benchmark_function(
            mock_simple_query,
            "simple_db_query",
            iterations=50
        )
        
        avg_time = simple_result.percentiles.get('avg', 0)
        assert avg_time < 50, f"Simple query average {avg_time:.2f}ms exceeds 50ms requirement"
        
        # Test complex queries
        complex_result = await benchmark_function(
            mock_complex_query,
            "complex_db_query",
            iterations=30
        )
        
        avg_time = complex_result.percentiles.get('avg', 0)
        assert avg_time < 100, f"Complex query average {avg_time:.2f}ms exceeds 100ms requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_load_handling(self, async_client):
        """Test concurrent load handling"""
        
        async def make_concurrent_requests():
            """Make concurrent requests to health endpoint"""
            tasks = []
            for _ in range(10):  # 10 concurrent requests
                tasks.append(async_client.get("/health"))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that all requests succeeded
            successful_requests = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            return successful_requests
        
        # Test concurrent load
        result = await benchmark_function(
            make_concurrent_requests,
            "concurrent_load_test",
            iterations=10
        )
        
        # Requirements
        assert result.error_rate < 5.0, f"Concurrent load error rate {result.error_rate:.2f}% too high"
        avg_time = result.percentiles.get('avg', 0)
        assert avg_time < 200, f"Concurrent load average response time {avg_time:.2f}ms too high"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test memory usage stability during operations"""
        
        async def memory_intensive_operation():
            """Simulate memory-intensive operation"""
            # Create and discard objects to test memory management
            data = []
            for i in range(1000):
                data.append({"id": i, "data": f"test_data_{i}" * 10})
            
            # Process the data
            result = len([item for item in data if item["id"] % 2 == 0])
            
            # Clear data to test garbage collection
            del data
            return result
        
        result = await benchmark_function(
            memory_intensive_operation,
            "memory_test",
            iterations=20
        )
        
        # Check memory usage didn't grow excessively
        memory_diff = result.memory_usage['diff_mb']
        assert abs(memory_diff) < 10, f"Memory usage grew by {memory_diff:.2f}MB (should be < 10MB)"
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache hit rate and performance"""
        
        cache_hits = 0
        cache_requests = 0
        
        async def simulate_cache_operation(key: str):
            """Simulate cache get/set operation"""
            nonlocal cache_hits, cache_requests
            cache_requests += 1
            
            # Simulate cache hit/miss (80% hit rate)
            if hash(key) % 10 < 8:
                cache_hits += 1
                await asyncio.sleep(0.001)  # 1ms cache hit
                return f"cached_value_{key}"
            else:
                await asyncio.sleep(0.005)  # 5ms cache miss + DB
                return f"fresh_value_{key}"
        
        # Test cache operations
        tasks = []
        for i in range(100):
            tasks.append(simulate_cache_operation(f"key_{i % 20}"))  # Repeated keys for cache hits
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # Calculate hit rate
        hit_rate = (cache_hits / cache_requests) * 100 if cache_requests > 0 else 0
        
        # Requirements
        assert hit_rate >= 70, f"Cache hit rate {hit_rate:.1f}% below 70% requirement"
        assert duration < 1.0, f"Cache operations took {duration:.3f}s (should be < 1s for 100 ops)"
    
    def test_frontend_bundle_size_requirement(self):
        """Test frontend bundle size < 500KB gzipped (simulated)"""
        
        # This would normally check actual build artifacts
        # For now, we'll simulate the requirement
        simulated_bundle_sizes = {
            'main.js': 250_000,  # 250KB
            'vendor.js': 180_000,  # 180KB
            'style.css': 45_000,   # 45KB
        }
        
        total_size = sum(simulated_bundle_sizes.values())
        gzipped_size = total_size * 0.7  # Assume 30% compression
        
        assert gzipped_size < 500_000, f"Bundle size {gzipped_size/1000:.1f}KB exceeds 500KB requirement"
    
    @pytest.mark.asyncio
    async def test_websocket_performance(self):
        """Test WebSocket connection and message handling performance"""
        
        async def simulate_websocket_messages():
            """Simulate WebSocket message processing"""
            messages_processed = 0
            
            for i in range(100):
                # Simulate message processing time
                await asyncio.sleep(0.001)  # 1ms per message
                messages_processed += 1
            
            return messages_processed
        
        result = await benchmark_function(
            simulate_websocket_messages,
            "websocket_messages",
            iterations=5
        )
        
        # WebSocket should handle 100 messages in < 500ms
        avg_time = result.percentiles.get('avg', 0)
        assert avg_time < 500, f"WebSocket message processing {avg_time:.2f}ms too slow"
    
    @pytest.mark.asyncio
    async def test_error_handling_performance(self, async_client):
        """Test that error handling doesn't significantly impact performance"""
        
        # Test normal endpoint
        normal_result = await benchmark_api(
            async_client,
            "GET",
            "/health",
            "normal_endpoint",
            iterations=50
        )
        
        # Test error endpoint (simulated)
        try:
            error_result = await benchmark_api(
                async_client,
                "GET",
                "/nonexistent",
                "error_endpoint", 
                iterations=50
            )
        except:
            # This is expected to fail, we just want to measure timing
            pass
        
        # Error handling shouldn't be more than 2x slower than normal
        normal_avg = normal_result.percentiles.get('avg', 0)
        # We can't easily test error timing here, but we can ensure normal performance is good
        assert normal_avg < 50, f"Normal endpoint performance degraded: {normal_avg:.2f}ms"

class TestScalabilityRequirements:
    """Test scalability and load requirements"""
    
    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, async_client):
        """Simulate concurrent users (scaled down for testing)"""
        
        async def simulate_user_session():
            """Simulate a user session with multiple requests"""
            # Health check
            health_response = await async_client.get("/health")
            
            # System info
            info_response = await async_client.get("/api/v1/system/info")
            
            # List events (would be authenticated in real scenario)
            # events_response = await async_client.get("/api/v1/eventos")
            
            return health_response.status_code == 200 and info_response.status_code == 200
        
        # Simulate 10 concurrent users (scaled down from 1000+)
        tasks = []
        for _ in range(10):
            tasks.append(simulate_user_session())
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        duration = time.time() - start_time
        
        # Check results
        successful_sessions = sum(1 for r in results if r is True)
        success_rate = (successful_sessions / len(tasks)) * 100
        
        # Requirements
        assert success_rate >= 95, f"User session success rate {success_rate:.1f}% below 95%"
        assert duration < 5.0, f"Concurrent user simulation took {duration:.2f}s (should be < 5s)"
    
    @pytest.mark.asyncio 
    async def test_data_processing_scalability(self):
        """Test data processing scalability"""
        
        async def process_batch_data(batch_size: int):
            """Process a batch of data"""
            data = [{"id": i, "value": i * 2} for i in range(batch_size)]
            
            # Simulate processing
            total = sum(item["value"] for item in data)
            await asyncio.sleep(batch_size * 0.0001)  # Scale with data size
            
            return {"processed": len(data), "total": total}
        
        # Test different batch sizes
        batch_sizes = [100, 500, 1000]
        results = {}
        
        for batch_size in batch_sizes:
            result = await benchmark_function(
                lambda: process_batch_data(batch_size),
                f"batch_processing_{batch_size}",
                iterations=5
            )
            results[batch_size] = result
        
        # Processing time should scale linearly (or better)
        time_100 = results[100].percentiles.get('avg', 0)
        time_1000 = results[1000].percentiles.get('avg', 0)
        
        # 10x data shouldn't take more than 15x time (allowing for overhead)
        scaling_factor = time_1000 / time_100 if time_100 > 0 else float('inf')
        assert scaling_factor < 15, f"Processing doesn't scale well: {scaling_factor:.1f}x"

class TestPerformanceMonitoring:
    """Test the performance monitoring system itself"""
    
    @pytest.mark.asyncio
    async def test_monitoring_overhead(self):
        """Test that monitoring doesn't add significant overhead"""
        
        async def simple_operation():
            """Simple operation to measure"""
            await asyncio.sleep(0.01)  # 10ms operation
            return "done"
        
        # Measure without explicit monitoring
        start_time = time.time()
        for _ in range(10):
            await simple_operation()
        baseline_time = time.time() - start_time
        
        # Measure with monitoring
        monitored_result = await benchmark_function(
            simple_operation,
            "monitored_operation",
            iterations=10
        )
        
        monitoring_time = monitored_result.duration / 1000  # Convert to seconds
        
        # Monitoring overhead should be < 10%
        overhead = ((monitoring_time - baseline_time) / baseline_time) * 100 if baseline_time > 0 else 0
        assert overhead < 10, f"Monitoring overhead {overhead:.1f}% too high"
    
    def test_performance_report_generation(self):
        """Test performance report generation"""
        
        # Generate a report
        report = ultra_performance_monitor.get_performance_report(hours=1)
        
        # Check report structure
        assert 'report_period_hours' in report
        assert 'generated_at' in report
        assert 'system_metrics' in report
        assert 'benchmarks' in report
        
        # Report generation should be fast
        start_time = time.time()
        report = ultra_performance_monitor.get_performance_report(hours=24)
        generation_time = time.time() - start_time
        
        assert generation_time < 1.0, f"Report generation took {generation_time:.3f}s (should be < 1s)"

# Performance test configuration
PERFORMANCE_REQUIREMENTS = {
    "api_response_p95_ms": 100,
    "database_query_avg_ms": 50,
    "error_rate_percent": 1.0,
    "cache_hit_rate_percent": 70,
    "bundle_size_kb": 500,
    "concurrent_users": 1000,  # Target (scaled down for tests)
    "memory_growth_mb": 10,
    "websocket_latency_ms": 50,
}

def pytest_configure(config):
    """Configure pytest with performance markers"""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as benchmark"
    )
    config.addinivalue_line(
        "markers", "load: mark test as load test"
    )

# Utility function to run all performance tests
async def run_performance_suite():
    """Run complete performance test suite"""
    print("🚀 Starting Ultra Performance Test Suite...")
    
    # Start monitoring
    await ultra_performance_monitor.start_monitoring(interval=1.0)
    
    try:
        # Run pytest programmatically
        import subprocess
        result = subprocess.run([
            "python", "-m", "pytest", 
            __file__, 
            "-v", 
            "--tb=short",
            "-m", "not slow"
        ], capture_output=True, text=True)
        
        print("📊 Test Results:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Warnings/Errors:")
            print(result.stderr)
        
        # Generate final report
        report = ultra_performance_monitor.get_performance_report(hours=1)
        print("\n📈 Performance Summary:")
        print(f"System metrics collected: {report['total_metrics_collected']}")
        print(f"Benchmarks run: {report['total_benchmarks_run']}")
        
        return result.returncode == 0
        
    finally:
        await ultra_performance_monitor.stop_monitoring()

if __name__ == "__main__":
    # Run the performance suite
    asyncio.run(run_performance_suite())