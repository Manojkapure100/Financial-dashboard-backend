"""
Helper utilities
"""

from datetime import datetime, timedelta


def get_date_range(days: int) -> tuple:
    """Get date range for the last N days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency"""
    return f"₹{value:.{decimals}f}"
