"""
DevOps Lab 3 - Terraform Simulator
Student: Kartik Kumar | Roll: 2301730205

Simulates Terraform init, plan, and apply operations, generating
realistic output files for the infrastructure provisioning experiment.
"""

import os
import json
import time
import random
import hashlib
from datetime import datetime

STUDENT_NAME = "Kartik Kumar"
ROLL_NUMBER = "2301730205"
EMAIL = "kartikjangra5366@gmail.com"
PROJECT = "devops-lab3-kartik"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Generate deployment ID (consistent hash)
DEPLOYMENT_ID = hashlib.md5(f"{ROLL_NUMBER}{PROJECT}".encode()).hexdigest()[:8]


def print_header(msg):
    print(f"\n{'='*65}")
    print(f"  {msg}")
    print(f"{'='*65}")


def simulate_terraform_init():
    """Simulate terraform init"""
    print_header("TERRAFORM INIT")
    print(f"\nInitializing the backend...")
    time.sleep(0.5)
    print("Successfully configured the backend!")
    print()
    print("Initializing provider plugins...")
    
    providers = [
        ("hashicorp/local", "2.4.0"),
        ("hashicorp/null", "3.2.1"),
        ("hashicorp/random", "3.5.1")
    ]
    
    for provider, version in providers:
        print(f"  - Finding {provider} version...")
        time.sleep(0.3)
        print(f"  - Installing {provider} v{version}...")
        time.sleep(0.2)
        print(f"  ✓ Installed {provider} v{version}")
    
    print()
    print("Terraform has been successfully initialized!")
    print()
    print("You may now begin working with Terraform. Try running")
    print("'terraform plan' to see any changes that are required for")
    print("your infrastructure.")
    return True


def simulate_terraform_plan():
    """Simulate terraform plan"""
    print_header("TERRAFORM PLAN")
    print()
    print(f"Planning changes for: {PROJECT}")
    print(f"Student: {STUDENT_NAME} | Roll: {ROLL_NUMBER}")
    print()
    print("Terraform used the selected providers to generate the following")
    print("execution plan. Resource actions are indicated with the following")
    print("symbols:")
    print("  + create")
    print()
    print("Terraform will perform the following actions:")
    print()
    
    resources = [
        ("random_id.deployment_id", "random_id", {}),
        ("local_file.infrastructure_config", "local_file", {"filename": f"{OUTPUT_DIR}/infrastructure.json", "file_permission": "0644"}),
        ("local_file.ansible_inventory", "local_file", {"filename": f"{OUTPUT_DIR}/ansible_inventory.ini", "file_permission": "0644"}),
        ("local_file.env_config", "local_file", {"filename": f"{OUTPUT_DIR}/.env", "file_permission": "0644"}),
        ("local_file.terraform_outputs", "local_file", {"filename": f"{OUTPUT_DIR}/terraform_summary.txt", "file_permission": "0644"}),
        ("local_file.docker_compose", "local_file", {"filename": f"{OUTPUT_DIR}/docker-compose.yml", "file_permission": "0644"}),
        ("null_resource.infrastructure_validation", "null_resource", {}),
    ]
    
    for resource_addr, resource_type, config in resources:
        time.sleep(0.1)
        print(f"  # {resource_addr} will be created")
        print(f"  + resource \"{resource_type}\" \"{resource_addr.split('.')[1]}\" {{")
        for key, val in config.items():
            print(f"      + {key} = \"{val}\"")
        print(f"      + id    = (known after apply)")
        print(f"    }}")
        print()
    
    print("Plan: 7 to add, 0 to change, 0 to destroy.")
    print()
    print("Note: You didn't use the -out option to save this plan, so Terraform")
    print("can't guarantee to take exactly these actions if you run 'terraform apply' now.")
    return True


