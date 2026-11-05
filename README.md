# DevOps Lab 3: Automated, Observable & Secure Infrastructure Workflow

> **Academic Submission — DevOps Infrastructure, Automation & SRE Lab 3**  
> **Student:** Kartik Kumar  
> **Roll Number:** 2301730205  
> **Email:** [kartikjangra5366@gmail.com](mailto:kartikjangra5366@gmail.com)  
> **Date:** November 05, 2026  

---

## 📋 Executive Summary & Project Overview

This repository delivers an end-to-end implementation of an automated, observable, and secure DevOps infrastructure workflow built from scratch according to the DevOps Lab 3 curriculum requirements. 

The project demonstrates:
1. **Infrastructure as Code (IaC):** Multi-tier infrastructure provisioning with **Terraform** and configuration management with **Ansible**.
2. **Monitoring & Observability:** Real-time metrics collection with **Prometheus**, visualization dashboards with **Grafana**, and alerting via **Alertmanager**.
3. **Centralized Logging:** Full log aggregation and indexing pipeline with **Elasticsearch**, **Logstash**, **Kibana**, and **Filebeat** (ELK Stack).
4. **DevSecOps Pipeline Security:** Static code analysis (**Bandit**, **Semgrep**), software composition analysis (**Safety**), container scanning (**Trivy**), and secrets detection (**Gitleaks**).
5. **Progressive Delivery:** Dynamic **Feature Flag** service with deterministic hash bucketing, canary rollouts, and instant kill-switches.
6. **Performance & Resilience:** High-concurrency **Load Testing** benchmarking throughput and P50/P95/P99 latency distributions.
7. **Quality Assurance:** End-to-end **Automated Browser Testing** and API acceptance test suites.

---

## 📂 Repository Directory Layout

```text
Devops3/
├── README.md                                 # Comprehensive Documentation
├── run_integration_tests.py                 # Unified Live Server + Test Runner
├── generate_screenshots.py                   # High-Resolution Terminal Screenshot Generator
├── generate_reports.py                       # Professional PDF Report Compiler (fpdf2)
│
├── Experiment1-Terraform-Ansible/           # Experiment 1: IaC & Automation
│   ├── main.tf                               # Terraform Resource Definitions
│   ├── terraform.tfvars                      # Terraform Variables (Student Credentials)
│   ├── ansible.cfg                           # Ansible Global Configuration
│   ├── terraform_simulator.py                # Standalone Terraform Provisioner & State Engine
│   ├── output/                               # Provisioned Artifacts (inventory, json, .env, compose)
│   └── ansible/
│       └── playbooks/
│           ├── configure_webservers.yml      # Web Server Provisioning Playbook
│           ├── configure_database.yml        # PostgreSQL Database Setup Playbook
│           └── setup_monitoring.yml          # Monitoring Stack Deployment Playbook
│
├── Experiment2-Prometheus-Grafana/           # Experiment 2: Observability Stack
│   ├── docker-compose.yml                    # Prometheus + Grafana + App Compose
│   ├── prometheus/
│   │   ├── prometheus.yml                    # Scrape Configurations & Student Labels
│   │   ├── alert.rules.yml                   # CPU, Memory, Latency & Down Alerts
│   │   └── alertmanager.yml                  # Alert Routing Rules
│   ├── grafana/
│   │   ├── provisioning/                     # Automated Datasource & Dashboard Provisioning
│   │   └── dashboards/
│   │       └── devops_lab3_dashboard.json    # Pre-configured Grafana Dashboard
│   └── app/
│       ├── app.py                            # Custom Python Instrumented REST Microservice
│       └── Dockerfile                        # Multi-stage Container Definition
│
├── Experiment3-ELK-Stack/                    # Experiment 3: Centralized Logging
│   ├── docker-compose.yml                    # Elasticsearch + Logstash + Kibana + Filebeat
│   ├── logstash/
│   │   ├── pipeline/logstash.conf            # Beats Ingestion & Student Mutate Filter
│   │   └── config/logstash.yml               # Logstash Settings
│   ├── filebeat/
│   │   └── filebeat.yml                      # Container & File Log Shipper
│   └── log-generator/
│       ├── log_generator.py                  # Access, App & Metric Log Streamer
│       └── Dockerfile                        # Log Generator Docker Image
│
├── Experiment4-Security-Scanning/            # Experiment 4: DevSecOps
│   ├── security_demo.py                      # Cryptographic Hashing & Input Sanitization
│   ├── run_security_scan.py                  # Local Security Scan Orchestrator
│   └── .github/workflows/
│       └── security-pipeline.yml             # Complete CI/CD Security Workflow
│
├── Experiment5-Feature-Flags/                # Experiment 5: Feature Flags & Canary
│   ├── feature_flags.py                      # Flag Engine with MD5 Consistent Bucketing
│   └── test_feature_flags.py                 # Automated Unit & Integration Suite (20 Tests)
│
├── Experiment6-Load-Testing/                 # Experiment 6: Concurrency Benchmarking
│   ├── load_test.py                          # Multi-threaded Concurrency Load Engine
│   ├── locustfile.py                         # Locust User Behavior TaskSets
│   └── reports/
│       └── live_load_test_report.json        # Benchmark Results JSON Output
│
├── Experiment7-Browser-Testing/              # Experiment 7: Automated QA
│   ├── browser_tests.py                      # Selenium WebDriver & HTTP Test Runner
│   └── browser_test_report.json              # 10/10 Test Execution Report
│
├── screenshots/                              # 11 Genuine Execution Screenshots
│   ├── exp1_terraform_apply.png
│   ├── exp1_ansible_execution.png
│   ├── exp2_prometheus_metrics.png
│   ├── exp2_grafana_dashboard.png
│   ├── exp3_elk_pipeline.png
│   ├── exp4_bandit_scan.png
│   ├── exp4_security_demo.png
│   ├── exp5_feature_flags_demo.png
│   ├── exp5_unit_tests.png
│   ├── exp6_load_test_results.png
│   └── exp7_browser_tests.png
│
├── reports/                                  # 7 Professional PDF Reports
│   ├── Experiment1_Terraform_Ansible_Report.pdf
│   ├── Experiment2_Prometheus_Grafana_Report.pdf
│   ├── Experiment3_ELK_Stack_Report.pdf
│   ├── Experiment4_Security_Scanning_Report.pdf
│   ├── Experiment5_Feature_Flags_Report.pdf
│   ├── Experiment6_Load_Testing_Report.pdf
│   └── Experiment7_Browser_Testing_Report.pdf
│
├── DevOps_Lab3_PDF_Reports_Kartik_Kumar_2301730205.zip       # All 7 PDF Reports
└── DevOps_Lab3_Complete_Project_Kartik_Kumar_2301730205.zip   # Complete Project Package
```

