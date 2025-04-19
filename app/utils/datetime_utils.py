"""Utility functions for datetime operations."""
import datetime


def utcnow():
    """
    Return the current UTC datetime with timezone information.
    
    This is a replacement for datetime.utcnow() which is deprecated.
    """
    return datetime.datetime.now(datetime.UTC)