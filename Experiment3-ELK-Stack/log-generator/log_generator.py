"""
DevOps Lab 3 - Log Generator Application
Student: Kartik Kumar | Roll: 2301730205 | Email: kartikjangra5366@gmail.com

Generates realistic application logs in JSON format for ELK stack ingestion.
"""

import os
import json
import time
import random
import logging
import threading
from datetime import datetime, timezone

# =============================================================================
# Configuration
# =============================================================================
STUDENT_NAME = os.environ.get('STUDENT_NAME', 'Kartik Kumar')
ROLL_NUMBER = os.environ.get('ROLL_NUMBER', '2301730205')
LOG_DIR = os.environ.get('LOG_DIR', '/app/logs')
LOG_INTERVAL = float(os.environ.get('LOG_INTERVAL', '0.5'))

os.makedirs(LOG_DIR, exist_ok=True)

# =============================================================================
# Log Templates
# =============================================================================
ENDPOINTS = ['/api/users', '/api/products', '/api/orders', '/api/payments', 
             '/api/auth/login', '/api/auth/logout', '/health', '/metrics']
METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
STATUS_CODES = [200, 200, 200, 200, 201, 201, 204, 400, 401, 403, 404, 500, 502]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'curl/7.84.0',
    'PostmanRuntime/7.32.3',
    'python-requests/2.31.0'
]
IP_POOL = [f"10.0.{random.randint(1,10)}.{random.randint(1,254)}" for _ in range(20)]
LOG_LEVELS = ['DEBUG', 'INFO', 'INFO', 'INFO', 'WARNING', 'ERROR']
SERVICES = ['auth-service', 'user-service', 'product-service', 'order-service', 'payment-service']

MESSAGES = {
    'INFO': [
        'Request processed successfully',
        'Database query executed',
        'Cache hit for key: {key}',
        'User authenticated: user_{id}',
        'Order {id} created successfully',
        'Payment processed for order_{id}',
        'Health check passed',
        'Service started successfully',
        'Configuration loaded',
    ],
    'WARNING': [
        'High memory usage detected: {value}%',
        'Slow database query: {value}ms',
        'Cache miss for key: {key}',
        'Rate limit approaching for IP: {ip}',
        'Retry attempt {value} for external service',
        'Session about to expire for user_{id}',
    ],
    'ERROR': [
        'Database connection failed: timeout after {value}ms',
        'Authentication failed for user_{id}',
        'External API returned 503 for endpoint: {endpoint}',
        'Failed to process payment for order_{id}',
        'Unhandled exception in {service}',
        'Disk space critically low: {value}% remaining',
    ],
    'DEBUG': [
        'Function {endpoint} called with params: id={id}',
        'SQL query: SELECT * FROM users WHERE id={id}',
        'Cache lookup for key: session_{id}',
        'Response serialized in {value}ms',
    ]
}

# =============================================================================
# Log Generators
# =============================================================================
def generate_access_log():
    """Generate HTTP access log entry"""
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUS_CODES)
    duration = round(random.uniform(0.001, 2.5), 4)
    size = random.randint(100, 10000)
    
    return {
        "type": "access_log",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": endpoint,
        "status": status,
        "duration_ms": round(duration * 1000, 2),
        "response_size_bytes": size,
        "remote_addr": random.choice(IP_POOL),
        "user_agent": random.choice(USER_AGENTS),
        "student_name": STUDENT_NAME,
        "roll_number": ROLL_NUMBER,
        "project": "devops-lab3"
    }

def generate_app_log():
    """Generate application log entry"""
    level = random.choice(LOG_LEVELS)
    service = random.choice(SERVICES)
    
    template_vars = {
        'key': f'session_{random.randint(1000, 9999)}',
        'id': random.randint(1, 1000),
        'value': random.randint(70, 99),
        'ip': random.choice(IP_POOL),
        'endpoint': random.choice(ENDPOINTS),
        'service': service,
    }
    
    messages = MESSAGES.get(level, MESSAGES['INFO'])
    message = random.choice(messages).format(**template_vars)
    
    return {
        "type": "app_log",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": service,
        "message": message,
        "thread_id": f"thread-{random.randint(1, 20)}",
        "request_id": f"req-{random.randint(100000, 999999)}",
        "student_name": STUDENT_NAME,
        "roll_number": ROLL_NUMBER,
        "environment": "development",
        "version": "1.0.0"
    }

def generate_metric_log():
    """Generate system metric log entry"""
    return {
        "type": "metric",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "cpu_usage_percent": round(random.uniform(20, 85), 2),
            "memory_usage_percent": round(random.uniform(40, 80), 2),
            "disk_usage_percent": round(random.uniform(30, 60), 2),
            "active_connections": random.randint(50, 500),
            "requests_per_second": round(random.uniform(10, 200), 2),
            "cache_hit_rate": round(random.uniform(0.70, 0.98), 3),
            "db_query_time_ms": round(random.uniform(1, 100), 2),
            "queue_depth": random.randint(0, 100)
        },
        "host": f"server-{random.randint(1, 3)}",
        "student_name": STUDENT_NAME,
        "roll_number": ROLL_NUMBER
    }

# =============================================================================
# Log Writers
# =============================================================================
def write_logs_to_file():
    """Write logs to files for Filebeat to pick up"""
    access_log_file = os.path.join(LOG_DIR, 'access.log')
    app_log_file = os.path.join(LOG_DIR, 'application.log')
    metrics_log_file = os.path.join(LOG_DIR, 'metrics.log')
    
    counter = 0
    print(f"[LOG-GENERATOR] Starting log generation")
    print(f"[LOG-GENERATOR] Student: {STUDENT_NAME} | Roll: {ROLL_NUMBER}")
    print(f"[LOG-GENERATOR] Log directory: {LOG_DIR}")
    
    while True:
        try:
            with open(access_log_file, 'a') as af, \
                 open(app_log_file, 'a') as appf, \
                 open(metrics_log_file, 'a') as mf:
                
                # Write access log
                access_entry = generate_access_log()
                af.write(json.dumps(access_entry) + '\n')
                
                # Write app logs (multiple per cycle)
                for _ in range(random.randint(1, 5)):
                    app_entry = generate_app_log()
                    appf.write(json.dumps(app_entry) + '\n')
                
                # Write metrics every 10 iterations
                if counter % 10 == 0:
                    metric_entry = generate_metric_log()
                    mf.write(json.dumps(metric_entry) + '\n')
                    
                counter += 1
                
                if counter % 50 == 0:
                    print(f"[LOG-GENERATOR] Generated {counter} log batches | {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(LOG_INTERVAL)
            
        except Exception as e:
            print(f"[LOG-GENERATOR] Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    print("=" * 60)
    print("DevOps Lab 3 - Log Generator")
    print(f"Student: {STUDENT_NAME}")
    print(f"Roll: {ROLL_NUMBER}")
    print("=" * 60)
    
    write_logs_to_file()

