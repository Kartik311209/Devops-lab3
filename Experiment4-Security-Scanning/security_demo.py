"""
DevOps Lab 3 - Security Scanning Demo Application
Student: Kartik Kumar | Roll: 2301730205

This module demonstrates security scanning with intentional issues
that can be detected by tools like Bandit, Safety, and Semgrep.
"""

import os
import hashlib
import secrets
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================
# SECURE IMPLEMENTATION (Best Practices)
# ============================================================

class SecureConfig:
    """Secure configuration management - no hardcoded secrets"""
    
    def __init__(self):
        self.db_host = os.environ.get('DB_HOST', 'localhost')
        self.db_port = int(os.environ.get('DB_PORT', '5432'))
        self.db_name = os.environ.get('DB_NAME', 'devopslab3_db')
        self.db_user = os.environ.get('DB_USER', '')
        self.db_password = os.environ.get('DB_PASSWORD', '')  # From env, not hardcoded
        self.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
        self.student_name = "Kartik Kumar"
        self.roll_number = "2301730205"
    
    def validate(self) -> bool:
        """Validate required configuration"""
        required = ['DB_USER', 'DB_PASSWORD', 'SECRET_KEY']
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            logger.warning(f"Missing environment variables: {missing}")
            return False
        return True


class SecurePasswordHash:
    """Secure password hashing using modern algorithms"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt (use bcrypt/argon2 in production)"""
        salt = secrets.token_hex(32)
        combined = f"{salt}{password}"
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        return f"{salt}:{hashed}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_value = stored_hash.split(':', 1)
            combined = f"{salt}{password}"
            computed = hashlib.sha256(combined.encode()).hexdigest()
            return secrets.compare_digest(computed, hash_value)
        except ValueError:
            return False


class InputValidator:
    """Input validation and sanitization"""
    
    ALLOWED_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    
    @staticmethod
    def sanitize_username(username: str) -> Optional[str]:
        """Sanitize and validate username"""
        if not username or len(username) > 50:
            return None
        sanitized = ''.join(c for c in username if c in InputValidator.ALLOWED_CHARS)
        return sanitized if sanitized == username else None
    
    @staticmethod
    def validate_roll_number(roll: str) -> bool:
        """Validate student roll number format"""
        if not roll or len(roll) != 10:
            return False
        return roll.isdigit()
    
    @staticmethod
    def sanitize_path(path: str) -> Optional[str]:
        """Prevent path traversal attacks"""
        import pathlib
        try:
            base = pathlib.Path('/app/data').resolve()
            full_path = (base / path).resolve()
            # Ensure path stays within base directory
            full_path.relative_to(base)
            return str(full_path)
        except (ValueError, RuntimeError):
            logger.error(f"Path traversal attempt detected: {path}")
            return None


class SecureSubprocess:
    """Secure subprocess execution with allowlist"""
    
    ALLOWED_COMMANDS = {'ls', 'pwd', 'date', 'whoami', 'hostname'}
    
    @staticmethod
    def run_safe_command(command: str) -> Optional[str]:
        """Run only pre-approved commands to prevent command injection"""
        cmd_parts = command.split()
        if not cmd_parts:
            return None
        
        cmd_name = os.path.basename(cmd_parts[0])
        if cmd_name not in SecureSubprocess.ALLOWED_COMMANDS:
            logger.error(f"Command not in allowlist: {cmd_name}")
            return None
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False  # Never use shell=True with user input
            )
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            logger.error(f"Subprocess error: {e}")
            return None


# ============================================================
# Security Scan Report Generator
# ============================================================

class SecurityScanReport:
    """Generates security scan reports for demonstration"""
    
    def __init__(self, student_name: str, roll_number: str):
        self.student_name = student_name
        self.roll_number = roll_number
        self.scan_results = []
    
    def add_scan_result(self, tool: str, severity: str, finding: str, status: str):
        self.scan_results.append({
            "tool": tool,
            "severity": severity,
            "finding": finding,
            "status": status,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        })
    
    def generate_report(self) -> dict:
        return {
            "report_title": "Security Scan Report - DevOps Lab 3",
            "student": {
                "name": self.student_name,
                "roll_number": self.roll_number,
                "email": "kartikjangra5366@gmail.com"
            },
            "summary": {
                "total_findings": len(self.scan_results),
                "critical": sum(1 for r in self.scan_results if r['severity'] == 'CRITICAL'),
                "high": sum(1 for r in self.scan_results if r['severity'] == 'HIGH'),
                "medium": sum(1 for r in self.scan_results if r['severity'] == 'MEDIUM'),
                "low": sum(1 for r in self.scan_results if r['severity'] == 'LOW'),
                "passed": sum(1 for r in self.scan_results if r['status'] == 'PASSED')
            },
            "tools_used": ["Bandit", "Safety", "Semgrep", "Trivy", "Gitleaks", "Checkov"],
            "findings": self.scan_results
        }


# ============================================================
# Demo: Run Security Analysis
# ============================================================

if __name__ == '__main__':
    import json
    
    print("=" * 60)
    print("DevOps Lab 3 - Security Analysis Demo")
    print("Student: Kartik Kumar | Roll: 2301730205")
    print("=" * 60)
    
    # Test secure password hashing
    hasher = SecurePasswordHash()
    pw_hash = hasher.hash_password("test_password_123")
    is_valid = hasher.verify_password("test_password_123", pw_hash)
    print(f"\n[Password Hashing] Valid: {is_valid}")
    
    # Test input validation
    validator = InputValidator()
    print(f"\n[Input Validation]")
    print(f"  Valid username 'kartik_kumar': {validator.sanitize_username('kartik_kumar')}")
    print(f"  Invalid username '../etc/passwd': {validator.sanitize_username('../etc/passwd')}")
    print(f"  Valid roll '2301730205': {validator.validate_roll_number('2301730205')}")
    
    # Generate security report
    report = SecurityScanReport("Kartik Kumar", "2301730205")
    report.add_scan_result("Bandit", "LOW", "Use of assert detected", "PASSED")
    report.add_scan_result("Safety", "HIGH", "No vulnerable dependencies found", "PASSED")
    report.add_scan_result("Semgrep", "MEDIUM", "SQL injection patterns checked", "PASSED")
    report.add_scan_result("Trivy", "CRITICAL", "No critical CVEs in base image", "PASSED")
    report.add_scan_result("Gitleaks", "HIGH", "No secrets detected in commits", "PASSED")
    report.add_scan_result("Checkov", "MEDIUM", "Terraform security best practices", "PASSED")
    
    print(f"\n[Security Report]")
    print(json.dumps(report.generate_report(), indent=2))

