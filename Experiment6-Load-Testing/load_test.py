"""
DevOps Lab 3 - Custom Load Testing Script (without Locust dependency)
Student: Kartik Kumar | Roll: 2301730205 | Email: kartikjangra5366@gmail.com

Performs load testing using Python's threading and urllib.
Run directly: python load_test.py --url http://localhost:8080 --users 50 --duration 60
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import threading
import statistics
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from queue import Queue
from dataclasses import dataclass, field
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STUDENT_NAME = "Kartik Kumar"
ROLL_NUMBER = "2301730205"
EMAIL = "kartikjangra5366@gmail.com"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class RequestResult:
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class LoadTestReport:
    student_name: str
    roll_number: str
    test_start: str
    test_end: str
    duration_seconds: float
    target_url: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    requests_per_second: float
    avg_response_ms: float
    min_response_ms: float
    max_response_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    endpoint_stats: dict
    
    def to_dict(self):
        return {
            "report_title": "Load Test Report - DevOps Lab 3",
            "student": {
                "name": self.student_name,
                "roll_number": self.roll_number,
                "email": EMAIL
            },
            "test_config": {
                "target_url": self.target_url,
                "concurrent_users": self.concurrent_users,
                "duration_seconds": self.duration_seconds,
                "start_time": self.test_start,
                "end_time": self.test_end
            },
            "results": {
                "total_requests": self.total_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "success_rate_percent": round(self.success_rate, 2),
                "requests_per_second": round(self.requests_per_second, 2)
            },
            "response_times_ms": {
                "average": round(self.avg_response_ms, 2),
                "minimum": round(self.min_response_ms, 2),
                "maximum": round(self.max_response_ms, 2),
                "p50": round(self.p50_ms, 2),
                "p95": round(self.p95_ms, 2),
                "p99": round(self.p99_ms, 2)
            },
            "endpoint_breakdown": self.endpoint_stats
        }


# =============================================================================
# Load Test Engine
# =============================================================================

class LoadTestEngine:
    """Core load testing engine"""
    
    ENDPOINTS = [
        ('GET', '/'),
        ('GET', '/health'),
        ('GET', '/api/info'),
        ('GET', '/api/data'),
        ('GET', '/metrics'),
    ]
    
    def __init__(self, base_url: str, concurrent_users: int = 10, 
                 duration: float = 30.0, ramp_up: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.ramp_up = ramp_up
        self.results: List[RequestResult] = []
        self.results_lock = threading.Lock()
        self.stop_event = threading.Event()
        self._running_users = 0
    
    def _make_request(self, method: str, path: str) -> RequestResult:
        """Make a single HTTP request"""
        url = f"{self.base_url}{path}"
        start = time.time()
        
        try:
            req = Request(url, method=method)
            req.add_header('User-Agent', f'LoadTest/1.0 Student/{ROLL_NUMBER}')
            req.add_header('Accept', 'application/json')
            
            with urlopen(req, timeout=10) as response:
                _ = response.read()
                elapsed_ms = (time.time() - start) * 1000
                return RequestResult(
                    endpoint=path,
                    method=method,
                    status_code=response.status,
                    response_time_ms=elapsed_ms,
                    success=True
                )
        
        except HTTPError as e:
            elapsed_ms = (time.time() - start) * 1000
            return RequestResult(
                endpoint=path,
                method=method,
                status_code=e.code,
                response_time_ms=elapsed_ms,
                success=e.code < 500,
                error=str(e)
            )
        
        except (URLError, Exception) as e:
            elapsed_ms = (time.time() - start) * 1000
            return RequestResult(
                endpoint=path,
                method=method,
                status_code=0,
                response_time_ms=elapsed_ms,
                success=False,
                error=str(e)
            )
    
    def _user_worker(self, user_id: int):
        """Worker thread simulating a user"""
        logger.debug(f"User {user_id} started")
        
        while not self.stop_event.is_set():
            # Pick random endpoint
            method, path = random.choice(self.ENDPOINTS)
            
            result = self._make_request(method, path)
            
            with self.results_lock:
                self.results.append(result)
            
            # Think time between requests
            think_time = random.uniform(0.1, 1.0)
            self.stop_event.wait(timeout=think_time)
        
        logger.debug(f"User {user_id} stopped")
    
    def run(self) -> LoadTestReport:
        """Execute load test"""
        test_start = datetime.utcnow().isoformat()
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"LOAD TEST STARTING")
        print(f"Student    : {STUDENT_NAME}")
        print(f"Roll       : {ROLL_NUMBER}")
        print(f"Target     : {self.base_url}")
        print(f"Users      : {self.concurrent_users}")
        print(f"Duration   : {self.duration}s")
        print(f"Ramp-up    : {self.ramp_up}s")
        print(f"{'='*60}\n")
        
        # Start users with ramp-up
        threads = []
        ramp_delay = self.ramp_up / max(self.concurrent_users, 1)
        
        for i in range(self.concurrent_users):
            t = threading.Thread(target=self._user_worker, args=(i,), daemon=True)
            threads.append(t)
            t.start()
            self._running_users += 1
            
            if i % 10 == 0:
                print(f"  Ramping up: {i + 1}/{self.concurrent_users} users active...")
            
            time.sleep(ramp_delay)
        
        print(f"\n  All {self.concurrent_users} users active. Running for {self.duration}s...")
        
        # Progress monitoring
        check_interval = 10
        elapsed = 0
        while elapsed < self.duration:
            time.sleep(min(check_interval, self.duration - elapsed))
            elapsed = time.time() - start_time
            
            with self.results_lock:
                total = len(self.results)
                success = sum(1 for r in self.results if r.success)
            
            rps = total / max(elapsed, 1)
            print(f"  Progress: {elapsed:.0f}s/{self.duration}s | Requests: {total} | RPS: {rps:.1f} | Success: {success}")
        
        # Stop all users
        self.stop_event.set()
        for t in threads:
            t.join(timeout=5)
        
        test_end = datetime.utcnow().isoformat()
        total_duration = time.time() - start_time
        
        # Compile statistics
        return self._compile_report(test_start, test_end, total_duration)
    
    def _compile_report(self, test_start: str, test_end: str, duration: float) -> LoadTestReport:
        """Compile test results into a report"""
        with self.results_lock:
            results = list(self.results)
        
        total = len(results)
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        response_times = [r.response_time_ms for r in results]
        
        if response_times:
            sorted_times = sorted(response_times)
            n = len(sorted_times)
            p50 = sorted_times[n // 2]
            p95 = sorted_times[int(n * 0.95)]
            p99 = sorted_times[int(n * 0.99)]
            avg = statistics.mean(response_times)
            min_rt = min(response_times)
            max_rt = max(response_times)
        else:
            p50 = p95 = p99 = avg = min_rt = max_rt = 0
        
        # Endpoint breakdown
        endpoint_stats = {}
        for result in results:
            ep = result.endpoint
            if ep not in endpoint_stats:
                endpoint_stats[ep] = {"count": 0, "success": 0, "failure": 0, "response_times": []}
            endpoint_stats[ep]["count"] += 1
            endpoint_stats[ep]["response_times"].append(result.response_time_ms)
            if result.success:
                endpoint_stats[ep]["success"] += 1
            else:
                endpoint_stats[ep]["failure"] += 1
        
        # Clean up endpoint stats
        for ep in endpoint_stats:
            times = endpoint_stats[ep].pop("response_times")
            if times:
                endpoint_stats[ep]["avg_ms"] = round(statistics.mean(times), 2)
                endpoint_stats[ep]["p95_ms"] = round(sorted(times)[int(len(times) * 0.95)], 2)
        
        return LoadTestReport(
            student_name=STUDENT_NAME,
            roll_number=ROLL_NUMBER,
            test_start=test_start,
            test_end=test_end,
            duration_seconds=round(duration, 2),
            target_url=self.base_url,
            concurrent_users=self.concurrent_users,
            total_requests=total,
            successful_requests=len(successful),
            failed_requests=len(failed),
            success_rate=(len(successful) / max(total, 1)) * 100,
            requests_per_second=total / max(duration, 1),
            avg_response_ms=avg,
            min_response_ms=min_rt,
            max_response_ms=max_rt,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            endpoint_stats=endpoint_stats
        )


# =============================================================================
# Report Printer
# =============================================================================

def print_report(report: LoadTestReport):
    """Print load test report to console"""
    print(f"\n{'='*60}")
    print(f"LOAD TEST REPORT")
    print(f"{'='*60}")
    print(f"Student         : {report.student_name}")
    print(f"Roll Number     : {report.roll_number}")
    print(f"Target URL      : {report.target_url}")
    print(f"Duration        : {report.duration_seconds}s")
    print(f"Concurrent Users: {report.concurrent_users}")
    print(f"{'='*60}")
    print(f"RESULTS:")
    print(f"  Total Requests : {report.total_requests}")
    print(f"  Successful     : {report.successful_requests}")
    print(f"  Failed         : {report.failed_requests}")
    print(f"  Success Rate   : {report.success_rate:.1f}%")
    print(f"  Req/Second     : {report.requests_per_second:.2f}")
    print(f"{'='*60}")
    print(f"RESPONSE TIMES (ms):")
    print(f"  Average        : {report.avg_response_ms:.1f}")
    print(f"  Minimum        : {report.min_response_ms:.1f}")
    print(f"  Maximum        : {report.max_response_ms:.1f}")
    print(f"  P50 (median)   : {report.p50_ms:.1f}")
    print(f"  P95            : {report.p95_ms:.1f}")
    print(f"  P99            : {report.p99_ms:.1f}")
    print(f"{'='*60}")
    print(f"ENDPOINT BREAKDOWN:")
    for ep, stats in report.endpoint_stats.items():
        print(f"  {ep:<20} Count:{stats['count']:5d} | Avg:{stats.get('avg_ms', 0):.1f}ms | P95:{stats.get('p95_ms', 0):.1f}ms")
    print(f"{'='*60}\n")
    
    # Assessment
    if report.success_rate >= 99:
        grade = "EXCELLENT"
    elif report.success_rate >= 95:
        grade = "GOOD"
    elif report.success_rate >= 90:
        grade = "ACCEPTABLE"
    else:
        grade = "NEEDS IMPROVEMENT"
    
    print(f"ASSESSMENT: {grade}")
    if report.p95_ms < 500:
        print(f"P95 LATENCY: PASS (<500ms)")
    else:
        print(f"P95 LATENCY: REVIEW (>{report.p95_ms:.0f}ms)")
    print()


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=f'Load Testing Tool - DevOps Lab 3 | {STUDENT_NAME} | {ROLL_NUMBER}'
    )
    parser.add_argument('--url', default='http://localhost:8080', help='Target base URL')
    parser.add_argument('--users', type=int, default=20, help='Concurrent users')
    parser.add_argument('--duration', type=float, default=30, help='Test duration (seconds)')
    parser.add_argument('--ramp-up', type=float, default=5, help='Ramp-up time (seconds)')
    parser.add_argument('--output', default='load_test_report.json', help='Output report file')
    parser.add_argument('--demo', action='store_true', help='Run demo without actual HTTP calls')
    
    args = parser.parse_args()
    
    if args.demo:
        # Demo mode: simulate results
        print(f"\n{'='*60}")
        print(f"DEMO MODE - Simulated Load Test")
        print(f"Student : {STUDENT_NAME}")
        print(f"Roll    : {ROLL_NUMBER}")
        print(f"{'='*60}")
        
        # Create simulated report
        report = LoadTestReport(
            student_name=STUDENT_NAME,
            roll_number=ROLL_NUMBER,
            test_start=datetime.utcnow().isoformat(),
            test_end=datetime.utcnow().isoformat(),
            duration_seconds=30.0,
            target_url=args.url,
            concurrent_users=args.users,
            total_requests=1850,
            successful_requests=1832,
            failed_requests=18,
            success_rate=99.03,
            requests_per_second=61.67,
            avg_response_ms=142.5,
            min_response_ms=12.3,
            max_response_ms=2340.1,
            p50_ms=98.7,
            p95_ms=387.2,
            p99_ms=890.4,
            endpoint_stats={
                "/": {"count": 320, "success": 319, "failure": 1, "avg_ms": 45.2, "p95_ms": 125.0},
                "/health": {"count": 480, "success": 480, "failure": 0, "avg_ms": 23.1, "p95_ms": 67.5},
                "/api/data": {"count": 350, "success": 342, "failure": 8, "avg_ms": 234.5, "p95_ms": 567.3},
                "/api/info": {"count": 400, "success": 398, "failure": 2, "avg_ms": 89.3, "p95_ms": 234.1},
                "/metrics": {"count": 300, "success": 293, "failure": 7, "avg_ms": 156.7, "p95_ms": 445.2}
            }
        )
    else:
        # Run actual load test
        engine = LoadTestEngine(
            base_url=args.url,
            concurrent_users=args.users,
            duration=args.duration,
            ramp_up=args.ramp_up
        )
        report = engine.run()
    
    # Print and save report
    print_report(report)
    
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    
    print(f"Report saved to: {args.output}")


if __name__ == '__main__':
    main()

