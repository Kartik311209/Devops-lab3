"""
DevOps Lab 3 - Feature Flags Tests
Student: Kartik Kumar | Roll: 2301730205

Unit and integration tests for the feature flag system.
"""

import os
import sys
import json
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_flags import (
    FeatureFlag, FeatureFlagStore, FeatureFlagService,
    FlagEvaluation, RolloutStrategy
)


class TestFeatureFlagStore(unittest.TestCase):
    """Tests for FeatureFlagStore"""
    
    def setUp(self):
        self.temp_file = tempfile.mktemp(suffix='.json')
        self.store = FeatureFlagStore(self.temp_file)
    
    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_set_and_get_flag(self):
        flag = FeatureFlag(
            name="test-flag",
            enabled=True,
            description="Test flag",
            created_by="Kartik Kumar"
        )
        self.store.set(flag)
        retrieved = self.store.get("test-flag")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "test-flag")
        self.assertTrue(retrieved.enabled)
    
    def test_get_nonexistent_flag(self):
        result = self.store.get("nonexistent")
        self.assertIsNone(result)
    
    def test_delete_flag(self):
        flag = FeatureFlag(name="del-flag", enabled=True, description="To delete")
        self.store.set(flag)
        self.assertTrue(self.store.delete("del-flag"))
        self.assertIsNone(self.store.get("del-flag"))
    
    def test_delete_nonexistent(self):
        self.assertFalse(self.store.delete("nonexistent"))
    
    def test_list_all_flags(self):
        for i in range(5):
            self.store.set(FeatureFlag(name=f"flag-{i}", enabled=True, description=f"Flag {i}"))
        flags = self.store.list_all()
        self.assertEqual(len(flags), 5)
    
    def test_persistence(self):
        """Test that flags persist across store instances"""
        flag = FeatureFlag(name="persist-flag", enabled=True, description="Persistent")
        self.store.set(flag)
        
        # Create new store instance with same file
        new_store = FeatureFlagStore(self.temp_file)
        retrieved = new_store.get("persist-flag")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "persist-flag")


class TestFeatureFlagService(unittest.TestCase):
    """Tests for FeatureFlagService"""
    
    def setUp(self):
        self.temp_file = tempfile.mktemp(suffix='.json')
        self.store = FeatureFlagStore(self.temp_file)
        self.service = FeatureFlagService(self.store)
        
        # Student info
        self.student = "kartik_kumar"
        self.roll = "2301730205"
    
    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_nonexistent_flag_returns_false(self):
        result = self.service.is_enabled("nonexistent-flag", self.student)
        self.assertFalse(result)
    
    def test_disabled_flag_returns_false(self):
        self.service.create_flag("disabled-flag", False, "Disabled test flag")
        result = self.service.is_enabled("disabled-flag", self.student)
        self.assertFalse(result)
    
    def test_all_users_strategy_enabled(self):
        self.service.create_flag(
            "all-users-flag", True, "All users",
            strategy=RolloutStrategy.ALL_USERS.value
        )
        result = self.service.is_enabled("all-users-flag", self.student)
        self.assertTrue(result)
    
    def test_percentage_rollout_deterministic(self):
        """Same user always gets same result for same flag"""
        self.service.create_flag(
            "percentage-flag", True, "50% rollout",
            strategy=RolloutStrategy.PERCENTAGE.value,
            percentage=50.0
        )
        
        # Same user, same flag -> consistent result
        results = [
            self.service.is_enabled("percentage-flag", "user_kartik")
            for _ in range(10)
        ]
        self.assertTrue(all(r == results[0] for r in results), "Results must be deterministic")
    
    def test_percentage_distribution(self):
        """Test that percentage rollout distributes correctly"""
        self.service.create_flag(
            "50pct-flag", True, "50% rollout",
            strategy=RolloutStrategy.PERCENTAGE.value,
            percentage=50.0
        )
        
        # Test with 1000 users
        users = [f"user_{i}" for i in range(1000)]
        enabled = sum(1 for u in users if self.service.is_enabled("50pct-flag", u))
        
        # Should be roughly 50% (within 10%)
        self.assertGreater(enabled, 400, f"Expected ~500 enabled, got {enabled}")
        self.assertLess(enabled, 600, f"Expected ~500 enabled, got {enabled}")
    
    def test_user_list_strategy(self):
        self.service.create_flag(
            "user-list-flag", True, "Specific users",
            strategy=RolloutStrategy.USER_LIST.value,
            users=["kartik_kumar", "alice"]
        )
        
        self.assertTrue(self.service.is_enabled("user-list-flag", "kartik_kumar"))
        self.assertTrue(self.service.is_enabled("user-list-flag", "alice"))
        self.assertFalse(self.service.is_enabled("user-list-flag", "bob"))
        self.assertFalse(self.service.is_enabled("user-list-flag", "charlie"))
    
    def test_toggle_flag(self):
        self.service.create_flag("toggle-flag", True, "Toggle test")
        self.assertTrue(self.service.is_enabled("toggle-flag", "user1"))
        
        self.service.toggle_flag("toggle-flag")
        self.assertFalse(self.service.is_enabled("toggle-flag", "user1"))
        
        self.service.toggle_flag("toggle-flag")
        self.assertTrue(self.service.is_enabled("toggle-flag", "user1"))
    
    def test_evaluation_has_reason(self):
        self.service.create_flag("reason-flag", True, "Reason test")
        evaluation = self.service.evaluate("reason-flag", "kartik")
        self.assertIsNotNone(evaluation.reason)
        self.assertTrue(len(evaluation.reason) > 0)
    
    def test_zero_percent_rollout(self):
        self.service.create_flag(
            "zero-pct", True, "Zero percent",
            strategy=RolloutStrategy.PERCENTAGE.value,
            percentage=0.0
        )
        users = [f"user_{i}" for i in range(100)]
        enabled = sum(1 for u in users if self.service.is_enabled("zero-pct", u))
        self.assertEqual(enabled, 0, "Zero percent should disable for all")
    
    def test_hundred_percent_rollout(self):
        self.service.create_flag(
            "full-pct", True, "Full percent",
            strategy=RolloutStrategy.PERCENTAGE.value,
            percentage=100.0
        )
        users = [f"user_{i}" for i in range(100)]
        enabled = sum(1 for u in users if self.service.is_enabled("full-pct", u))
        self.assertEqual(enabled, 100, "100 percent should enable for all")
    
    def test_stats_tracking(self):
        self.service.create_flag("stats-flag", True, "Stats test")
        
        for i in range(10):
            self.service.evaluate("stats-flag", f"user_{i}")
        
        stats = self.service.get_stats()
        self.assertIn("flags", stats)
        self.assertIn("stats-flag", stats["flags"])
        self.assertEqual(stats["flags"]["stats-flag"]["total"], 10)
    
    def test_student_metadata(self):
        """Verify student metadata in service"""
        self.assertEqual(self.service.STUDENT_INFO["name"], "Kartik Kumar")
        self.assertEqual(self.service.STUDENT_INFO["roll"], "2301730205")
        self.assertEqual(self.service.STUDENT_INFO["email"], "kartikjangra5366@gmail.com")


