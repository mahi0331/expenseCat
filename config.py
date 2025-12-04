"""
Configuration module for Expense Tracker application.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class containing all application settings.
    Loads values from environment variables with sensible defaults.
    """
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        'DATABASE_URL', 
        'sqlite:///expense_tracker.db'  # Using SQLite for easy local testing
    )
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    
    # Alert Configuration
    DEFAULT_ALERT_THRESHOLD = int(os.getenv('DEFAULT_ALERT_THRESHOLD', '10'))
    
    # Application Settings
    DEFAULT_CATEGORIES = [
        'Food',
        'Transport',
        'Entertainment',
        'Shopping',
        'Bills',
        'Healthcare',
        'Education',
        'Other'
    ]
    
    @staticmethod
    def is_email_configured():
        """
        Check if email configuration is properly set up.
        
        Returns:
            bool: True if email is configured, False otherwise
        """
        return bool(
            Config.SMTP_USERNAME and 
            Config.SMTP_PASSWORD and 
            Config.EMAIL_FROM
        )
