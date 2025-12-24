# forensic_engine/__init__.py
"""
Forensic Engine Module
Handles all forensic analysis operations
"""

from .orchestrator import ForensicOrchestrator
from .disk_forensics import DiskForensics
from .memory_forensics import MemoryForensics
from .network_forensics import NetworkForensics
from .log_forensics import LogForensics

__all__ = [
    'ForensicOrchestrator',
    'DiskForensics',
    'MemoryForensics',
    'NetworkForensics',
    'LogForensics'
]

__version__ = '1.0.0'