class TestFeatureFlagIntegration(unittest.TestCase):
    """Integration tests for feature flags"""
    
    def setUp(self):
        self.temp_file = tempfile.mktemp(suffix='.json')
        self.service = FeatureFlagService(FeatureFlagStore(self.temp_file))
    
    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
    
    def test_gradual_rollout_workflow(self):
        """Test a typical gradual feature rollout workflow"""
        # Start at 0%
        self.service.create_flag(
            "gradual-feature", True, "Gradual rollout",
            strategy="percentage", percentage=0
        )
        
        users = [f"user_{i}" for i in range(100)]
        
        def check_coverage():
            return sum(1 for u in users if self.service.is_enabled("gradual-feature", u))
        
        self.assertEqual(check_coverage(), 0)
        
        # Roll out to 25%
        self.service.set_rollout_percentage("gradual-feature", 25)
        coverage_25 = check_coverage()
        self.assertGreater(coverage_25, 15)
        self.assertLess(coverage_25, 40)
        
        # Roll out to 100%
        self.service.set_rollout_percentage("gradual-feature", 100)
        self.assertEqual(check_coverage(), 100)
        
        # Roll back to 0%
        self.service.set_rollout_percentage("gradual-feature", 0)
        self.assertEqual(check_coverage(), 0)
    
    def test_emergency_disable(self):
        """Test emergency feature disable"""
        self.service.create_flag("critical-feature", True, "Critical feature")
        
        # Feature is enabled
        self.assertTrue(self.service.is_enabled("critical-feature", "user1"))
        
        # Emergency: disable flag
        flag = self.service._store.get("critical-feature")
        flag.enabled = False
        self.service._store.set(flag)
        
        # Feature is now disabled for all users
        for i in range(10):
            self.assertFalse(self.service.is_enabled("critical-feature", f"user_{i}"))


if __name__ == '__main__':
    # Student info display
    print("=" * 60)
    print("DevOps Lab 3 - Feature Flags Tests")
    print("Student: Kartik Kumar | Roll: 2301730205")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureFlagStore))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureFlagService))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureFlagIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTotal Tests: {result.testsRun}")
    print(f"Passed     : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed     : {len(result.failures)}")
    print(f"Errors     : {len(result.errors)}")
    
    sys.exit(0 if result.wasSuccessful() else 1)

