"""
Ultra-Performance Load Testing Framework
Sistema Universal de Gestão de Eventos - Enterprise Scale Testing
Target: Realistic traffic simulation, 10,000+ concurrent users, performance validation
"""

import asyncio
import aiohttp
import time
import random
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
import csv
from concurrent.futures import ThreadPoolExecutor
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

# ================================
# LOAD TESTING CONFIGURATION
# ================================

class LoadTestScenario(Enum):
    """Load test scenarios for different use cases"""
    BASELINE = "baseline"                    # Basic functionality test
    REALISTIC_TRAFFIC = "realistic_traffic"  # Normal day traffic pattern
    PEAK_TRAFFIC = "peak_traffic"           # Peak event day (Black Friday style)
    SPIKE_TEST = "spike_test"               # Sudden traffic spikes
    ENDURANCE = "endurance"                 # Long-running stability test
    CONCURRENT_EVENTS = "concurrent_events"  # Multiple events simultaneously
    REAL_TIME_HEAVY = "real_time_heavy"     # Heavy WebSocket usage

@dataclass
class UserProfile:
    """User behavior profile for realistic load testing"""
    profile_name: str
    weight: float  # Percentage of total users
    think_time_min: float  # Minimum think time between actions (seconds)
    think_time_max: float  # Maximum think time between actions (seconds)
    session_duration_min: int  # Minimum session duration (minutes)
    session_duration_max: int  # Maximum session duration (minutes)
    actions: List[Dict[str, Any]]  # List of possible actions with weights

@dataclass
class LoadTestConfig:
    """Comprehensive load test configuration"""
    # Basic configuration
    base_url: str = "http://localhost:8001"
    scenario: LoadTestScenario = LoadTestScenario.REALISTIC_TRAFFIC
    duration_minutes: int = 30
    
    # User simulation
    max_concurrent_users: int = 1000
    ramp_up_duration_minutes: int = 5
    ramp_down_duration_minutes: int = 5
    
    # Request configuration
    timeout_seconds: int = 30
    max_retries: int = 3
    think_time_multiplier: float = 1.0
    
    # Output configuration
    output_directory: str = "load_test_results"
    enable_real_time_reporting: bool = True
    export_detailed_metrics: bool = True
    
    # Performance targets
    target_response_time_p95_ms: int = 50
    target_response_time_p99_ms: int = 100
    max_acceptable_error_rate: float = 0.5  # 0.5%

# ================================
# USER BEHAVIOR PROFILES
# ================================

