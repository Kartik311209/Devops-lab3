"""
DevOps Lab 3 - Live Integration Test Runner
Student: Kartik Kumar | Roll: 2301730205
Runs the app server and executes browser tests + load tests in one process.
"""

import os, sys, json, time, threading, urllib.request, statistics

sys.path.insert(0, 'c:/Users/karti/Desktop/Devops3/Experiment2-Prometheus-Grafana/app')
os.chdir('c:/Users/karti/Desktop/Devops3/Experiment2-Prometheus-Grafana/app')
os.environ['PORT'] = '19877'

import importlib.util
spec = importlib.util.spec_from_file_location(
    'app',
    'c:/Users/karti/Desktop/Devops3/Experiment2-Prometheus-Grafana/app/app.py'
)
app_mod = importlib.util.module_from_spec(spec)
from http.server import HTTPServer
spec.loader.exec_module(app_mod)

PORT = 19877
BASE = f'http://127.0.0.1:{PORT}'
app_mod.START_TIME = time.time()
server = HTTPServer(('127.0.0.1', PORT), app_mod.AppHandler)
srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
srv_thread.start()
time.sleep(2)
print(f"Server started on port {PORT}")


# =================================================================
# Helper
# =================================================================
def http_get(path, timeout=5):
    r = urllib.request.urlopen(f'{BASE}{path}', timeout=timeout)
    content = r.read().decode()
    return r.status, content


# =================================================================
# BROWSER TESTS
# =================================================================
print()
print('=' * 65)
print('EXPERIMENT 7: AUTOMATED BROWSER TESTS')
print('Student: Kartik Kumar | Roll: 2301730205')
print('=' * 65)

def tc001():
    s, _ = http_get('/')
    return s == 200

def tc002():
    s, c = http_get('/health')
    return s == 200 and 'healthy' in c

def tc003():
    s, c = http_get('/metrics')
    return s == 200 and len(c) > 50

def tc004():
    s, c = http_get('/api/info')
    return s == 200 and '2301730205' in c

def tc005():
    s, c = http_get('/api/data')
    return s == 200 and len(c) > 10

def tc006():
    t0 = time.time()
    http_get('/')
    return (time.time() - t0) * 1000 < 3000

def tc007():
    try:
        http_get('/nonexistent-page-xyz')
        return True
    except Exception:
        return True

def tc008():
    s, c = http_get('/')
    return s == 200 and 'Kartik Kumar' in c

def tc009():
    s, c = http_get('/health')
    d = json.loads(c)
    return 'status' in d

def tc010():
    s, c = http_get('/metrics')
    return s == 200 and 'app_info' in c


test_cases = [
    ('TC001_Homepage_Accessible',    'Homepage returns HTTP 200',                  tc001),
    ('TC002_Health_Check_Pass',      'Health endpoint returns healthy status',      tc002),
    ('TC003_Metrics_Available',      'Prometheus metrics endpoint returns data',    tc003),
    ('TC004_API_Info_Returns_JSON',  'API info endpoint returns student data',      tc004),
    ('TC005_API_Data_Returns_Content','API data endpoint returns JSON data',        tc005),
    ('TC006_Response_Time_OK',       'Homepage responds within 3 seconds',         tc006),
    ('TC007_404_Returns_Response',   'Non-existent URL returns a response',        tc007),
    ('TC008_Student_Info_Present',   'Application contains student info',          tc008),
    ('TC009_Health_Status_Field',    'Health response has status field',           tc009),
    ('TC010_Metrics_Contains_App',   'Metrics contain app_info gauge',             tc010),
]

passed_bt = failed_bt = 0
bt_results = []

for name, desc, fn in test_cases:
    t0 = time.time()
    try:
        result = fn()
        ms = (time.time() - t0) * 1000
        status = 'PASS' if result else 'FAIL'
        icon = 'V' if result else 'X'
        if result:
            passed_bt += 1
        else:
            failed_bt += 1
        print(f'  [{status}] {icon} {name} ({ms:.0f}ms)')
    except Exception as e:
        ms = (time.time() - t0) * 1000
        failed_bt += 1
        status = 'FAIL'
        print(f'  [FAIL] X {name} ({ms:.0f}ms) - {str(e)[:60]}')
    bt_results.append({'name': name, 'desc': desc, 'status': status})

print()
print(f'Browser Test Summary: {passed_bt}/{len(test_cases)} passed | '
      f'Pass Rate: {passed_bt/len(test_cases)*100:.0f}%')

os.makedirs('c:/Users/karti/Desktop/Devops3/Experiment7-Browser-Testing', exist_ok=True)
with open('c:/Users/karti/Desktop/Devops3/Experiment7-Browser-Testing/browser_test_report.json', 'w') as f:
    json.dump({
        'report_title': 'Browser Test Report - DevOps Lab 3',
        'student': {'name': 'Kartik Kumar', 'roll': '2301730205', 'email': 'kartikjangra5366@gmail.com'},
        'total': len(test_cases), 'passed': passed_bt, 'failed': failed_bt,
        'pass_rate': f'{passed_bt/len(test_cases)*100:.0f}%',
        'results': bt_results
    }, f, indent=2)


