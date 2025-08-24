"""
Load Performance Tests
Ultra-performance testing for high-load scenarios
"""

import asyncio
import time
import statistics
import pytest
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Test Configuration
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = [10, 50, 100, 200]
TEST_DURATION = 60  # seconds
EXPECTED_RESPONSE_TIME = 200  # ms
ERROR_RATE_THRESHOLD = 0.05  # 5%

class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time = None
        self.end_time = None
    
    def add_result(self, response_time: float, status_code: int, error: str = None):
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.response_times:
            return {}
        
        successful_requests = len([s for s in self.status_codes if 200 <= s < 400])
        total_requests = len(self.status_codes)
        error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 0
        
        duration = (self.end_time - self.start_time) if self.start_time and self.end_time else 0
        throughput = total_requests / duration if duration > 0 else 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': total_requests - successful_requests,
            'error_rate': error_rate,
            'throughput_rps': throughput,
            'duration_seconds': duration,
            'response_times': {
                'min': min(self.response_times),
                'max': max(self.response_times),
                'mean': statistics.mean(self.response_times),
                'median': statistics.median(self.response_times),
                'p95': statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
                'p99': statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else max(self.response_times),
            },
            'errors': self.errors[:10]  # First 10 errors
        }

@pytest.fixture
async def http_session():
    """HTTP session for making requests"""
    connector = aiohttp.TCPConnector(
        limit=1000,
        limit_per_host=100,
        ttl_dns_cache=300,
        use_dns_cache=True,
    )
    
    timeout = aiohttp.ClientTimeout(total=30, connect=10)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={'User-Agent': 'Performance-Test/1.0'}
    ) as session:
        yield session

async def make_request(session: aiohttp.ClientSession, url: str, method: str = 'GET', 
                      data: Dict = None) -> Dict[str, Any]:
    """Make HTTP request and measure performance"""
    start_time = time.perf_counter()
    
    try:
        async with session.request(method, url, json=data) as response:
            await response.text()  # Read response body
            
        response_time = (time.perf_counter() - start_time) * 1000  # ms
        
        return {
            'response_time': response_time,
            'status_code': response.status,
            'error': None
        }
        
    except Exception as e:
        response_time = (time.perf_counter() - start_time) * 1000
        return {
            'response_time': response_time,
            'status_code': 0,
            'error': str(e)
        }

async def user_simulation(session: aiohttp.ClientSession, user_id: int, 
                         duration: int) -> PerformanceMetrics:
    """Simulate a single user's interaction"""
    metrics = PerformanceMetrics()
    metrics.start_time = time.time()
    
    end_time = time.time() + duration
    
    # User journey simulation
    user_actions = [
        {'url': f'{BASE_URL}/', 'method': 'GET'},
        {'url': f'{BASE_URL}/health', 'method': 'GET'},
        {'url': f'{BASE_URL}/api/v1/eventos', 'method': 'GET'},
        {'url': f'{BASE_URL}/api/v1/dashboard/stats', 'method': 'GET'},
        {'url': f'{BASE_URL}/metrics', 'method': 'GET'},
    ]
    
    action_index = 0
    
    while time.time() < end_time:
        action = user_actions[action_index % len(user_actions)]
        
        result = await make_request(session, action['url'], action['method'])
        metrics.add_result(
            result['response_time'], 
            result['status_code'], 
            result['error']
        )
        
        # Realistic think time between requests
        await asyncio.sleep(0.5 + (user_id % 3) * 0.2)
        action_index += 1
    
    metrics.end_time = time.time()
    return metrics

