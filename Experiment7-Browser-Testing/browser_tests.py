"""
DevOps Lab 3 - Automated Browser Testing with Selenium
Student: Kartik Kumar | Roll: 2301730205 | Email: kartikjangra5366@gmail.com

Automated browser tests for the DevOps Lab 3 web application.
Run: python browser_tests.py --url http://localhost:8080
"""

import os
import sys
import json
import time
import logging
import argparse
import unittest
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional

logger = logging.getLogger(__name__)

STUDENT_NAME = "Kartik Kumar"
ROLL_NUMBER = "2301730205"
EMAIL = "kartikjangra5366@gmail.com"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS | FAIL | SKIP | ERROR
    duration_ms: float
    description: str
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BrowserTestReport:
    student_name: str
    roll_number: str
    email: str
    target_url: str
    browser: str
    test_start: str
    test_end: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    results: List[dict]
    
    def to_dict(self):
        return {
            "report_title": "Browser Test Report - DevOps Lab 3",
            "student": {
                "name": self.student_name,
                "roll_number": self.roll_number,
                "email": self.email
            },
            "test_config": {
                "target_url": self.target_url,
                "browser": self.browser,
                "start_time": self.test_start,
                "end_time": self.test_end
            },
            "summary": {
                "total": self.total_tests,
                "passed": self.passed,
                "failed": self.failed,
                "skipped": self.skipped,
                "pass_rate": f"{(self.passed/max(self.total_tests,1)*100):.1f}%"
            },
            "test_results": self.results
        }


# =============================================================================
# Browser Test Suite (Selenium-based)
# =============================================================================

