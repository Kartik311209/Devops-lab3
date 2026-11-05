"""
DevOps Lab 3 - Feature Flags Implementation
Student: Kartik Kumar | Roll: 2301730205 | Email: kartikjangra5366@gmail.com

Implements a complete feature flag system for gradual feature rollout.
"""

import os
import json
import time
import hashlib
import logging
import threading
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class RolloutStrategy(Enum):
    ALL_USERS = "all_users"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    GRADUAL = "gradual"
    BETA = "beta"


@dataclass
class FeatureFlag:
    """Represents a feature flag configuration"""
    name: str
    enabled: bool
    description: str
    rollout_strategy: str = RolloutStrategy.ALL_USERS.value
    rollout_percentage: float = 100.0
    allowed_users: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: str = "Kartik Kumar"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FlagEvaluation:
    """Result of a feature flag evaluation"""
    flag_name: str
    user_id: str
    enabled: bool
    reason: str
    variant: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# Feature Flag Store
# =============================================================================

class FeatureFlagStore:
    """In-memory feature flag store with file persistence"""
    
    def __init__(self, storage_path: str = "flags.json"):
        self._flags: Dict[str, FeatureFlag] = {}
        self._storage_path = storage_path
        self._lock = threading.RLock()
        self._load_from_file()
    
    def _load_from_file(self):
        """Load flags from JSON file"""
        if os.path.exists(self._storage_path):
            try:
                with open(self._storage_path) as f:
                    data = json.load(f)
                    for name, flag_data in data.items():
                        self._flags[name] = FeatureFlag(**flag_data)
                logger.info(f"Loaded {len(self._flags)} flags from {self._storage_path}")
            except Exception as e:
                logger.error(f"Failed to load flags: {e}")
    
    def _save_to_file(self):
        """Persist flags to JSON file"""
        try:
            with open(self._storage_path, 'w') as f:
                json.dump(
                    {name: flag.to_dict() for name, flag in self._flags.items()},
                    f, indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save flags: {e}")
    
    def get(self, name: str) -> Optional[FeatureFlag]:
        with self._lock:
            return self._flags.get(name)
    
    def set(self, flag: FeatureFlag):
        with self._lock:
            flag.updated_at = datetime.utcnow().isoformat()
            self._flags[flag.name] = flag
            self._save_to_file()
            logger.info(f"Flag '{flag.name}' set to enabled={flag.enabled}")
    
    def delete(self, name: str) -> bool:
        with self._lock:
            if name in self._flags:
                del self._flags[name]
                self._save_to_file()
                return True
            return False
    
    def list_all(self) -> List[FeatureFlag]:
        with self._lock:
            return list(self._flags.values())


# =============================================================================
# Feature Flag Service
# =============================================================================

class FeatureFlagService:
    """
    Core feature flag evaluation engine.
    
    Supports multiple rollout strategies:
    - all_users: Feature enabled for everyone
    - percentage: Gradual rollout by percentage
    - user_list: Enable only for specific users
    - gradual: Time-based gradual rollout
    - beta: Beta tester program
    """
    
    STUDENT_INFO = {
        "name": "Kartik Kumar",
        "roll": "2301730205",
        "email": "kartikjangra5366@gmail.com"
    }
    
    def __init__(self, store: Optional[FeatureFlagStore] = None):
        self._store = store or FeatureFlagStore()
        self._evaluation_callbacks: List[Callable] = []
        self._stats: Dict[str, Dict] = {}
    
    def _get_user_bucket(self, flag_name: str, user_id: str) -> float:
        """Deterministically assign user to a 0-100 bucket using hash"""
        combined = f"{flag_name}:{user_id}"
        hash_int = int(hashlib.md5(combined.encode()).hexdigest(), 16)
        return (hash_int % 10000) / 100.0  # 0.00 - 99.99
    
    def is_enabled(self, flag_name: str, user_id: str = "anonymous", 
                   context: Optional[dict] = None) -> bool:
        """Evaluate whether a feature is enabled for a user"""
        evaluation = self.evaluate(flag_name, user_id, context)
        return evaluation.enabled
    
    def evaluate(self, flag_name: str, user_id: str = "anonymous",
                 context: Optional[dict] = None) -> FlagEvaluation:
        """Full feature flag evaluation with reason"""
        flag = self._store.get(flag_name)
        
        if not flag:
            result = FlagEvaluation(
                flag_name=flag_name,
                user_id=user_id,
                enabled=False,
                reason="FLAG_NOT_FOUND"
            )
            self._record_evaluation(result)
            return result
        
        if not flag.enabled:
            result = FlagEvaluation(
                flag_name=flag_name,
                user_id=user_id,
                enabled=False,
                reason="FLAG_DISABLED"
            )
            self._record_evaluation(result)
            return result
        
        # Evaluate based on rollout strategy
        strategy = flag.rollout_strategy
        
        if strategy == RolloutStrategy.ALL_USERS.value:
            enabled, reason = True, "ALL_USERS"
        
        elif strategy == RolloutStrategy.PERCENTAGE.value:
            bucket = self._get_user_bucket(flag_name, user_id)
            enabled = bucket < flag.rollout_percentage
            reason = f"PERCENTAGE_{flag.rollout_percentage}%_BUCKET_{bucket:.2f}"
        
        elif strategy == RolloutStrategy.USER_LIST.value:
            enabled = user_id in flag.allowed_users
            reason = "USER_ALLOWLIST" if enabled else "NOT_IN_ALLOWLIST"
        
        elif strategy == RolloutStrategy.BETA.value:
            beta_users = flag.metadata.get("beta_users", [])
            enabled = user_id in beta_users
            reason = "BETA_USER" if enabled else "NOT_BETA_USER"
        
        else:
            enabled, reason = False, "UNKNOWN_STRATEGY"
        
        result = FlagEvaluation(
            flag_name=flag_name,
            user_id=user_id,
            enabled=enabled,
            reason=reason,
            metadata=flag.metadata
        )
        
        self._record_evaluation(result)
        return result
    
    def _record_evaluation(self, evaluation: FlagEvaluation):
        """Record evaluation for analytics"""
        name = evaluation.flag_name
        if name not in self._stats:
            self._stats[name] = {"total": 0, "enabled": 0, "disabled": 0}
        self._stats[name]["total"] += 1
        if evaluation.enabled:
            self._stats[name]["enabled"] += 1
        else:
            self._stats[name]["disabled"] += 1
    
    def create_flag(self, name: str, enabled: bool, description: str,
                    strategy: str = "all_users", percentage: float = 100.0,
                    users: Optional[List[str]] = None, metadata: Optional[dict] = None) -> FeatureFlag:
        """Create a new feature flag"""
        flag = FeatureFlag(
            name=name,
            enabled=enabled,
            description=description,
            rollout_strategy=strategy,
            rollout_percentage=percentage,
            allowed_users=users or [],
            metadata=metadata or {},
            created_by="Kartik Kumar"
        )
        self._store.set(flag)
        logger.info(f"Created flag: {name} (enabled={enabled}, strategy={strategy})")
        return flag
    
    def toggle_flag(self, name: str) -> Optional[FeatureFlag]:
        """Toggle a feature flag on/off"""
        flag = self._store.get(name)
        if flag:
            flag.enabled = not flag.enabled
            self._store.set(flag)
            logger.info(f"Toggled flag '{name}' to {flag.enabled}")
        return flag
    
    def set_rollout_percentage(self, name: str, percentage: float) -> Optional[FeatureFlag]:
        """Update rollout percentage for gradual rollout"""
        flag = self._store.get(name)
        if flag:
            flag.rollout_percentage = max(0.0, min(100.0, percentage))
            flag.rollout_strategy = RolloutStrategy.PERCENTAGE.value
            self._store.set(flag)
        return flag
    
    def get_stats(self) -> dict:
        """Get evaluation statistics"""
        return {
            "student": self.STUDENT_INFO,
            "flags": self._stats,
            "total_flags": len(self._store.list_all()),
            "active_flags": sum(1 for f in self._store.list_all() if f.enabled)
        }
    
    def list_flags(self) -> List[dict]:
        """List all flags with their current state"""
        return [f.to_dict() for f in self._store.list_all()]


# =============================================================================
# Feature Flag REST API
# =============================================================================

class FeatureFlagAPI:
    """Simple HTTP API for feature flag management"""
    
    def __init__(self, service: FeatureFlagService, port: int = 8090):
        self.service = service
        self.port = port
    
    def handle_request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        """Route HTTP requests to handlers"""
        
        if method == 'GET' and path == '/flags':
            return {"flags": self.service.list_flags(), "status": "ok"}
        
        elif method == 'GET' and path.startswith('/flags/'):
            flag_name = path.split('/flags/')[1]
            flag = self.service._store.get(flag_name)
            if flag:
                return flag.to_dict()
            return {"error": "Flag not found", "name": flag_name}
        
        elif method == 'POST' and path == '/flags':
            if not body:
                return {"error": "Request body required"}
            flag = self.service.create_flag(
                name=body['name'],
                enabled=body.get('enabled', False),
                description=body.get('description', ''),
                strategy=body.get('strategy', 'all_users'),
                percentage=body.get('percentage', 100.0),
                users=body.get('users', []),
                metadata=body.get('metadata', {})
            )
            return flag.to_dict()
        
        elif method == 'GET' and path.startswith('/evaluate/'):
            parts = path.split('/')
            flag_name = parts[2] if len(parts) > 2 else ''
            user_id = parts[3] if len(parts) > 3 else 'anonymous'
            evaluation = self.service.evaluate(flag_name, user_id)
            return {
                "flag": evaluation.flag_name,
                "user": evaluation.user_id,
                "enabled": evaluation.enabled,
                "reason": evaluation.reason
            }
        
        elif method == 'GET' and path == '/stats':
            return self.service.get_stats()
        
        return {"error": "Not found", "path": path}


# =============================================================================
# Demo & Testing
# =============================================================================

def run_demo():
    """Demonstrate the feature flag system"""
    print("=" * 60)
    print("DevOps Lab 3 - Feature Flags Demo")
    print("Student: Kartik Kumar | Roll: 2301730205")
    print("=" * 60)
    
    # Initialize service
    service = FeatureFlagService(FeatureFlagStore("demo_flags.json"))
    
    # Create feature flags
    print("\n1. Creating feature flags...")
    
    service.create_flag(
        name="new-ui-redesign",
        enabled=True,
        description="New UI redesign with modern components",
        strategy="percentage",
        percentage=25.0,
        metadata={"version": "2.0", "designer": "Kartik Kumar"}
    )
    
    service.create_flag(
        name="ai-recommendations",
        enabled=True,
        description="AI-powered product recommendations",
        strategy="all_users",
        metadata={"model": "GPT-4", "enabled_by": "Kartik Kumar"}
    )
    
    service.create_flag(
        name="beta-checkout",
        enabled=True,
        description="Beta checkout flow for selected users",
        strategy="user_list",
        users=["user_kartik", "user_beta1", "user_beta2"],
        metadata={"beta_start": "2024-01-01"}
    )
    
    service.create_flag(
        name="dark-mode",
        enabled=False,
        description="Dark mode theme (disabled)",
        strategy="all_users"
    )
    
    print(f"  Created {len(service.list_flags())} flags")
    
    # Test evaluations
    print("\n2. Evaluating feature flags for different users...")
    
    test_users = ["user_kartik", "user_alice", "user_bob", "user_charlie", "user_beta1"]
    test_flags = ["new-ui-redesign", "ai-recommendations", "beta-checkout", "dark-mode"]
    
    print(f"\n{'User':<15} {'Flag':<25} {'Enabled':<10} {'Reason'}")
    print("-" * 70)
    
    for user in test_users:
        for flag in test_flags:
            eval_result = service.evaluate(flag, user)
            status = "✓ YES" if eval_result.enabled else "✗ NO"
            print(f"  {user:<15} {flag:<25} {status:<10} {eval_result.reason}")
    
    # Gradual rollout demo
    print("\n3. Gradual rollout simulation (new-ui-redesign)...")
    
    for pct in [0, 10, 25, 50, 75, 100]:
        service.set_rollout_percentage("new-ui-redesign", pct)
        users = [f"user_{i}" for i in range(100)]
        enabled_count = sum(1 for u in users if service.is_enabled("new-ui-redesign", u))
        print(f"  Rollout {pct:3d}%: {enabled_count}/100 users get feature")
    
    # Statistics
    print("\n4. Feature flag statistics:")
    stats = service.get_stats()
    print(f"  Student     : {stats['student']['name']} ({stats['student']['roll']})")
    print(f"  Total flags : {stats['total_flags']}")
    print(f"  Active flags: {stats['active_flags']}")
    
    print("\n5. Toggle dark-mode flag...")
    service.toggle_flag("dark-mode")
    dm = service._store.get("dark-mode")
    print(f"  dark-mode is now: {'enabled' if dm.enabled else 'disabled'}")
    
    print("\n✓ Feature flags demo completed!")
    
    # Cleanup
    if os.path.exists("demo_flags.json"):
        os.remove("demo_flags.json")


if __name__ == '__main__':
    run_demo()

