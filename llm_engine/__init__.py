# llm_engine/__init__.py
"""
LLM Report Generation Module
Handles AI-powered forensic report generation using Groq/Llama
"""

from .report_generator import ReportGenerator

__all__ = ['ReportGenerator']

__version__ = '1.0.0'