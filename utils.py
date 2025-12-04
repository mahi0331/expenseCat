"""
Utility functions for the Expense Tracker application.
Provides helper functions for formatting, validation, and common operations.
"""

from datetime import datetime
from typing import List, Dict, Any
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_success(message: str):
    """
    Print success message in green color.
    
    Args:
        message: Success message to display
    """
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """
    Print error message in red color.
    
    Args:
        message: Error message to display
    """
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """
    Print warning message in yellow color.
    
    Args:
        message: Warning message to display
    """
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """
    Print info message in blue color.
    
    Args:
        message: Info message to display
    """
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_table(data: List[Dict[str, Any]], headers: List[str] = None):
    """
    Print data in a formatted table.
    
    Args:
        data: List of dictionaries containing table data
        headers: Optional list of header names
    """
    if not data:
        print_info("No data to display.")
        return
    
    if headers is None:
        headers = list(data[0].keys())
    
    table_data = [[row.get(h, '') for h in headers] for row in data]
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount to format
    
    Returns:
        Formatted currency string
    """
    return f"₹{amount:,.2f}"


def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email format is valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_positive_number(value: str, field_name: str = "Value") -> float:
    """
    Validate and convert string to positive float.
    
    Args:
        value: String value to validate
        field_name: Name of the field for error messages
    
    Returns:
        Float value if valid
    
    Raises:
        ValueError: If value is not a positive number
    """
    try:
        num = float(value)
        if num <= 0:
            raise ValueError(f"{field_name} must be a positive number.")
        return num
    except ValueError:
        raise ValueError(f"{field_name} must be a valid positive number.")


def get_month_name(month: int) -> str:
    """
    Get month name from month number.
    
    Args:
        month: Month number (1-12)
    
    Returns:
        Month name
    """
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    return months[month - 1] if 1 <= month <= 12 else 'Invalid'


def parse_date(date_str: str) -> datetime:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string to parse
    
    Returns:
        datetime object
    
    Raises:
        ValueError: If date format is invalid
    """
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError("Invalid date format. Use YYYY-MM-DD, DD/MM/YYYY, or MM/DD/YYYY.")


def get_current_month_year() -> tuple:
    """
    Get current month and year.
    
    Returns:
        Tuple of (month, year)
    """
    now = datetime.now()
    return now.month, now.year


def clear_screen():
    """
    Clear the terminal screen (cross-platform).
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def confirm_action(message: str) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
    
    Returns:
        True if user confirms, False otherwise
    """
    response = input(f"{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


def truncate_string(text: str, max_length: int = 50) -> str:
    """
    Truncate string to maximum length with ellipsis.
    
    Args:
        text: String to truncate
        max_length: Maximum length
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