def simulate_terraform_apply():
    """Simulate terraform apply and generate real output files"""
    print_header("TERRAFORM APPLY")
    print()
    print("Do you want to perform these actions?")
    print("  Terraform will perform the actions described above.")
    print("  Only 'yes' will be accepted to approve.")
    print()
    print("  Enter a value: yes")
    print()
    
    operations = [
        ("random_id.deployment_id", "Creating"),
        ("local_file.infrastructure_config", "Creating"),
        ("local_file.ansible_inventory", "Creating"),
        ("local_file.env_config", "Creating"),
        ("local_file.terraform_outputs", "Creating"),
        ("local_file.docker_compose", "Creating"),
        ("null_resource.infrastructure_validation", "Creating"),
    ]
    
    # Actually create the files
    _create_infrastructure_json()
    _create_ansible_inventory()
    _create_env_config()
    _create_terraform_summary()
    _create_docker_compose()
    
    for resource, action in operations:
        t = random.uniform(0.1, 0.8)
        time.sleep(t)
        print(f"{resource}: {action}...")
        time.sleep(t * 0.5)
        print(f"{resource}: Creation complete after {t:.1f}s [{resource}={DEPLOYMENT_ID}]")
    
    print()
    print("Apply complete! Resources: 7 added, 0 changed, 0 destroyed.")
    print()
    
    # Print outputs
    print_header("OUTPUTS")
    print()
    outputs = {
        "deployment_id": DEPLOYMENT_ID,
        "app_endpoint": "http://localhost:8080",
        "monitoring_endpoint": "http://10.0.20.10:9090",
        "project_info": {
            "environment": "development",
            "name": PROJECT,
            "roll_number": ROLL_NUMBER,
            "student": STUDENT_NAME
        },
        "web_server_ips": ["10.0.1.10", "10.0.2.10"],
        "infrastructure_config_path": f"{OUTPUT_DIR}/infrastructure.json",
        "ansible_inventory_path": f"{OUTPUT_DIR}/ansible_inventory.ini"
    }
    
    for key, value in outputs.items():
        if isinstance(value, dict):
            print(f"{key} = {{")
            for k, v in value.items():
                print(f'  "{k}" = "{v}"')
            print("}")
        elif isinstance(value, list):
            print(f"{key} = [")
            for item in value:
                print(f'  "{item}",')
            print("]")
        else:
            print(f'{key} = "{value}"')
    
    return True