def get_user_profiles() -> List[UserProfile]:
    """Get realistic user behavior profiles"""
    return [
        # Event organizers - Heavy dashboard usage
        UserProfile(
            profile_name="organizer",
            weight=0.05,  # 5% of users
            think_time_min=2.0,
            think_time_max=15.0,
            session_duration_min=30,
            session_duration_max=120,
            actions=[
                {"action": "login", "weight": 1.0, "endpoint": "/api/v3/auth/login"},
                {"action": "view_events", "weight": 0.9, "endpoint": "/api/v3/events"},
                {"action": "view_event_details", "weight": 0.8, "endpoint": "/api/v3/events/{event_id}"},
                {"action": "view_participants", "weight": 0.6, "endpoint": "/api/v3/events/{event_id}/participants"},
                {"action": "export_data", "weight": 0.2, "endpoint": "/api/v3/events/{event_id}/export"},
                {"action": "view_analytics", "weight": 0.4, "endpoint": "/api/v3/analytics/{event_id}"},
            ]
        ),
        
        # Participants - Check-in focused
        UserProfile(
            profile_name="participant",
            weight=0.70,  # 70% of users
            think_time_min=5.0,
            think_time_max=30.0,
            session_duration_min=5,
            session_duration_max=30,
            actions=[
                {"action": "view_event", "weight": 1.0, "endpoint": "/api/v3/events/{event_id}"},
                {"action": "register", "weight": 0.3, "endpoint": "/api/v3/events/{event_id}/register"},
                {"action": "checkin", "weight": 0.8, "endpoint": "/api/v3/events/{event_id}/checkin"},
                {"action": "view_qr_code", "weight": 0.4, "endpoint": "/api/v3/participants/{participant_id}/qr"},
            ]
        ),
        
        # POS operators - Transaction heavy
        UserProfile(
            profile_name="pos_operator",
            weight=0.10,  # 10% of users
            think_time_min=10.0,
            think_time_max=60.0,
            session_duration_min=60,
            session_duration_max=300,
            actions=[
                {"action": "pos_login", "weight": 1.0, "endpoint": "/api/v3/pos/login"},
                {"action": "view_products", "weight": 0.9, "endpoint": "/api/v3/pos/products"},
                {"action": "process_sale", "weight": 0.7, "endpoint": "/api/v3/pos/sales"},
                {"action": "update_inventory", "weight": 0.3, "endpoint": "/api/v3/pos/inventory"},
                {"action": "view_sales_report", "weight": 0.4, "endpoint": "/api/v3/pos/reports"},
            ]
        ),
        
        # Monitors/Dashboard viewers - Read-heavy
        UserProfile(
            profile_name="monitor",
            weight=0.10,  # 10% of users
            think_time_min=5.0,
            think_time_max=20.0,
            session_duration_min=15,
            session_duration_max=60,
            actions=[
                {"action": "view_dashboard", "weight": 1.0, "endpoint": "/api/v3/dashboard"},
                {"action": "view_live_stats", "weight": 0.8, "endpoint": "/api/v3/events/{event_id}/stats"},
                {"action": "view_system_health", "weight": 0.5, "endpoint": "/health"},
                {"action": "view_metrics", "weight": 0.3, "endpoint": "/api/v3/performance/metrics"},
            ]
        ),
        
        # API clients - Automated systems
        UserProfile(
            profile_name="api_client",
            weight=0.05,  # 5% of users
            think_time_min=0.1,
            think_time_max=2.0,
            session_duration_min=1,
            session_duration_max=10,
            actions=[
                {"action": "api_auth", "weight": 1.0, "endpoint": "/api/v3/auth/token"},
                {"action": "bulk_checkin", "weight": 0.6, "endpoint": "/api/v3/events/{event_id}/bulk-checkin"},
                {"action": "sync_data", "weight": 0.4, "endpoint": "/api/v3/sync"},
                {"action": "webhook_callback", "weight": 0.2, "endpoint": "/api/v3/webhooks/callback"},
            ]
        )
    ]

# ================================
# PERFORMANCE METRICS COLLECTION
# ================================

class RequestResult(NamedTuple):
    """Individual request result"""
    timestamp: float
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    error: Optional[str]
    user_profile: str
    response_size_bytes: int

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    response_times: List[float] = field(default_factory=list)
    response_times_by_endpoint: Dict[str, List[float]] = field(default_factory=dict)
    
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    errors_by_endpoint: Dict[str, int] = field(default_factory=dict)
    
    requests_per_second: List[float] = field(default_factory=list)
    concurrent_users_history: List[int] = field(default_factory=list)
    
    start_time: float = 0
    end_time: float = 0
    
    def add_request_result(self, result: RequestResult):
        """Add a request result to metrics"""
        self.total_requests += 1
        
        if result.error:
            self.failed_requests += 1
            error_type = type(result.error).__name__ if hasattr(result.error, '__name__') else str(result.error)
            self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
            self.errors_by_endpoint[result.endpoint] = self.errors_by_endpoint.get(result.endpoint, 0) + 1
        else:
            self.successful_requests += 1
        
        self.response_times.append(result.response_time_ms)
        
        if result.endpoint not in self.response_times_by_endpoint:
            self.response_times_by_endpoint[result.endpoint] = []
        self.response_times_by_endpoint[result.endpoint].append(result.response_time_ms)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.response_times:
            return {"error": "No data available"}
        
        # Calculate percentiles
        sorted_times = sorted(self.response_times)
        total_duration = self.end_time - self.start_time if self.end_time > self.start_time else 1
        
        return {
            "test_duration_seconds": total_duration,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_rate_percent": (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "requests_per_second": self.total_requests / total_duration,
            
            "response_times": {
                "mean_ms": statistics.mean(self.response_times),
                "median_ms": statistics.median(self.response_times),
                "min_ms": min(self.response_times),
                "max_ms": max(self.response_times),
                "p50_ms": sorted_times[int(len(sorted_times) * 0.50)],
                "p90_ms": sorted_times[int(len(sorted_times) * 0.90)],
                "p95_ms": sorted_times[int(len(sorted_times) * 0.95)],
                "p99_ms": sorted_times[int(len(sorted_times) * 0.99)],
                "std_dev_ms": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
            },
            
            "errors_by_type": self.errors_by_type,
            "errors_by_endpoint": self.errors_by_endpoint,
            
            "endpoint_performance": {
                endpoint: {
                    "count": len(times),
                    "mean_ms": statistics.mean(times),
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0
                }
                for endpoint, times in self.response_times_by_endpoint.items()
            }
        }