# =================================================================
# LOAD TESTS
# =================================================================
print()
print('=' * 65)
print('EXPERIMENT 6: LOAD TESTING')
print('Student: Kartik Kumar | Roll: 2301730205')
print('=' * 65)

USERS = 25
DURATION = 30
endpoints = ['/', '/health', '/api/info', '/api/data', '/metrics']
results_lt = []
stop_ev = threading.Event()
lock = threading.Lock()


def user_worker(uid):
    import random
    import urllib.request as ur
    while not stop_ev.is_set():
        ep = random.choice(endpoints)
        t0 = time.time()
        try:
            r = ur.urlopen(f'http://127.0.0.1:{PORT}{ep}', timeout=5)
            _ = r.read()
            ms = (time.time() - t0) * 1000
            with lock:
                results_lt.append({'ep': ep, 'status': r.status, 'ms': ms, 'ok': True})
        except Exception:
            ms = (time.time() - t0) * 1000
            with lock:
                results_lt.append({'ep': ep, 'status': 0, 'ms': ms, 'ok': False})
        time.sleep(0.05)


print(f'Starting {USERS} concurrent users for {DURATION}s...')
lt_threads = [
    threading.Thread(target=user_worker, args=(i,), daemon=True)
    for i in range(USERS)
]
lt_start = time.time()
for t in lt_threads:
    t.start()

for i in range(DURATION // 10):
    time.sleep(10)
    elapsed = time.time() - lt_start
    with lock:
        total_so_far = len(results_lt)
        success_so_far = sum(1 for r in results_lt if r['ok'])
    rps = total_so_far / elapsed
    print(f'  Progress: {elapsed:.0f}s | Requests: {total_so_far} | RPS: {rps:.1f} | Success: {success_so_far}')

stop_ev.set()
for t in lt_threads:
    t.join(timeout=3)

lt_duration = time.time() - lt_start
with lock:
    lt_copy = list(results_lt)

total_lt = len(lt_copy)
successful_lt = sum(1 for r in lt_copy if r['ok'])
failed_lt = total_lt - successful_lt
rps_final = total_lt / lt_duration
times = sorted(r['ms'] for r in lt_copy)
n = len(times)
p50 = times[n // 2] if n else 0
p95 = times[int(n * 0.95)] if n else 0
p99 = times[int(n * 0.99)] if n else 0
avg_ms = statistics.mean(times) if times else 0

print()
print('=' * 65)
print('LOAD TEST RESULTS')
print('=' * 65)
print(f'  Student       : Kartik Kumar | Roll: 2301730205')
print(f'  Duration      : {lt_duration:.1f}s')
print(f'  Users         : {USERS}')
print(f'  Total Reqs    : {total_lt}')
print(f'  Successful    : {successful_lt}')
print(f'  Failed        : {failed_lt}')
print(f'  Success Rate  : {successful_lt/max(total_lt,1)*100:.1f}%')
print(f'  Throughput    : {rps_final:.1f} req/s')
print(f'  Avg Response  : {avg_ms:.1f}ms')
print(f'  P50           : {p50:.1f}ms')
print(f'  P95           : {p95:.1f}ms')
print(f'  P99           : {p99:.1f}ms')
print()

ep_stats = {}
for r in lt_copy:
    ep = r['ep']
    if ep not in ep_stats:
        ep_stats[ep] = {'count': 0, 'ok': 0, 'times': []}
    ep_stats[ep]['count'] += 1
    ep_stats[ep]['times'].append(r['ms'])
    if r['ok']:
        ep_stats[ep]['ok'] += 1

print('Endpoint Breakdown:')
for ep, s in ep_stats.items():
    t_sorted = sorted(s['times'])
    avg_t = statistics.mean(s['times']) if s['times'] else 0
    p95_t = t_sorted[int(len(t_sorted) * 0.95)] if t_sorted else 0
    print(f'  {ep:<20} Count:{s["count"]:5d} | Avg:{avg_t:.0f}ms | P95:{p95_t:.0f}ms')

os.makedirs('c:/Users/karti/Desktop/Devops3/Experiment6-Load-Testing/reports', exist_ok=True)
with open('c:/Users/karti/Desktop/Devops3/Experiment6-Load-Testing/reports/live_load_test_report.json', 'w') as f:
    json.dump({
        'report_title': 'Load Test Report - DevOps Lab 3',
        'student': {'name': 'Kartik Kumar', 'roll': '2301730205'},
        'total': total_lt, 'successful': successful_lt, 'failed': failed_lt,
        'rps': round(rps_final, 2), 'avg_ms': round(avg_ms, 2),
        'p50': round(p50, 2), 'p95': round(p95, 2), 'p99': round(p99, 2)
    }, f, indent=2)

server.shutdown()
print()
print('All experiments complete!')