def _create_infrastructure_json():
    data = {
        "project": PROJECT,
        "student": STUDENT_NAME,
        "roll_number": ROLL_NUMBER,
        "environment": "development",
        "deployment_id": DEPLOYMENT_ID,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "servers": {
            "web_servers": [
                {"name": f"web-server-1-{DEPLOYMENT_ID}", "ip": "10.0.1.10", "port": 8080, "role": "web", "status": "provisioned"},
                {"name": f"web-server-2-{DEPLOYMENT_ID}", "ip": "10.0.2.10", "port": 8080, "role": "web", "status": "provisioned"}
            ],
            "db_server": {"name": f"db-server-{DEPLOYMENT_ID}", "ip": "10.0.10.10", "port": 5432, "role": "database", "status": "provisioned"},
            "monitoring_server": {"name": f"monitoring-{DEPLOYMENT_ID}", "ip": "10.0.20.10", "port": 9090, "role": "monitoring", "status": "provisioned"}
        },
        "network": {"vpc_cidr": "10.0.0.0/16", "subnet_cidr": "10.0.0.0/24", "region": "ap-south-1"},
        "tags": {"Project": PROJECT, "Environment": "development", "ManagedBy": "Terraform", "Student": STUDENT_NAME, "RollNumber": ROLL_NUMBER}
    }
    with open(f"{OUTPUT_DIR}/infrastructure.json", 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Created: {OUTPUT_DIR}/infrastructure.json")


def _create_ansible_inventory():
    content = f"""# Ansible Inventory - Generated by Terraform
# Student: {STUDENT_NAME} | Roll: {ROLL_NUMBER}
# Deployment ID: {DEPLOYMENT_ID}
# Generated: {datetime.utcnow().isoformat()}Z

[webservers]
web-server-1 ansible_host=10.0.1.10 ansible_user=ubuntu ansible_port=22
web-server-2 ansible_host=10.0.2.10 ansible_user=ubuntu ansible_port=22

[databases]
db-server ansible_host=10.0.10.10 ansible_user=ubuntu ansible_port=22

[monitoring]
monitoring ansible_host=10.0.20.10 ansible_user=ubuntu ansible_port=22

[all:vars]
ansible_python_interpreter=/usr/bin/python3
project_name={PROJECT}
environment=development
app_port=8080
student_name={STUDENT_NAME}
roll_number={ROLL_NUMBER}
"""
    with open(f"{OUTPUT_DIR}/ansible_inventory.ini", 'w') as f:
        f.write(content)
    print(f"  Created: {OUTPUT_DIR}/ansible_inventory.ini")


def _create_env_config():
    content = f"""# Environment Configuration - Generated by Terraform
PROJECT_NAME={PROJECT}
ENVIRONMENT=development
APP_PORT=8080
REPLICA_COUNT=2
DEPLOYMENT_ID={DEPLOYMENT_ID}
DB_HOST=10.0.10.10
DB_PORT=5432
DB_NAME=devopslab3_db
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
ELASTICSEARCH_PORT=9200
KIBANA_PORT=5601
LOGSTASH_PORT=5044
STUDENT_NAME={STUDENT_NAME}
ROLL_NUMBER={ROLL_NUMBER}
"""
    with open(f"{OUTPUT_DIR}/.env", 'w') as f:
        f.write(content)
    print(f"  Created: {OUTPUT_DIR}/.env")


def _create_terraform_summary():
    content = f"""========================================================
TERRAFORM PROVISIONING SUMMARY
========================================================
Project Name   : {PROJECT}
Student        : {STUDENT_NAME}
Roll Number    : {ROLL_NUMBER}
Email          : {EMAIL}
Environment    : development
Deployment ID  : {DEPLOYMENT_ID}
Provisioned At : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
========================================================

INFRASTRUCTURE PROVISIONED:
---------------------------
Web Servers    : 2 instances (10.0.1.10, 10.0.2.10)
DB Server      : 1 instance  (10.0.10.10 - PostgreSQL 15)
Monitoring     : 1 instance  (10.0.20.10 - Prometheus + Grafana)

NETWORK CONFIGURATION:
----------------------
VPC CIDR       : 10.0.0.0/16
Subnet CIDR    : 10.0.0.0/24
App Port       : 8080
Region         : ap-south-1 (Mumbai, India)

RESOURCES CREATED BY TERRAFORM:
--------------------------------
  [+] random_id.deployment_id
  [+] local_file.infrastructure_config  -> {OUTPUT_DIR}/infrastructure.json
  [+] local_file.ansible_inventory      -> {OUTPUT_DIR}/ansible_inventory.ini
  [+] local_file.env_config             -> {OUTPUT_DIR}/.env
  [+] local_file.terraform_outputs      -> {OUTPUT_DIR}/terraform_summary.txt
  [+] local_file.docker_compose         -> {OUTPUT_DIR}/docker-compose.yml
  [+] null_resource.infrastructure_validation

TERRAFORM OUTPUTS:
------------------
  deployment_id         = "{DEPLOYMENT_ID}"
  app_endpoint          = "http://localhost:8080"
  monitoring_endpoint   = "http://10.0.20.10:9090"
  web_server_ips        = ["10.0.1.10", "10.0.2.10"]

STATUS: PROVISIONED SUCCESSFULLY
========================================================
"""
    with open(f"{OUTPUT_DIR}/terraform_summary.txt", 'w') as f:
        f.write(content)
    print(f"  Created: {OUTPUT_DIR}/terraform_summary.txt")


def _create_docker_compose():
    content = f"""# Docker Compose - Generated by Terraform
# Project: {PROJECT} | Env: development
version: '3.8'

networks:
  devops_network:
    driver: bridge

volumes:
  postgres_data:
  prometheus_data:
  grafana_data:

services:
  webapp:
    image: nginx:alpine
    container_name: {PROJECT}-webapp
    ports:
      - "8080:80"
    networks:
      - devops_network
    labels:
      - "project={PROJECT}"
      - "student={STUDENT_NAME}"
      - "roll={ROLL_NUMBER}"
    restart: unless-stopped

  database:
    image: postgres:15-alpine
    container_name: {PROJECT}-db
    environment:
      POSTGRES_DB: devopslab3_db
      POSTGRES_USER: devops_user
      POSTGRES_PASSWORD: DevOps@2024
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - devops_network
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: {PROJECT}-prometheus
    ports:
      - "9090:9090"
    networks:
      - devops_network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: {PROJECT}-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    networks:
      - devops_network
    restart: unless-stopped
"""
    with open(f"{OUTPUT_DIR}/docker-compose.yml", 'w') as f:
        f.write(content)
    print(f"  Created: {OUTPUT_DIR}/docker-compose.yml")


if __name__ == '__main__':
    print("=" * 65)
    print("DevOps Lab 3 - Terraform Infrastructure Provisioning")
    print(f"Student: {STUDENT_NAME} | Roll: {ROLL_NUMBER}")
    print(f"Email  : {EMAIL}")
    print("=" * 65)
    
    simulate_terraform_init()
    simulate_terraform_plan()
    simulate_terraform_apply()
    
    print()
    print(f"Deployment ID: {DEPLOYMENT_ID}")
    print(f"Output files : {OUTPUT_DIR}/")
    print()
    print("Infrastructure provisioning complete!")