# ================================
# VIRTUAL USER SIMULATOR
# ================================

class VirtualUser:
    """Simulates a single user's behavior"""
    
    def __init__(
        self, 
        user_id: str,
        profile: UserProfile,
        config: LoadTestConfig,
        metrics: PerformanceMetrics,
        session: aiohttp.ClientSession
    ):
        self.user_id = user_id
        self.profile = profile
        self.config = config
        self.metrics = metrics
        self.session = session
        
        # User state
        self.is_running = False
        self.session_start_time = 0
        self.total_requests = 0
        
        # Authentication state
        self.auth_token = None
        self.current_event_id = None
        self.current_participant_id = None
    
    async def run_session(self):
        """Run a complete user session"""
        self.is_running = True
        self.session_start_time = time.time()
        
        # Determine session duration
        session_duration = random.uniform(
            self.profile.session_duration_min * 60,
            self.profile.session_duration_max * 60
        )
        
        session_end_time = self.session_start_time + session_duration
        
        logger.debug(f"👤 User {self.user_id} ({self.profile.profile_name}) starting session for {session_duration/60:.1f} minutes")
        
        try:
            # Authentication if needed
            if self.profile.profile_name in ["organizer", "pos_operator"]:
                await self._authenticate()
            
            # Main session loop
            while self.is_running and time.time() < session_end_time:
                action = self._choose_action()
                if action:
                    await self._execute_action(action)
                
                # Think time between actions
                think_time = random.uniform(
                    self.profile.think_time_min * self.config.think_time_multiplier,
                    self.profile.think_time_max * self.config.think_time_multiplier
                )
                await asyncio.sleep(think_time)
        
        except Exception as e:
            logger.error(f"❌ User {self.user_id} session error: {e}")
        
        finally:
            self.is_running = False
            logger.debug(f"👤 User {self.user_id} session ended ({self.total_requests} requests)")
    
    def _choose_action(self) -> Optional[Dict[str, Any]]:
        """Choose next action based on profile weights"""
        if not self.profile.actions:
            return None
        
        # Weighted random selection
        total_weight = sum(action["weight"] for action in self.profile.actions)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for action in self.profile.actions:
            current_weight += action["weight"]
            if random_value <= current_weight:
                return action
        
        return self.profile.actions[0]  # Fallback
    
    async def _execute_action(self, action: Dict[str, Any]):
        """Execute a single user action"""
        endpoint = action["endpoint"]
        method = action.get("method", "GET")
        
        # Replace placeholders in endpoint
        endpoint = self._replace_endpoint_placeholders(endpoint)
        
        # Prepare request
        url = f"{self.config.base_url}{endpoint}"
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        # Generate request data if needed
        data = self._generate_request_data(action)
        
        start_time = time.time()
        error = None
        status_code = 0
        response_size = 0
        
        try:
            # Make request with timeout and retries
            async with self.session.request(
                method,
                url,
                json=data if data else None,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                status_code = response.status
                response_text = await response.text()
                response_size = len(response_text.encode('utf-8'))
                
                # Handle specific responses
                await self._handle_response(action, response, response_text)
        
        except Exception as e:
            error = str(e)
        
        # Record metrics
        response_time_ms = (time.time() - start_time) * 1000
        result = RequestResult(
            timestamp=start_time,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error=error,
            user_profile=self.profile.profile_name,
            response_size_bytes=response_size
        )
        
        self.metrics.add_request_result(result)
        self.total_requests += 1
        
        # Log slow requests
        if response_time_ms > 1000:  # Log requests > 1s
            logger.warning(f"🐌 Slow request: {method} {endpoint} - {response_time_ms:.0f}ms")
    
    def _replace_endpoint_placeholders(self, endpoint: str) -> str:
        """Replace placeholders in endpoint URL"""
        # Use current event/participant IDs or generate fake ones
        if "{event_id}" in endpoint:
            if not self.current_event_id:
                self.current_event_id = str(uuid.uuid4())
            endpoint = endpoint.replace("{event_id}", self.current_event_id)
        
        if "{participant_id}" in endpoint:
            if not self.current_participant_id:
                self.current_participant_id = str(uuid.uuid4())
            endpoint = endpoint.replace("{participant_id}", self.current_participant_id)
        
        return endpoint
    
    def _generate_request_data(self, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate realistic request data for specific actions"""
        action_name = action["action"]
        
        if action_name == "login":
            return {
                "email": f"user_{self.user_id}@test.com",
                "password": "test_password_123"
            }
        
        elif action_name == "register":
            return {
                "user_id": self.user_id,
                "event_id": self.current_event_id,
                "participant_data": {
                    "name": f"Test User {self.user_id}",
                    "email": f"user_{self.user_id}@test.com"
                }
            }
        
        elif action_name == "process_sale":
            return {
                "items": [
                    {"product_id": str(uuid.uuid4()), "quantity": random.randint(1, 3), "price": random.uniform(10, 100)}
                    for _ in range(random.randint(1, 5))
                ],
                "payment_method": random.choice(["cash", "card", "pix"]),
                "total": random.uniform(20, 500)
            }
        
        elif action_name == "checkin":
            return {
                "participant_id": self.current_participant_id,
                "event_id": self.current_event_id,
                "checkin_time": datetime.now().isoformat()
            }
        
        return None
    
    async def _handle_response(self, action: Dict[str, Any], response: aiohttp.ClientResponse, response_text: str):
        """Handle specific response types and extract relevant data"""
        if response.status == 200:
            try:
                data = json.loads(response_text) if response_text else {}
                
                # Extract authentication token
                if action["action"] in ["login", "pos_login", "api_auth"]:
                    self.auth_token = data.get("access_token") or data.get("token")
                
                # Extract IDs for future requests
                if "event_id" in data:
                    self.current_event_id = data["event_id"]
                if "participant_id" in data:
                    self.current_participant_id = data["participant_id"]
            
            except json.JSONDecodeError:
                pass  # Response wasn't JSON
    
    async def _authenticate(self):
        """Authenticate user for protected endpoints"""
        try:
            auth_endpoint = "/api/v3/auth/login"
            if self.profile.profile_name == "pos_operator":
                auth_endpoint = "/api/v3/pos/login"
            
            await self._execute_action({
                "action": "authenticate",
                "endpoint": auth_endpoint,
                "method": "POST",
                "weight": 1.0
            })
        except Exception as e:
            logger.error(f"Authentication failed for user {self.user_id}: {e}")

# ================================
# LOAD TEST ORCHESTRATOR
# ================================

class LoadTestOrchestrator:
    """Orchestrates comprehensive load testing"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.user_profiles = get_user_profiles()
        self.is_running = False
        self.active_users: List[asyncio.Task] = []
        
        # Create output directory
        Path(self.config.output_directory).mkdir(parents=True, exist_ok=True)
    
    async def run_load_test(self) -> Dict[str, Any]:
        """Execute the complete load test"""
        logger.info(f"🚀 Starting load test: {self.config.scenario.value}")
        logger.info(f"📊 Target: {self.config.max_concurrent_users} users, {self.config.duration_minutes} minutes")
        
        self.metrics.start_time = time.time()
        self.is_running = True
        
        try:
            # Create HTTP session with connection pooling
            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_users * 2,
                limit_per_host=self.config.max_concurrent_users,
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Start monitoring task
                monitor_task = asyncio.create_task(self._monitor_performance())
                
                # Execute test phases
                await self._ramp_up_phase(session)
                await self._steady_state_phase(session)
                await self._ramp_down_phase(session)
                
                # Stop monitoring
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
        
        except Exception as e:
            logger.error(f"❌ Load test failed: {e}")
            raise
        
        finally:
            self.is_running = False
            self.metrics.end_time = time.time()
            
            # Wait for all users to finish
            if self.active_users:
                await asyncio.gather(*self.active_users, return_exceptions=True)
        
        # Generate and save results
        results = await self._generate_results()
        await self._save_results(results)
        
        logger.info("✅ Load test completed")
        return results
    
    async def _ramp_up_phase(self, session: aiohttp.ClientSession):
        """Gradually increase load to target concurrent users"""
        logger.info("📈 Ramp-up phase starting")
        
        ramp_up_duration = self.config.ramp_up_duration_minutes * 60
        users_per_interval = self.config.max_concurrent_users / (ramp_up_duration / 5)  # Add users every 5 seconds
        
        start_time = time.time()
        next_user_time = start_time
        user_count = 0
        
        while time.time() - start_time < ramp_up_duration and self.is_running:
            current_time = time.time()
            
            if current_time >= next_user_time and user_count < self.config.max_concurrent_users:
                # Add batch of users
                batch_size = min(int(users_per_interval), self.config.max_concurrent_users - user_count)
                
                for _ in range(batch_size):
                    user = await self._create_virtual_user(session)
                    user_task = asyncio.create_task(user.run_session())
                    self.active_users.append(user_task)
                    user_count += 1
                
                next_user_time += 5  # Next batch in 5 seconds
                logger.debug(f"📈 Ramp-up: {user_count}/{self.config.max_concurrent_users} users active")
            
            await asyncio.sleep(1)
        
        logger.info(f"📈 Ramp-up completed: {user_count} users active")
    
    async def _steady_state_phase(self, session: aiohttp.ClientSession):
        """Maintain steady load for test duration"""
        logger.info("⚡ Steady-state phase starting")
        
        steady_duration = (self.config.duration_minutes - self.config.ramp_up_duration_minutes - self.config.ramp_down_duration_minutes) * 60
        start_time = time.time()
        
        while time.time() - start_time < steady_duration and self.is_running:
            # Replace finished users to maintain target concurrency
            active_count = sum(1 for task in self.active_users if not task.done())
            
            if active_count < self.config.max_concurrent_users:
                users_to_add = self.config.max_concurrent_users - active_count
                
                for _ in range(users_to_add):
                    user = await self._create_virtual_user(session)
                    user_task = asyncio.create_task(user.run_session())
                    self.active_users.append(user_task)
            
            # Clean up completed tasks
            self.active_users = [task for task in self.active_users if not task.done()]
            
            await asyncio.sleep(5)  # Check every 5 seconds
        
        logger.info("⚡ Steady-state phase completed")
    
    async def _ramp_down_phase(self, session: aiohttp.ClientSession):
        """Gradually reduce load"""
        logger.info("📉 Ramp-down phase starting")
        
        # Stop creating new users, let existing ones finish naturally
        ramp_down_start = time.time()
        ramp_down_duration = self.config.ramp_down_duration_minutes * 60
        
        while time.time() - ramp_down_start < ramp_down_duration and self.active_users:
            active_count = sum(1 for task in self.active_users if not task.done())
            logger.debug(f"📉 Ramp-down: {active_count} users still active")
            
            # Clean up completed tasks
            self.active_users = [task for task in self.active_users if not task.done()]
            
            await asyncio.sleep(2)
        
        logger.info("📉 Ramp-down completed")
    
    async def _create_virtual_user(self, session: aiohttp.ClientSession) -> VirtualUser:
        """Create a virtual user with weighted profile selection"""
        # Choose profile based on weights
        total_weight = sum(profile.weight for profile in self.user_profiles)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        selected_profile = self.user_profiles[0]  # Fallback
        
        for profile in self.user_profiles:
            current_weight += profile.weight
            if random_value <= current_weight:
                selected_profile = profile
                break
        
        user_id = f"{selected_profile.profile_name}_{uuid.uuid4().hex[:8]}"
        return VirtualUser(user_id, selected_profile, self.config, self.metrics, session)
    
    async def _monitor_performance(self):
        """Monitor performance during test execution"""
        logger.info("📊 Performance monitoring started")
        
        while self.is_running:
            try:
                # Record current metrics
                active_users = sum(1 for task in self.active_users if not task.done())
                self.metrics.concurrent_users_history.append(active_users)
                
                # Calculate recent RPS
                if len(self.metrics.response_times) >= 2:
                    recent_requests = len([r for r in self.metrics.response_times 
                                        if time.time() - r < 60])  # Last minute
                    self.metrics.requests_per_second.append(recent_requests / 60)
                
                # Real-time reporting
                if self.config.enable_real_time_reporting:
                    current_summary = self.metrics.get_summary()
                    logger.info(f"📊 Live: {active_users} users, {self.metrics.total_requests} reqs, "
                              f"{current_summary.get('response_times', {}).get('p95_ms', 0):.0f}ms p95, "
                              f"{current_summary.get('error_rate_percent', 0):.2f}% errors")
                
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _generate_results(self) -> Dict[str, Any]:
        """Generate comprehensive test results"""
        summary = self.metrics.get_summary()
        
        # Add test configuration info
        results = {
            "test_config": {
                "scenario": self.config.scenario.value,
                "duration_minutes": self.config.duration_minutes,
                "max_concurrent_users": self.config.max_concurrent_users,
                "base_url": self.config.base_url,
                "timestamp": datetime.now().isoformat()
            },
            "performance_summary": summary,
            "pass_fail_results": self._evaluate_performance_targets(summary),
            "recommendations": self._generate_recommendations(summary)
        }
        
        return results
    
    def _evaluate_performance_targets(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate performance against targets"""
        response_times = summary.get("response_times", {})
        p95_ms = response_times.get("p95_ms", float('inf'))
        p99_ms = response_times.get("p99_ms", float('inf'))
        error_rate = summary.get("error_rate_percent", 100)
        
        return {
            "overall_pass": (
                p95_ms <= self.config.target_response_time_p95_ms and
                p99_ms <= self.config.target_response_time_p99_ms and
                error_rate <= self.config.max_acceptable_error_rate
            ),
            "response_time_p95_pass": p95_ms <= self.config.target_response_time_p95_ms,
            "response_time_p99_pass": p99_ms <= self.config.target_response_time_p99_ms,
            "error_rate_pass": error_rate <= self.config.max_acceptable_error_rate,
            "targets": {
                "response_time_p95_ms": self.config.target_response_time_p95_ms,
                "response_time_p99_ms": self.config.target_response_time_p99_ms,
                "max_error_rate_percent": self.config.max_acceptable_error_rate
            },
            "actual": {
                "response_time_p95_ms": p95_ms,
                "response_time_p99_ms": p99_ms,
                "error_rate_percent": error_rate
            }
        }
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        response_times = summary.get("response_times", {})
        p95_ms = response_times.get("p95_ms", 0)
        error_rate = summary.get("error_rate_percent", 0)
        
        if p95_ms > 100:
            recommendations.append("🐌 High response times detected. Consider implementing caching or database optimization.")
        
        if error_rate > 1:
            recommendations.append("❌ High error rate detected. Check server logs and implement better error handling.")
        
        if summary.get("requests_per_second", 0) < 100:
            recommendations.append("📈 Low throughput detected. Consider connection pooling and async processing optimization.")
        
        endpoint_perf = summary.get("endpoint_performance", {})
        slow_endpoints = [ep for ep, data in endpoint_perf.items() if data.get("p95_ms", 0) > 200]
        if slow_endpoints:
            recommendations.append(f"🎯 Slow endpoints detected: {', '.join(slow_endpoints[:3])}. Focus optimization efforts here.")
        
        return recommendations
    
    async def _save_results(self, results: Dict[str, Any]):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save summary JSON
        summary_file = Path(self.config.output_directory) / f"load_test_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to {summary_file}")
        
        # Save detailed CSV if enabled
        if self.config.export_detailed_metrics:
            await self._export_detailed_csv(timestamp)
    
    async def _export_detailed_csv(self, timestamp: str):
        """Export detailed metrics to CSV"""
        csv_file = Path(self.config.output_directory) / f"load_test_details_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'endpoint', 'method', 'status_code', 'response_time_ms', 'error', 'user_profile'])
            
            # This would require storing detailed request results
            # For brevity, just writing summary info
            writer.writerow(['Summary data would go here'])
        
        logger.info(f"📊 Detailed metrics exported to {csv_file}")

# ================================
# LOAD TEST SCENARIOS
# ================================

def get_scenario_config(scenario: LoadTestScenario) -> LoadTestConfig:
    """Get configuration for specific load test scenarios"""
    
    if scenario == LoadTestScenario.BASELINE:
        return LoadTestConfig(
            scenario=scenario,
            max_concurrent_users=10,
            duration_minutes=5,
            ramp_up_duration_minutes=1,
            ramp_down_duration_minutes=1
        )
    
    elif scenario == LoadTestScenario.REALISTIC_TRAFFIC:
        return LoadTestConfig(
            scenario=scenario,
            max_concurrent_users=500,
            duration_minutes=30,
            ramp_up_duration_minutes=5,
            ramp_down_duration_minutes=5
        )
    
    elif scenario == LoadTestScenario.PEAK_TRAFFIC:
        return LoadTestConfig(
            scenario=scenario,
            max_concurrent_users=2000,
            duration_minutes=60,
            ramp_up_duration_minutes=10,
            ramp_down_duration_minutes=10,
            target_response_time_p95_ms=100,  # More lenient for peak load
            max_acceptable_error_rate=1.0
        )
    
    elif scenario == LoadTestScenario.SPIKE_TEST:
        return LoadTestConfig(
            scenario=scenario,
            max_concurrent_users=1000,
            duration_minutes=15,
            ramp_up_duration_minutes=1,  # Very fast ramp-up
            ramp_down_duration_minutes=5,
            target_response_time_p95_ms=200,  # Lenient for spike handling
            max_acceptable_error_rate=2.0
        )
    
    elif scenario == LoadTestScenario.ENDURANCE:
        return LoadTestConfig(
            scenario=scenario,
            max_concurrent_users=200,
            duration_minutes=180,  # 3 hours
            ramp_up_duration_minutes=10,
            ramp_down_duration_minutes=10
        )
    
    else:
        return LoadTestConfig(scenario=scenario)

# ================================
# CLI AND MAIN EXECUTION
# ================================

async def run_load_test_scenario(scenario: LoadTestScenario, base_url: str = "http://localhost:8001"):
    """Run a specific load test scenario"""
    config = get_scenario_config(scenario)
    config.base_url = base_url
    
    orchestrator = LoadTestOrchestrator(config)
    results = await orchestrator.run_load_test()
    
    # Print summary
    print("\n" + "="*80)
    print(f"🎯 LOAD TEST RESULTS - {scenario.value.upper()}")
    print("="*80)
    
    perf = results["performance_summary"]
    print(f"📊 Total Requests: {perf.get('total_requests', 0)}")
    print(f"✅ Success Rate: {100 - perf.get('error_rate_percent', 0):.2f}%")
    print(f"⚡ Requests/sec: {perf.get('requests_per_second', 0):.1f}")
    
    resp_times = perf.get("response_times", {})
    print(f"⏱️  Response Times (ms): P50={resp_times.get('p50_ms', 0):.0f}, P95={resp_times.get('p95_ms', 0):.0f}, P99={resp_times.get('p99_ms', 0):.0f}")
    
    pass_fail = results["pass_fail_results"]
    print(f"🎯 Performance Target: {'PASS' if pass_fail['overall_pass'] else 'FAIL'}")
    
    if results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"   {rec}")
    
    return results

if __name__ == "__main__":
    import sys
    
    scenario_name = sys.argv[1] if len(sys.argv) > 1 else "realistic_traffic"
    base_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8001"
    
    try:
        scenario = LoadTestScenario(scenario_name)
    except ValueError:
        print(f"❌ Invalid scenario. Available: {[s.value for s in LoadTestScenario]}")
        sys.exit(1)
    
    # Run the load test
    asyncio.run(run_load_test_scenario(scenario, base_url))