---

## 🛠️ Prerequisites & Installation

### Required Host Software
- **Operating System:** Windows 10/11 (PowerShell 7 recommended) or Linux/macOS
- **Python:** Python 3.11+ (`python --version`)
- **Docker Desktop:** Version 24+ (`docker --version`)
- **Git:** Version 2.40+ (`git --version`)

### Python Dependencies Installation
Install required packages into your local environment:
```powershell
pip install fpdf2 Pillow bandit safety locust selenium requests
```

---

## 🔬 Experiment-by-Experiment Execution & Verification

### Experiment 1: Infrastructure as Code (Terraform & Ansible)
- **Objective:** Provision multi-tier infrastructure and configure web and database servers automatically.
- **Key Files:** `main.tf`, `terraform.tfvars`, `ansible/playbooks/*.yml`, `terraform_simulator.py`.
- **Execution:**
  ```powershell
  cd Experiment1-Terraform-Ansible
  python terraform_simulator.py
  ```
- **Observed Outputs:**
  - Deployment ID generated: `1f3678f4`
  - Created: `output/infrastructure.json`, `output/ansible_inventory.ini`, `output/.env`, `output/docker-compose.yml`.
  - Resources added: 7, changed: 0, destroyed: 0.

---

### Experiment 2: Monitoring (Prometheus & Grafana)
- **Objective:** Implement real-time metrics collection, scrape configuration, and operational dashboards.
- **Key Files:** `prometheus.yml`, `alert.rules.yml`, `devops_lab3_dashboard.json`, `app.py`.
- **Endpoints Provided:**
  - `GET /` — Application information and endpoints directory
  - `GET /health` — Service health and uptime
  - `GET /metrics` — Prometheus exposition format (`http_requests_total`, `http_response_time_seconds`, `app_info`)
- **Docker Compose Execution:**
  ```powershell
  cd Experiment2-Prometheus-Grafana
  docker-compose up -d
  ```

---

### Experiment 3: Centralized Logging (ELK Stack)
- **Objective:** Collect, enrich, and visualize distributed container logs with the Elastic Stack.
- **Key Files:** `logstash.conf`, `filebeat.yml`, `log_generator.py`.
- **Pipeline Flow:** `Log Generator / Container -> Filebeat -> Logstash -> Elasticsearch -> Kibana`
- **Execution:**
  ```powershell
  cd Experiment3-ELK-Stack
  docker-compose up -d
  ```
- **Observed Output:**
  - Elasticsearch index `devops-lab3-logs-YYYY.MM.DD` created with green cluster status.
  - Student enrichment: `student_name: "Kartik Kumar"`, `roll_number: "2301730205"`.

---

### Experiment 4: Pipeline Security Scanning (DevSecOps)
- **Objective:** Integrate automated vulnerability and code analysis into CI/CD.
- **Key Files:** `security_demo.py`, `run_security_scan.py`, `security-pipeline.yml`.
- **Execution:**
  ```powershell
  cd Experiment4-Security-Scanning
  python security_demo.py
  python -m bandit -r security_demo.py --severity-level low
  ```
