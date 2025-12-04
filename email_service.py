"""
Email notification service for sending budget alerts.
Handles SMTP connection and email composition.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from config import Config
from utils import print_success, print_error, format_currency


class EmailService:
    """
    Service class for sending email notifications.
    Uses SMTP to send budget alerts and warnings to users.
    """
    
    def __init__(self):
        """Initialize email service with configuration."""
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.from_email = Config.EMAIL_FROM
        self.is_configured = Config.is_email_configured()
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML supported)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured:
            print_error("Email is not configured. Please set up SMTP settings in .env file.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print_error(f"Failed to send email: {str(e)}")
            return False
    
    def send_budget_alert(self, user_email: str, username: str, 
                         category_name: str, spent: float, 
                         budget: float, percentage_left: float) -> bool:
        """
        Send budget alert notification to user.
        
        Args:
            user_email: User's email address
            username: User's name
            category_name: Budget category name
            spent: Amount spent
            budget: Budget amount
            percentage_left: Percentage of budget remaining
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"⚠️ Budget Alert: {category_name}"
        
        body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ padding: 20px; background-color: #f5f5f5; }}
                    .alert-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                    .stats {{ background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .warning {{ color: #856404; }}
                    .amount {{ font-size: 18px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Budget Alert Notification</h2>
                    <p>Hello {username},</p>
                    
                    <div class="alert-box">
                        <p class="warning">
                            <strong>Warning:</strong> You have only {percentage_left:.1f}% of your budget remaining!
                        </p>
                    </div>
                    
                    <div class="stats">
                        <h3>Budget Summary for {category_name}</h3>
                        <p><strong>Budget:</strong> <span class="amount">{format_currency(budget)}</span></p>
                        <p><strong>Spent:</strong> <span class="amount">{format_currency(spent)}</span></p>
                        <p><strong>Remaining:</strong> <span class="amount">{format_currency(budget - spent)}</span></p>
                        <p><strong>Percentage Used:</strong> {100 - percentage_left:.1f}%</p>
                    </div>
                    
                    <p>Consider reviewing your expenses to stay within your budget.</p>
                    
                    <p>Best regards,<br>Expense Tracker Team</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_budget_exceeded_alert(self, user_email: str, username: str,
                                   category_name: str, spent: float,
                                   budget: float, overspent: float) -> bool:
        """
        Send alert when budget is exceeded.
        
        Args:
            user_email: User's email address
            username: User's name
            category_name: Budget category name
            spent: Amount spent
            budget: Budget amount
            overspent: Amount over budget
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"🚨 Budget Exceeded: {category_name}"
        
        body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ padding: 20px; background-color: #f5f5f5; }}
                    .alert-box {{ background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; }}
                    .stats {{ background-color: white; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .danger {{ color: #721c24; }}
                    .amount {{ font-size: 18px; font-weight: bold; }}
                    .overspent {{ color: #dc3545; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Budget Exceeded Alert</h2>
                    <p>Hello {username},</p>
                    
                    <div class="alert-box">
                        <p class="danger">
                            <strong>Alert:</strong> You have exceeded your budget for {category_name}!
                        </p>
                    </div>
                    
                    <div class="stats">
                        <h3>Budget Summary for {category_name}</h3>
                        <p><strong>Budget:</strong> <span class="amount">{format_currency(budget)}</span></p>
                        <p><strong>Spent:</strong> <span class="amount overspent">{format_currency(spent)}</span></p>
                        <p><strong>Over Budget:</strong> <span class="amount overspent">{format_currency(overspent)}</span></p>
                        <p><strong>Percentage Used:</strong> {(spent / budget * 100):.1f}%</p>
                    </div>
                    
                    <p>Please review your spending and adjust your budget or expenses accordingly.</p>
                    
                    <p>Best regards,<br>Expense Tracker Team</p>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body)
