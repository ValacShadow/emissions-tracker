from datetime import datetime
from fastapi import HTTPException


def safe_str_to_datetime(date_str: str):
    """Convert string to datetime object, return None if invalid."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None  # Invalid date format


def validate_date_range(start_date: str, end_date: str):
    """Validate if start_date is earlier than end_date and both are valid."""
    start_dt = safe_str_to_datetime(start_date)
    end_dt = safe_str_to_datetime(end_date)

    # Check if start_date or end_date is invalid
    if not start_dt:
        raise HTTPException(status_code=400, detail="Invalid start_date format. Please use YYYY-MM-DD.")
    
    if not end_dt:
        raise HTTPException(status_code=400, detail="Invalid end_date format. Please use YYYY-MM-DD.")

    # Check if start_date is earlier than end_date
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start_date cannot be later than end_date.")
    
    return start_dt, end_dt
