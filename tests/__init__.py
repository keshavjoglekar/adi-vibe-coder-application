"""
Test Suite for AI Agent Application System

This test suite provides comprehensive coverage for all components of the
AI agent system built for the Analog Devices application.

Test Categories:
- Unit tests for individual agents
- Integration tests for complete workflows  
- Performance tests for optimization validation
- Error handling tests for robustness

Usage:
    # Run all tests
    pytest tests/ -v
    
    # Run with coverage
    pytest tests/ --cov=agents --cov=lib
    
    # Run specific test category
    pytest tests/test_agents.py -v
    pytest tests/test_integration.py -v
"""

__version__ = "1.0.0"