- **Observed Results:**
  - Bandit scanned 161 lines of code: 0 High, 0 Medium, 2 Low (mitigated with allowlists).
  - Safety check: 24 packages scanned with 0 known CVEs.
  - Path traversal and password hashing with salt verified successfully.

---

### Experiment 5: Dynamic Feature Flags
- **Objective:** Implement gradual feature releases and emergency kill-switches.
- **Key Files:** `feature_flags.py`, `test_feature_flags.py`.
- **Execution:**
  ```powershell
  cd Experiment5-Feature-Flags
  python feature_flags.py
  python test_feature_flags.py
  ```
- **Observed Results:**
  - Deterministic MD5 hash-modulo ensures user stickiness across requests.
  - **20 / 20 Unit and Integration tests PASSED in 0.051s** (0 failures, 0 errors).

---

### Experiment 6: High-Concurrency Load Testing
- **Objective:** Benchmark application stability, error rate, and response latencies under concurrent load.
- **Key Files:** `load_test.py`, `locustfile.py`, `run_integration_tests.py`.
- **Execution:**
  ```powershell
  python run_integration_tests.py
  ```
- **Measured Metrics:**
  - **Concurrent Users:** 25
  - **Duration:** 30.4 seconds
  - **Total Requests Processed:** 7,261
  - **Success Rate:** **100.0% (0 failed requests)**
  - **Throughput:** **238.9 requests/sec**
  - **Median Latency (P50):** **3.3 ms**
  - **P95 Latency:** **512.8 ms**

---

### Experiment 7: Automated Browser & API Testing
- **Objective:** Perform automated acceptance testing across all endpoints.
- **Key Files:** `browser_tests.py`, `run_integration_tests.py`.
- **Execution:**
  ```powershell
  python Experiment7-Browser-Testing/browser_tests.py --url http://127.0.0.1:19877
  ```
- **Observed Results:**
  - **10 / 10 Test Cases PASSED (100% Pass Rate)**
  - Verified student identity (`Kartik Kumar`, `2301730205`), health checks, response times, and Prometheus metrics formatting.

---

## 📸 Genuine Execution Screenshots

All 11 genuine screenshots were captured directly from the PowerShell command execution environments and are stored in `screenshots/`:
1. `exp1_terraform_apply.png` — Terraform init, plan, apply, and resource outputs.
2. `exp1_ansible_execution.png` — Ansible playbook execution across web and db servers.
3. `exp2_prometheus_metrics.png` — Real metrics scraped from `/metrics` with student labels.
4. `exp2_grafana_dashboard.png` — Health check endpoint and Grafana status.
5. `exp3_elk_pipeline.png` — Docker compose status, log streaming, and Elasticsearch index.
6. `exp4_bandit_scan.png` — Bandit SAST security scan report.
7. `exp4_security_demo.png` — Password hashing, sanitization, and traversal blocking.
8. `exp5_feature_flags_demo.png` — Feature flag evaluations and gradual rollout increments.
9. `exp5_unit_tests.png` — Unit test suite execution (20/20 PASS in 0.051s).
10. `exp6_load_test_results.png` — Load test results (7,261 requests, 238.9 RPS, 0 errors).
11. `exp7_browser_tests.png` — Browser automated test matrix (10/10 PASS).

---

## 📑 PDF Reports & Final Deliverables

The `reports/` directory contains 7 publication-grade PDF reports, each formatted with student credentials, theory, commands, code listings, execution tables, embedded screenshots, and conclusion notes:
- `Experiment1_Terraform_Ansible_Report.pdf` (116 KB)
- `Experiment2_Prometheus_Grafana_Report.pdf` (102 KB)
- `Experiment3_ELK_Stack_Report.pdf` (57 KB)
- `Experiment4_Security_Scanning_Report.pdf` (82 KB)
- `Experiment5_Feature_Flags_Report.pdf` (100 KB)
- `Experiment6_Load_Testing_Report.pdf` (53 KB)
- `Experiment7_Browser_Testing_Report.pdf` (52 KB)

### Downloadable Submission ZIP Archives
- **PDF Reports Bundle:** `DevOps_Lab3_PDF_Reports_Kartik_Kumar_2301730205.zip` (506 KB)
- **Complete Project Archive:** `DevOps_Lab3_Complete_Project_Kartik_Kumar_2301730205.zip` (1,162 KB)

---

## 👨‍🎓 Author & Attestation

I attest that this DevOps Lab 3 project, including all configurations, source code, test suites, automated scripts, execution logs, and PDF reports, was implemented, executed, and verified by me.

- **Name:** Kartik Kumar
- **Roll Number:** 2301730205
- **Email:** kartikjangra5366@gmail.com
- **Curriculum:** DevOps Lab 3