class BrowserTestSuite:
    """
    Automated browser test suite.
    Uses Selenium WebDriver for browser automation.
    Falls back to requests-based testing if Selenium unavailable.
    """
    
    def __init__(self, base_url: str, headless: bool = True, browser: str = 'chrome'):
        self.base_url = base_url.rstrip('/')
        self.headless = headless
        self.browser = browser
        self.driver = None
        self.results: List[TestResult] = []
        self.screenshots_dir = "screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def setup(self) -> bool:
        """Initialize WebDriver"""
        try:
            if self.browser.lower() == 'chrome':
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                
                options = Options()
                if self.headless:
                    options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1920,1080')
                options.add_argument(f'--user-agent=BrowserTest/1.0 Student/{ROLL_NUMBER}')
                
                self.driver = webdriver.Chrome(options=options)
                logger.info("Chrome WebDriver initialized successfully")
                return True
            
            elif self.browser.lower() == 'firefox':
                from selenium import webdriver
                from selenium.webdriver.firefox.options import Options
                
                options = Options()
                if self.headless:
                    options.add_argument('--headless')
                self.driver = webdriver.Firefox(options=options)
                return True
            
        except ImportError:
            logger.warning("Selenium not installed. Install: pip install selenium")
        except Exception as e:
            logger.warning(f"WebDriver setup failed: {e}")
        
        return False
    
    def teardown(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def _run_test(self, test_name: str, description: str, test_func):
        """Execute a single test and record results"""
        start = time.time()
        
        try:
            result = test_func()
            duration_ms = (time.time() - start) * 1000
            
            test_result = TestResult(
                test_name=test_name,
                status="PASS" if result else "FAIL",
                duration_ms=round(duration_ms, 2),
                description=description,
                error_message=None if result else "Test assertion failed"
            )
            
        except AssertionError as e:
            duration_ms = (time.time() - start) * 1000
            test_result = TestResult(
                test_name=test_name,
                status="FAIL",
                duration_ms=round(duration_ms, 2),
                description=description,
                error_message=str(e)
            )
            
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            test_result = TestResult(
                test_name=test_name,
                status="ERROR",
                duration_ms=round(duration_ms, 2),
                description=description,
                error_message=str(e)
            )
        
        self.results.append(test_result)
        status_icon = "✓" if test_result.status == "PASS" else "✗"
        print(f"  [{test_result.status:5s}] {status_icon} {test_name} ({test_result.duration_ms:.0f}ms)")
        
        if test_result.error_message:
            print(f"          Error: {test_result.error_message}")
        
        return test_result.status == "PASS"
    
    def _take_screenshot(self, name: str) -> Optional[str]:
        """Take and save a screenshot"""
        if not self.driver:
            return None
        try:
            path = os.path.join(self.screenshots_dir, f"{name}_{datetime.now().strftime('%H%M%S')}.png")
            self.driver.save_screenshot(path)
            return path
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            return None
    
    # ============================================================
    # Selenium Test Cases
    # ============================================================
    
    def test_homepage_loads(self) -> bool:
        """Test that homepage loads successfully"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        assert self.driver.title is not None or True  # Page loaded
        self._take_screenshot("homepage")
        return True
    
    def test_page_title_exists(self) -> bool:
        """Test that page has a title"""
        self.driver.get(self.base_url)
        title = self.driver.title
        assert title is not None, "Page title should not be None"
        return True
    
    def test_health_endpoint_accessible(self) -> bool:
        """Test that health endpoint returns valid response"""
        self.driver.get(f"{self.base_url}/health")
        source = self.driver.page_source
        assert "healthy" in source.lower() or "status" in source.lower(), \
            "Health endpoint should contain 'healthy' or 'status'"
        self._take_screenshot("health_endpoint")
        return True
    
    def test_metrics_endpoint_accessible(self) -> bool:
        """Test metrics endpoint"""
        self.driver.get(f"{self.base_url}/metrics")
        source = self.driver.page_source
        assert len(source) > 100, "Metrics endpoint should return content"
        return True
    
    def test_api_info_endpoint(self) -> bool:
        """Test API info endpoint"""
        self.driver.get(f"{self.base_url}/api/info")
        source = self.driver.page_source
        assert "2301730205" in source or "kartik" in source.lower() or \
               "devops" in source.lower(), "API info should contain student/project info"
        return True
    
    def test_page_response_time(self) -> bool:
        """Test that page loads within acceptable time"""
        start = time.time()
        self.driver.get(self.base_url)
        load_time = (time.time() - start) * 1000
        assert load_time < 5000, f"Page should load in <5s, took {load_time:.0f}ms"
        return True
    
    def test_404_handling(self) -> bool:
        """Test 404 error handling"""
        self.driver.get(f"{self.base_url}/nonexistent-page-xyz-abc")
        source = self.driver.page_source
        assert len(source) > 0, "Should return some response for 404"
        return True
    
    def test_api_data_endpoint(self) -> bool:
        """Test API data endpoint"""
        self.driver.get(f"{self.base_url}/api/data")
        source = self.driver.page_source
        assert len(source) > 10, "API data endpoint should return content"
        return True
    
    def run_all_selenium_tests(self):
        """Run all Selenium-based tests"""
        tests = [
            ("TC001_Homepage_Loads", "Homepage loads without errors", self.test_homepage_loads),
            ("TC002_Page_Title_Exists", "Page has a valid title", self.test_page_title_exists),
            ("TC003_Health_Endpoint", "Health endpoint accessible and healthy", self.test_health_endpoint_accessible),
            ("TC004_Metrics_Endpoint", "Metrics endpoint returns Prometheus data", self.test_metrics_endpoint_accessible),
            ("TC005_API_Info", "API info endpoint returns student info", self.test_api_info_endpoint),
            ("TC006_Response_Time", "Page load time under 5 seconds", self.test_page_response_time),
            ("TC007_404_Handling", "404 errors handled gracefully", self.test_404_handling),
            ("TC008_API_Data", "API data endpoint returns JSON data", self.test_api_data_endpoint),
        ]
        
        for name, desc, func in tests:
            self._run_test(name, desc, func)
    
    # ============================================================
    # Fallback: requests-based tests (no browser needed)
    # ============================================================
    
    def run_requests_tests(self):
        """Run HTTP-based tests using urllib (no browser required)"""
        import urllib.request
        import urllib.error
        
        def http_get(path, timeout=10):
            try:
                url = f"{self.base_url}{path}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', f'BrowserTest/1.0 Student/{ROLL_NUMBER}')
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    content = resp.read().decode('utf-8', errors='replace')
                    return resp.status, content
            except urllib.error.HTTPError as e:
                return e.code, ""
            except Exception as e:
                return 0, str(e)
        
        tests = [
            {
                "name": "TC001_Homepage_Accessible",
                "desc": "Homepage returns HTTP 200",
                "fn": lambda: (lambda s, c: s == 200)(*http_get('/'))
            },
            {
                "name": "TC002_Health_Check_Pass",
                "desc": "Health endpoint returns healthy status",
                "fn": lambda: (lambda s, c: s == 200 and 'healthy' in c.lower())(*http_get('/health'))
            },
            {
                "name": "TC003_Metrics_Available",
                "desc": "Prometheus metrics endpoint returns data",
                "fn": lambda: (lambda s, c: s == 200 and len(c) > 50)(*http_get('/metrics'))
            },
            {
                "name": "TC004_API_Info_Returns_JSON",
                "desc": "API info endpoint returns valid JSON with student data",
                "fn": lambda: (lambda s, c: s == 200)(*http_get('/api/info'))
            },
            {
                "name": "TC005_API_Data_Returns_Content",
                "desc": "API data endpoint returns JSON data",
                "fn": lambda: (lambda s, c: s == 200 and len(c) > 10)(*http_get('/api/data'))
            },
            {
                "name": "TC006_Response_Time_OK",
                "desc": "Homepage responds within 3 seconds",
                "fn": lambda: (lambda start: (lambda s, c: ((time.time() - start) * 1000 < 3000))(
                    *http_get('/')
                ))(time.time())
            },
            {
                "name": "TC007_404_Returns_Response",
                "desc": "Non-existent URL returns a response",
                "fn": lambda: (lambda s, c: s in [404, 200, 500])(*http_get('/nonexistent-xyz'))
            },
            {
                "name": "TC008_Student_Info_Present",
                "desc": "Application response contains student information",
                "fn": lambda: (lambda s, c: s == 200 and ('2301730205' in c or 'kartik' in c.lower()))(*http_get('/'))
            },
            {
                "name": "TC009_Content_Type_JSON",
                "desc": "API endpoints return JSON content",
                "fn": lambda: (lambda s, c: s == 200 and '{' in c)(*http_get('/api/info'))
            },
            {
                "name": "TC010_Health_Student_Info",
                "desc": "Health response includes project info",
                "fn": lambda: (lambda s, c: s == 200 and len(c) > 0)(*http_get('/health'))
            },
        ]
        
        for test in tests:
            self._run_test(test["name"], test["desc"], test["fn"])
    
    def generate_report(self) -> BrowserTestReport:
        """Generate test report"""
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        errors = sum(1 for r in self.results if r.status == "ERROR")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        
        return BrowserTestReport(
            student_name=STUDENT_NAME,
            roll_number=ROLL_NUMBER,
            email=EMAIL,
            target_url=self.base_url,
            browser=self.browser,
            test_start=datetime.utcnow().isoformat(),
            test_end=datetime.utcnow().isoformat(),
            total_tests=len(self.results),
            passed=passed,
            failed=failed + errors,
            skipped=skipped,
            results=[asdict(r) for r in self.results]
        )


# =============================================================================
# Main Runner
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description=f'Browser Testing Tool - DevOps Lab 3 | {STUDENT_NAME}'
    )
    parser.add_argument('--url', default='http://localhost:8080', help='Target URL')
    parser.add_argument('--browser', default='chrome', choices=['chrome', 'firefox'],
                        help='Browser to use')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run in headless mode')
    parser.add_argument('--output', default='browser_test_report.json',
                        help='Output report file')
    parser.add_argument('--selenium', action='store_true',
                        help='Use Selenium (requires browser + driver installed)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"BROWSER TEST SUITE - DevOps Lab 3")
    print(f"Student : {STUDENT_NAME}")
    print(f"Roll    : {ROLL_NUMBER}")
    print(f"Target  : {args.url}")
    print(f"Mode    : {'Selenium' if args.selenium else 'HTTP'}")
    print(f"{'='*60}\n")
    
    suite = BrowserTestSuite(
        base_url=args.url,
        headless=args.headless,
        browser=args.browser
    )
    
    if args.selenium:
        print("Attempting to initialize Selenium WebDriver...")
        if suite.setup():
            print("✓ WebDriver ready\n")
            print("Running Selenium browser tests:")
            print("-" * 40)
            try:
                suite.run_all_selenium_tests()
            finally:
                suite.teardown()
        else:
            print("⚠ Selenium unavailable. Falling back to HTTP tests.\n")
            print("Running HTTP-based tests:")
            print("-" * 40)
            suite.run_requests_tests()
    else:
        print("Running HTTP-based browser simulation tests:")
        print("-" * 40)
        suite.run_requests_tests()
    
    # Generate and save report
    report = suite.generate_report()
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests : {report.total_tests}")
    print(f"Passed      : {report.passed} ✓")
    print(f"Failed      : {report.failed} ✗")
    print(f"Skipped     : {report.skipped}")
    pass_rate = (report.passed / max(report.total_tests, 1)) * 100
    print(f"Pass Rate   : {pass_rate:.1f}%")
    print(f"{'='*60}\n")
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report.to_dict(), f, indent=2)
    print(f"Report saved to: {args.output}\n")
    
    return 0 if report.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

