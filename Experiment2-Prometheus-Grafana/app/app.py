"""
DevOps Lab 3 - Sample Application with Prometheus Metrics
Student: Kartik Kumar | Roll: 2301730205 | Email: kartikjangra5366@gmail.com
"""

import os
import time
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# Metrics Store
# =============================================================================
class MetricsStore:
    def __init__(self):
        self.request_count = {}
        self.error_count = {}
        self.response_times = []
        self.lock = threading.Lock()
        
    def record_request(self, path, method, status, duration):
        with self.lock:
            key = f"{method}_{path}_{status}"
            self.request_count[key] = self.request_count.get(key, 0) + 1
            if status >= 400:
                self.error_count[key] = self.error_count.get(key, 0) + 1
            self.response_times.append(duration)
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
    
    def get_prometheus_metrics(self):
        with self.lock:
            lines = []
            lines.append("# HELP http_requests_total Total number of HTTP requests")
            lines.append("# TYPE http_requests_total counter")
            for key, count in self.request_count.items():
                parts = key.split('_', 2)
                if len(parts) == 3:
                    method, path, status = parts
                    lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status}",student="kartik-kumar",roll="2301730205"}} {count}')
            
            lines.append("# HELP http_errors_total Total number of HTTP errors")
            lines.append("# TYPE http_errors_total counter")
            for key, count in self.error_count.items():
                parts = key.split('_', 2)
                if len(parts) == 3:
                    method, path, status = parts
                    lines.append(f'http_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}')
            
            lines.append("# HELP http_response_time_seconds HTTP response time in seconds")
            lines.append("# TYPE http_response_time_seconds summary")
            if self.response_times:
                sorted_times = sorted(self.response_times)
                n = len(sorted_times)
                p50 = sorted_times[int(n * 0.5)]
                p95 = sorted_times[int(n * 0.95)]
                p99 = sorted_times[int(n * 0.99)]
                total = sum(sorted_times)
                lines.append(f'http_response_time_seconds{{quantile="0.5",student="kartik-kumar"}} {p50:.4f}')
                lines.append(f'http_response_time_seconds{{quantile="0.95",student="kartik-kumar"}} {p95:.4f}')
                lines.append(f'http_response_time_seconds{{quantile="0.99",student="kartik-kumar"}} {p99:.4f}')
                lines.append(f'http_response_time_seconds_sum{{student="kartik-kumar"}} {total:.4f}')
                lines.append(f'http_response_time_seconds_count{{student="kartik-kumar"}} {n}')
            
            # Custom app metrics
            lines.append("# HELP app_info Application information")
            lines.append("# TYPE app_info gauge")
            lines.append('app_info{name="devops-lab3-app",student="Kartik Kumar",roll="2301730205",version="1.0.0"} 1')
            
            # Simulated business metrics
            lines.append("# HELP active_users_total Simulated active users")
            lines.append("# TYPE active_users_total gauge")
            lines.append(f'active_users_total{{student="kartik-kumar"}} {random.randint(50, 200)}')
            
            lines.append("# HELP orders_processed_total Simulated orders processed")
            lines.append("# TYPE orders_processed_total counter")
            lines.append(f'orders_processed_total{{student="kartik-kumar"}} {random.randint(1000, 5000)}')
            
            return "\n".join(lines) + "\n"

metrics = MetricsStore()

# =============================================================================
# HTTP Request Handler
# =============================================================================
class AppHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        start_time = time.time()
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            if path == '/':
                self._handle_root()
                status = 200
            elif path == '/health':
                self._handle_health()
                status = 200
            elif path == '/metrics':
                self._handle_metrics()
                status = 200
            elif path == '/api/info':
                self._handle_info()
                status = 200
            elif path == '/api/data':
                self._handle_data()
                status = 200
            elif path == '/api/slow':
                time.sleep(random.uniform(0.1, 2.0))
                self._handle_data()
                status = 200
            elif path == '/api/error':
                self._handle_error()
                status = 500
            else:
                self._handle_404()
                status = 404
        except Exception as e:
            logger.error(f"Error handling {path}: {e}")
            self._handle_500()
            status = 500
        
        duration = time.time() - start_time
        metrics.record_request(path, 'GET', status, duration)
    
    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('X-Student', 'Kartik Kumar')
        self.send_header('X-Roll', '2301730205')
        self.end_headers()
        self.wfile.write(body)
    
    def _handle_root(self):
        self._send_json({
            "app": "DevOps Lab 3 Application",
            "student": "Kartik Kumar",
            "roll_number": "2301730205",
            "email": "kartikjangra5366@gmail.com",
            "version": "1.0.0",
            "endpoints": ["/health", "/metrics", "/api/info", "/api/data", "/api/slow", "/api/error"],
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
    
    def _handle_health(self):
        self._send_json({
            "status": "healthy",
            "app": "devops-lab3-app",
            "student": "Kartik Kumar",
            "roll_number": "2301730205",
            "uptime_seconds": int(time.time() - START_TIME),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })
    
    def _handle_metrics(self):
        body = metrics.get_prometheus_metrics().encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def _handle_info(self):
        self._send_json({
            "app_name": "devops-lab3",
            "student": {
                "name": "Kartik Kumar",
                "roll": "2301730205",
                "email": "kartikjangra5366@gmail.com"
            },
            "environment": os.environ.get('ENVIRONMENT', 'development'),
            "port": int(os.environ.get('PORT', 8080)),
            "metrics_url": "/metrics",
            "health_url": "/health"
        })
    
    def _handle_data(self):
        self._send_json({
            "data": [{"id": i, "value": random.randint(1, 100)} for i in range(10)],
            "total": 10,
            "generated_by": "Kartik Kumar",
            "roll": "2301730205"
        })
    
    def _handle_error(self):
        self._send_json({"error": "Simulated internal server error", "code": 500}, 500)
    
    def _handle_404(self):
        self._send_json({"error": "Not found", "path": self.path}, 404)
    
    def _handle_500(self):
        self._send_json({"error": "Internal server error"}, 500)

# =============================================================================
# Main
# =============================================================================
START_TIME = time.time()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'
    
    logger.info("=" * 60)
    logger.info("DevOps Lab 3 - Sample Application")
    logger.info(f"Student: Kartik Kumar | Roll: 2301730205")
    logger.info(f"Starting on http://{host}:{port}")
    logger.info("=" * 60)
    
    server = HTTPServer((host, port), AppHandler)
    
    # Simulate background traffic for metrics
    def generate_traffic():
        import urllib.request
        endpoints = ['/', '/health', '/api/info', '/api/data']
        while True:
            try:
                ep = random.choice(endpoints)
                urllib.request.urlopen(f'http://localhost:{port}{ep}', timeout=2)
            except:
                pass
            time.sleep(random.uniform(1, 5))
    
    traffic_thread = threading.Thread(target=generate_traffic, daemon=True)
    traffic_thread.start()
    
    try:
        logger.info(f"Server running at http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        server.shutdown()

