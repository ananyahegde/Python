from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class TestCase:
    name: str
    module: str
    func: callable
    duration: float = 0.0
    skip_reason: Optional[str] = None

class TestResult:
    def __init__(self):
        self.passed: List[TestCase] = []
        self.failed: List[tuple[TestCase, str]] = []
        self.skipped: List[tuple[TestCase, str]] = []
        self.errors: List[tuple[TestCase, str]] = []
    
    def add_pass(self, test: TestCase):
        self.passed.append(test)
    
    def add_fail(self, test: TestCase, message: str):
        self.failed.append((test, message))
    
    def add_skip(self, test: TestCase, reason: str):
        self.skipped.append((test, reason))
    
    def add_error(self, test: TestCase, message: str):
        self.errors.append((test, message))
    
    @property
    def total(self) -> int:
        return len(self.passed) + len(self.failed) + len(self.skipped) + len(self.errors)
    
    @property
    def passed_count(self) -> int:
        return len(self.passed)
    
    @property
    def failed_count(self) -> int:
        return len(self.failed)
    
    @property
    def skipped_count(self) -> int:
        return len(self.skipped)
    
    @property
    def errors_count(self) -> int:
        return len(self.errors)