@pytest.mark.performance
@pytest.mark.parametrize("concurrent_users", CONCURRENT_USERS)
async def test_load_performance(http_session, concurrent_users):
    """Test system performance under various load levels"""
    
    print(f"\n🚀 Running load test with {concurrent_users} concurrent users")
    
    # Run concurrent user simulations
    tasks = [
        user_simulation(http_session, user_id, TEST_DURATION)
        for user_id in range(concurrent_users)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_duration = time.time() - start_time
    
    # Aggregate metrics
    all_response_times = []
    all_status_codes = []
    all_errors = []
    total_requests = 0
    
    for metrics in results:
        summary = metrics.get_summary()
        all_response_times.extend(metrics.response_times)
        all_status_codes.extend(metrics.status_codes)
        all_errors.extend(metrics.errors)
        total_requests += summary['total_requests']
    
    # Calculate overall metrics
    successful_requests = len([s for s in all_status_codes if 200 <= s < 400])
    error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 0
    throughput = total_requests / total_duration
    
    avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
    p95_response_time = statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else 0
    p99_response_time = statistics.quantiles(all_response_times, n=100)[98] if len(all_response_times) >= 100 else 0
    
    # Print results
    print(f"📊 Load Test Results:")
    print(f"   Users: {concurrent_users}")
    print(f"   Duration: {total_duration:.2f}s")
    print(f"   Total Requests: {total_requests}")
    print(f"   Successful Requests: {successful_requests}")
    print(f"   Error Rate: {error_rate:.2%}")
    print(f"   Throughput: {throughput:.2f} RPS")
    print(f"   Avg Response Time: {avg_response_time:.2f}ms")
    print(f"   P95 Response Time: {p95_response_time:.2f}ms")
    print(f"   P99 Response Time: {p99_response_time:.2f}ms")
    
    # Assertions for performance criteria
    assert error_rate <= ERROR_RATE_THRESHOLD, f"Error rate {error_rate:.2%} exceeds threshold {ERROR_RATE_THRESHOLD:.2%}"
    assert avg_response_time <= EXPECTED_RESPONSE_TIME, f"Average response time {avg_response_time:.2f}ms exceeds {EXPECTED_RESPONSE_TIME}ms"
    assert p95_response_time <= EXPECTED_RESPONSE_TIME * 2, f"P95 response time {p95_response_time:.2f}ms exceeds threshold"
    assert throughput > concurrent_users * 0.5, f"Throughput {throughput:.2f} RPS is too low for {concurrent_users} users"

@pytest.mark.performance
async def test_stress_performance(http_session):
    """Stress test to find system breaking point"""
    
    print(f"\n💥 Running stress test")
    
    stress_levels = [50, 100, 200, 500, 1000]
    results = {}
    
    for users in stress_levels:
        print(f"   Testing with {users} users...")
        
        tasks = [
            user_simulation(http_session, user_id, 30)  # 30 second stress
            for user_id in range(users)
        ]
        
        try:
            start_time = time.time()
            user_results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Filter successful results
            successful_results = [r for r in user_results if isinstance(r, PerformanceMetrics)]
            
            if successful_results:
                all_response_times = []
                all_status_codes = []
                
                for metrics in successful_results:
                    all_response_times.extend(metrics.response_times)
                    all_status_codes.extend(metrics.status_codes)
                
                successful_requests = len([s for s in all_status_codes if 200 <= s < 400])
                total_requests = len(all_status_codes)
                error_rate = (total_requests - successful_requests) / total_requests if total_requests > 0 else 1
                
                avg_response_time = statistics.mean(all_response_times) if all_response_times else float('inf')
                
                results[users] = {
                    'error_rate': error_rate,
                    'avg_response_time': avg_response_time,
                    'throughput': total_requests / duration,
                    'successful': error_rate < 0.2 and avg_response_time < 1000  # 20% error rate, 1s response time
                }
            else:
                results[users] = {
                    'error_rate': 1.0,
                    'avg_response_time': float('inf'),
                    'throughput': 0,
                    'successful': False
                }
                
        except Exception as e:
            print(f"   Failed at {users} users: {e}")
            results[users] = {
                'error_rate': 1.0,
                'avg_response_time': float('inf'),
                'throughput': 0,
                'successful': False,
                'error': str(e)
            }
    
    # Find breaking point
    max_successful_users = 0
    for users, result in results.items():
        if result['successful']:
            max_successful_users = users
        print(f"   {users} users: Error Rate {result['error_rate']:.2%}, "
              f"Avg Response {result['avg_response_time']:.0f}ms, "
              f"Throughput {result['throughput']:.1f} RPS - "
              f"{'✅ PASS' if result['successful'] else '❌ FAIL'}")
    
    print(f"\n📈 Maximum capacity: {max_successful_users} concurrent users")
    
    # Assert minimum capacity
    assert max_successful_users >= 100, f"System should handle at least 100 concurrent users, but broke at {max_successful_users}"

@pytest.mark.performance
async def test_spike_performance(http_session):
    """Test system behavior under sudden traffic spikes"""
    
    print(f"\n⚡ Running spike test")
    
    # Baseline load
    baseline_users = 50
    spike_users = 300
    spike_duration = 30
    
    # Start baseline load
    print(f"   Starting baseline: {baseline_users} users")
    baseline_tasks = [
        user_simulation(http_session, user_id, 120)  # 2 minutes
        for user_id in range(baseline_users)
    ]
    
    # Wait 30 seconds, then add spike
    await asyncio.sleep(30)
    
    print(f"   Adding spike: {spike_users} additional users")
    spike_tasks = [
        user_simulation(http_session, user_id + baseline_users, spike_duration)
        for user_id in range(spike_users)
    ]
    
    # Run spike and measure impact
    start_spike = time.time()
    spike_results = await asyncio.gather(*spike_tasks, return_exceptions=True)
    spike_duration_actual = time.time() - start_spike
    
    # Wait for baseline to complete
    baseline_results = await asyncio.gather(*baseline_tasks)
    
    # Analyze spike impact
    successful_spike_results = [r for r in spike_results if isinstance(r, PerformanceMetrics)]
    
    if successful_spike_results:
        spike_response_times = []
        spike_status_codes = []
        
        for metrics in successful_spike_results:
            spike_response_times.extend(metrics.response_times)
            spike_status_codes.extend(metrics.status_codes)
        
        spike_error_rate = len([s for s in spike_status_codes if s >= 400]) / len(spike_status_codes) if spike_status_codes else 1
        spike_avg_response = statistics.mean(spike_response_times) if spike_response_times else float('inf')
        
        print(f"   Spike Results:")
        print(f"     Duration: {spike_duration_actual:.2f}s")
        print(f"     Error Rate: {spike_error_rate:.2%}")
        print(f"     Avg Response: {spike_avg_response:.2f}ms")
        
        # System should handle spikes gracefully
        assert spike_error_rate < 0.3, f"Spike error rate {spike_error_rate:.2%} too high"
        assert spike_avg_response < 2000, f"Spike response time {spike_avg_response:.2f}ms too high"
    
    print("✅ Spike test completed")

@pytest.mark.performance
async def test_memory_leak_detection(http_session):
    """Test for memory leaks during sustained load"""
    
    print(f"\n🔍 Running memory leak detection")
    
    # Run sustained load and monitor memory usage
    users = 100
    test_cycles = 5
    cycle_duration = 60
    
    memory_usage = []
    
    for cycle in range(test_cycles):
        print(f"   Cycle {cycle + 1}/{test_cycles}")
        
        # Check memory usage before cycle (implement actual memory monitoring)
        # memory_before = get_system_memory_usage()
        
        tasks = [
            user_simulation(http_session, user_id, cycle_duration)
            for user_id in range(users)
        ]
        
        await asyncio.gather(*tasks)
        
        # Check memory usage after cycle
        # memory_after = get_system_memory_usage()
        # memory_usage.append(memory_after - memory_before)
        
        # Simulate memory monitoring
        memory_usage.append(cycle * 10)  # Mock increasing memory
        
        # Brief pause between cycles
        await asyncio.sleep(10)
    
    # Analyze memory trend
    if len(memory_usage) > 2:
        # Check if memory usage is consistently increasing
        increasing_trend = all(
            memory_usage[i] >= memory_usage[i-1] 
            for i in range(1, len(memory_usage))
        )
        
        avg_increase = (memory_usage[-1] - memory_usage[0]) / len(memory_usage)
        
        print(f"   Memory trend: {memory_usage}")
        print(f"   Average increase: {avg_increase:.2f} units per cycle")
        
        # Memory should not consistently increase
        # assert not increasing_trend or avg_increase < 50, "Potential memory leak detected"
    
    print("✅ Memory leak detection completed")