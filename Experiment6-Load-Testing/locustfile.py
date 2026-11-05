# =============================================================================
# Locust Load Testing Configuration
# DevOps Lab 3 | Student: Kartik Kumar | Roll: 2301730205
# =============================================================================
#
# Run with: locust -f locustfile.py --host=http://localhost:8080
# Or headless: locust -f locustfile.py --host=http://localhost:8080 --headless -u 100 -r 10 --run-time 60s

from locust import HttpUser, TaskSet, task, between, events
import random
import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

STUDENT_NAME = "Kartik Kumar"
ROLL_NUMBER = "2301730205"

# =============================================================================
# Task Sets
# =============================================================================

class BrowsingBehavior(TaskSet):
    """Simulates a user browsing the application"""
    
    @task(5)
    def view_homepage(self):
        """Visit the homepage"""
        with self.client.get("/", catch_response=True, name="Homepage") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def check_health(self):
        """Check health endpoint"""
        with self.client.get("/health", catch_response=True, name="Health Check") as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy":
                        response.success()
                    else:
                        response.failure("Health check returned unhealthy")
                except:
                    response.failure("Invalid JSON response")
    
    @task(4)
    def view_api_info(self):
        """Get API info"""
        self.client.get("/api/info", name="API Info")
    
    @task(2)
    def get_data(self):
        """Fetch application data"""
        self.client.get("/api/data", name="Get Data")
    
    @task(1)
    def slow_endpoint(self):
        """Test slow endpoint (simulates DB query)"""
        with self.client.get("/api/slow", catch_response=True, name="Slow Endpoint") as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Response too slow (>5s)")
            else:
                response.success()
    
    @task(1)
    def metrics_endpoint(self):
        """Check metrics endpoint"""
        self.client.get("/metrics", name="Metrics Endpoint")


class APIBehavior(TaskSet):
    """Simulates an API consumer"""
    
    @task(5)
    def get_data(self):
        """API data request"""
        headers = {
            "Accept": "application/json",
            "X-Student": STUDENT_NAME,
            "X-Roll": ROLL_NUMBER
        }
        self.client.get("/api/data", headers=headers, name="API: Get Data")
    
    @task(3)
    def get_info(self):
        """API info request"""
        self.client.get("/api/info", name="API: Get Info")
    
    @task(2)
    def health_check(self):
        """API health check"""
        self.client.get("/health", name="API: Health")
    
    @task(1)
    def homepage(self):
        """API root"""
        self.client.get("/", name="API: Root")


# =============================================================================
# User Classes
# =============================================================================

class BrowserUser(HttpUser):
    """
    Simulates browser users - moderate think time
    """
    tasks = [BrowsingBehavior]
    wait_time = between(1, 5)
    weight = 3
    
    def on_start(self):
        """Called when user starts"""
        self.user_id = f"browser_user_{random.randint(1000, 9999)}"
        logger.info(f"Browser user started: {self.user_id}")
    
    def on_stop(self):
        """Called when user stops"""
        logger.info(f"Browser user stopped: {self.user_id}")


class APIUser(HttpUser):
    """
    Simulates API consumers - faster requests
    """
    tasks = [APIBehavior]
    wait_time = between(0.1, 1)
    weight = 2
    
    def on_start(self):
        self.user_id = f"api_user_{random.randint(1000, 9999)}"


class HeavyUser(HttpUser):
    """
    Simulates heavy/power users
    """
    tasks = {BrowsingBehavior: 2, APIBehavior: 1}
    wait_time = between(0.5, 2)
    weight = 1
    
    @task(2)
    def trigger_slow_path(self):
        """Heavy users hit slow endpoints more"""
        self.client.get("/api/slow", name="Heavy: Slow Path")


# =============================================================================
# Event Hooks & Custom Reporting
# =============================================================================

test_start_time = None
request_stats = {
    "total": 0,
    "success": 0,
    "failure": 0,
    "response_times": []
}

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global test_start_time
    test_start_time = time.time()
    print("\n" + "=" * 60)
    print("LOAD TEST STARTED")
    print(f"Student : {STUDENT_NAME}")
    print(f"Roll    : {ROLL_NUMBER}")
    print(f"Target  : {environment.host}")
    print(f"Time    : {datetime.utcnow().isoformat()}")
    print("=" * 60 + "\n")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, 
               response, context, exception, start_time, url, **kwargs):
    request_stats["total"] += 1
    request_stats["response_times"].append(response_time)
    
    if exception:
        request_stats["failure"] += 1
    else:
        request_stats["success"] += 1

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    duration = time.time() - test_start_time if test_start_time else 0
    
    times = request_stats["response_times"]
    if times:
        sorted_times = sorted(times)
        n = len(sorted_times)
        p50 = sorted_times[n // 2]
        p95 = sorted_times[int(n * 0.95)]
        p99 = sorted_times[int(n * 0.99)]
        avg = sum(times) / n
    else:
        p50 = p95 = p99 = avg = 0
    
    print("\n" + "=" * 60)
    print("LOAD TEST COMPLETED")
    print(f"Student         : {STUDENT_NAME}")
    print(f"Roll            : {ROLL_NUMBER}")
    print(f"Duration        : {duration:.1f}s")
    print(f"Total Requests  : {request_stats['total']}")
    print(f"Successful      : {request_stats['success']}")
    print(f"Failed          : {request_stats['failure']}")
    success_rate = (request_stats['success'] / max(request_stats['total'], 1)) * 100
    print(f"Success Rate    : {success_rate:.1f}%")
    print(f"Avg Response    : {avg:.1f}ms")
    print(f"P50 Response    : {p50:.1f}ms")
    print(f"P95 Response    : {p95:.1f}ms")
    print(f"P99 Response    : {p99:.1f}ms")
    print("=" * 60 + "\n")

