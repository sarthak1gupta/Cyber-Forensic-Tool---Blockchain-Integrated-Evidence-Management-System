# blockchain/__init__.py
"""
Blockchain Integration Module
Handles Ethereum blockchain interactions for evidence chain of custody
"""

from .blockchain_handler import BlockchainHandler

__all__ = ['BlockchainHandler']

__version__ = '1.0.0'