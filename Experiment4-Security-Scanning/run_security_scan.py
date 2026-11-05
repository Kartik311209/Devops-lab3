"""
DevOps Lab 3 - Security Scanner Runner
Student: Kartik Kumar | Roll: 2301730205

Runs security scans locally and generates reports.
"""

import subprocess
import sys
import os
import json
import datetime

STUDENT_NAME = "Kartik Kumar"
ROLL_NUMBER = "2301730205"
EMAIL = "kartikjangra5366@gmail.com"

def run_command(cmd, capture=True):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture, text=True, timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print(f"  Student: {STUDENT_NAME} | Roll: {ROLL_NUMBER}")
    print("=" * 60)

def run_bandit_scan():
    """Run Bandit Python security scanner"""
    print_header("BANDIT - Python Security Scanner")
    
    # Check if bandit is installed
    code, out, err = run_command("bandit --version")
    if code != 0:
        print("Installing bandit...")
        run_command("pip install bandit -q")
    
    # Run scan
    code, out, err = run_command("bandit -r . -f txt -ll 2>&1")
    print(out if out else "No output from bandit")
    
    # Generate JSON report
    run_command("bandit -r . -f json -o reports/bandit_report.json -ll 2>&1")
    print("✓ Bandit scan complete. Report saved to reports/bandit_report.json")
    return {"tool": "bandit", "status": "completed", "exit_code": code}

def run_safety_scan():
    """Run Safety dependency vulnerability scanner"""
    print_header("SAFETY - Dependency Vulnerability Scanner")
    
    code, out, err = run_command("safety --version")
    if code != 0:
        run_command("pip install safety -q")
    
    code, out, err = run_command("safety check 2>&1")
    print(out if out else "Safety check completed")
    
    run_command("safety check --json -o reports/safety_report.json 2>&1")
    print("✓ Safety scan complete. Report saved to reports/safety_report.json")
    return {"tool": "safety", "status": "completed", "exit_code": code}

def run_pylint():
    """Run Pylint code quality check"""
    print_header("PYLINT - Code Quality Analysis")
    
    code, out, err = run_command("pylint --version")
    if code != 0:
        run_command("pip install pylint -q")
    
    code, out, err = run_command("pylint security_demo.py --score=yes 2>&1")
    print(out if out else "Pylint check completed")
    return {"tool": "pylint", "status": "completed", "exit_code": code}

def generate_security_report(results):
    """Generate comprehensive security report"""
    print_header("GENERATING SECURITY REPORT")
    
    os.makedirs("reports", exist_ok=True)
    
    report = {
        "title": "DevOps Lab 3 - Security Scan Report",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "student": {
            "name": STUDENT_NAME,
            "roll_number": ROLL_NUMBER,
            "email": EMAIL
        },
        "scan_results": results,
        "summary": {
            "total_scans": len(results),
            "completed": sum(1 for r in results if r.get("status") == "completed"),
            "tools_used": [r["tool"] for r in results]
        }
    }
    
    report_path = "reports/security_summary.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\nSecurity Scan Summary:")
    print(f"  Student    : {STUDENT_NAME}")
    print(f"  Roll       : {ROLL_NUMBER}")
    print(f"  Scans Run  : {len(results)}")
    print(f"  Report     : {report_path}")
    print(f"\nTools Used  : {', '.join(r['tool'] for r in results)}")
    print("\n✓ Security scanning complete!")
    
    return report

if __name__ == '__main__':
    print("=" * 60)
    print("DevOps Lab 3 - Security Scanner")
    print(f"Student: {STUDENT_NAME}")
    print(f"Roll   : {ROLL_NUMBER}")
    print(f"Email  : {EMAIL}")
    print("=" * 60)
    
    os.makedirs("reports", exist_ok=True)
    
    results = []
    results.append(run_bandit_scan())
    results.append(run_safety_scan())
    results.append(run_pylint())
    
    report = generate_security_report(results)
    sys.exit(0)

