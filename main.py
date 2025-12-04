"""
Command-line interface for Expense Tracker application.
Provides interactive menu-based interface for all features.
"""

import sys
from datetime import datetime
from typing import Optional

from database import init_db
from services import ExpenseTrackerService
from models import User
from utils import (
    print_success, print_error, print_warning, print_info, print_table,
    format_currency, validate_email, validate_positive_number,
    get_month_name, parse_date, get_current_month_year,
    clear_screen, confirm_action
)


class ExpenseTrackerCLI:
    """
    Command-line interface for the Expense Tracker application.
    Provides interactive menus for all application features.
    """
    
    def __init__(self):
        """Initialize CLI with service layer."""
        self.service = ExpenseTrackerService()
        self.current_user: Optional[User] = None
    
    def run(self):
        """Main application loop."""
        print_info("Welcome to Expense Tracker!")
        print_info("Initializing database...")
        
        try:
            init_db()
            self.service.initialize_default_categories()
        except Exception as e:
            print_error(f"Failed to initialize database: {str(e)}")
            return
        
        while True:
            if self.current_user:
                self.main_menu()
            else:
                self.login_menu()
    
    # ==================== Login Menu ====================
    
    def login_menu(self):
        """Display login/registration menu."""
        print("\n" + "="*50)
        print("LOGIN / REGISTER")
        print("="*50)
        print("1. Login")
        print("2. Register new user")
        print("3. List all users")
        print("4. Exit")
        print("="*50)
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.login()
        elif choice == '2':
            self.register()
        elif choice == '3':
            self.list_users()
        elif choice == '4':
            print_info("Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid choice!")
    
    def login(self):
        """Handle user login."""
        username = input("Enter username: ").strip()
        user = self.service.get_user_by_username(username)
        
        if user:
            self.current_user = user
            print_success(f"Welcome back, {user.username}!")
        else:
            print_error("User not found!")
    
    def register(self):
        """Handle new user registration."""
        print("\n--- Register New User ---")
        username = input("Enter username: ").strip()
        
        if not username:
            print_error("Username cannot be empty!")
            return
        
        email = input("Enter email: ").strip()
        
        if not validate_email(email):
            print_error("Invalid email format!")
            return
        
        user = self.service.create_user(username, email)
        if user:
            self.current_user = user
    
    def list_users(self):
        """Display all registered users."""
        users = self.service.list_all_users()
        
        if not users:
            print_info("No users registered yet.")
            return
        
        user_data = [
            {
                'ID': user.id,
                'Username': user.username,
                'Email': user.email,
                'Joined': user.created_at.strftime('%Y-%m-%d')
            }
            for user in users
        ]
        
        print_table(user_data)
    
    # ==================== Main Menu ====================
    
    def main_menu(self):
        """Display main application menu."""
        print("\n" + "="*50)
        print(f"EXPENSE TRACKER - {self.current_user.username}")
        print("="*50)
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Manage Budgets")
        print("4. View Reports")
        print("5. Manage Alerts")
        print("6. Group Expenses (Splitwise)")
        print("7. Categories")
        print("8. Logout")
        print("9. Exit")
        print("="*50)
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.add_expense_menu()
        elif choice == '2':
            self.view_expenses_menu()
        elif choice == '3':
            self.budget_menu()
        elif choice == '4':
            self.reports_menu()
        elif choice == '5':
            self.alerts_menu()
        elif choice == '6':
            self.group_menu()
        elif choice == '7':
            self.categories_menu()
        elif choice == '8':
            self.current_user = None
            print_info("Logged out successfully!")
        elif choice == '9':
            print_info("Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid choice!")
    
    # ==================== Expense Management ====================
    
    def add_expense_menu(self):
        """Menu for adding new expense."""
        print("\n--- Add New Expense ---")
        
        # Show categories
        categories = self.service.list_all_categories()
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.name}")
        
        cat_choice = input("\nEnter category number: ").strip()
        
        try:
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(categories):
                print_error("Invalid category!")
                return
            
            category = categories[cat_index]
        except ValueError:
            print_error("Invalid input!")
            return
        
        amount_str = input("Enter amount: ").strip()
        
        try:
            amount = validate_positive_number(amount_str, "Amount")
        except ValueError as e:
            print_error(str(e))
            return
        
        description = input("Enter description (optional): ").strip()
        
        date_str = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
        date = None
        
        if date_str:
            try:
                date = parse_date(date_str)
            except ValueError as e:
                print_error(str(e))
                return
        
        self.service.add_expense(
            self.current_user.id,
            category.name,
            amount,
            description,
            date
        )
    
    def view_expenses_menu(self):
        """Menu for viewing expenses."""
        print("\n--- View Expenses ---")
        print("1. View all expenses")
        print("2. View expenses for specific month")
        print("3. View expenses by category")
        print("4. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            expenses = self.service.get_user_expenses(self.current_user.id)
            self.display_expenses(expenses)
        
        elif choice == '2':
            month_str = input("Enter month (1-12): ").strip()
            year_str = input("Enter year (e.g., 2024): ").strip()
            
            try:
                month = int(month_str)
                year = int(year_str)
                
                if month < 1 or month > 12:
                    print_error("Invalid month!")
                    return
                
                expenses = self.service.get_user_expenses(
                    self.current_user.id, month, year
                )
                self.display_expenses(expenses, f"{get_month_name(month)} {year}")
            
            except ValueError:
                print_error("Invalid input!")
        
        elif choice == '3':
            categories = self.service.list_all_categories()
            print("\nAvailable categories:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat.name}")
            
            cat_choice = input("\nEnter category number: ").strip()
            
            try:
                cat_index = int(cat_choice) - 1
                if cat_index < 0 or cat_index >= len(categories):
                    print_error("Invalid category!")
                    return
                
                category = categories[cat_index]
                expenses = self.service.get_user_expenses(
                    self.current_user.id, category_name=category.name
                )
                self.display_expenses(expenses, f"Category: {category.name}")
            
            except ValueError:
                print_error("Invalid input!")
    
    def display_expenses(self, expenses, title="Expenses"):
        """Display expenses in table format."""
        if not expenses:
            print_info("No expenses found.")
            return
        
        print(f"\n--- {title} ---")
        
        expense_data = [
            {
                'Date': exp.date.strftime('%Y-%m-%d'),
                'Category': exp.category.name,
                'Amount': format_currency(exp.amount),
                'Description': exp.description[:30] if exp.description else '-'
            }
            for exp in expenses
        ]
        
        print_table(expense_data)
        
        total = sum(exp.amount for exp in expenses)
        print(f"\nTotal: {format_currency(total)}")
    
    # ==================== Budget Management ====================
    
    def budget_menu(self):
        """Menu for budget management."""
        print("\n--- Budget Management ---")
        print("1. Set budget for category")
        print("2. View current budgets")
        print("3. View budget for specific month")
        print("4. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.set_budget_menu()
        elif choice == '2':
            month, year = get_current_month_year()
            self.view_budgets(month, year)
        elif choice == '3':
            month_str = input("Enter month (1-12): ").strip()
            year_str = input("Enter year: ").strip()
            
            try:
                month = int(month_str)
                year = int(year_str)
                
                if month < 1 or month > 12:
                    print_error("Invalid month!")
                    return
                
                self.view_budgets(month, year)
            
            except ValueError:
                print_error("Invalid input!")
    
    def set_budget_menu(self):
        """Set budget for a category."""
        print("\n--- Set Budget ---")
        
        categories = self.service.list_all_categories()
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.name}")
        
        cat_choice = input("\nEnter category number: ").strip()
        
        try:
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(categories):
                print_error("Invalid category!")
                return
            
            category = categories[cat_index]
        except ValueError:
            print_error("Invalid input!")
            return
        
        amount_str = input("Enter budget amount: ").strip()
        
        try:
            amount = validate_positive_number(amount_str, "Budget amount")
        except ValueError as e:
            print_error(str(e))
            return
        
        use_current = input("Set for current month? (y/n): ").strip().lower()
        
        if use_current == 'y':
            month, year = get_current_month_year()
        else:
            month_str = input("Enter month (1-12): ").strip()
            year_str = input("Enter year: ").strip()
            
            try:
                month = int(month_str)
                year = int(year_str)
                
                if month < 1 or month > 12:
                    print_error("Invalid month!")
                    return
            except ValueError:
                print_error("Invalid input!")
                return
        
        self.service.set_budget(
            self.current_user.id,
            category.name,
            amount,
            month,
            year
        )
    
    def view_budgets(self, month: int, year: int):
        """View budgets for a specific month."""
        budgets = self.service.get_user_budgets(self.current_user.id, month, year)
        
        if not budgets:
            print_info(f"No budgets set for {get_month_name(month)} {year}.")
            return
        
        print(f"\n--- Budgets for {get_month_name(month)} {year} ---")
        
        budget_data = [
            {
                'Category': budget.category.name,
                'Budget': format_currency(budget.amount)
            }
            for budget in budgets
        ]
        
        print_table(budget_data)
    
    # ==================== Reports ====================
    
    def reports_menu(self):
        """Menu for viewing reports."""
        print("\n--- Reports ---")
        print("1. Monthly summary")
        print("2. Budget vs Spending comparison")
        print("3. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1' or choice == '2':
            use_current = input("Use current month? (y/n): ").strip().lower()
            
            if use_current == 'y':
                month, year = get_current_month_year()
            else:
                month_str = input("Enter month (1-12): ").strip()
                year_str = input("Enter year: ").strip()
                
                try:
                    month = int(month_str)
                    year = int(year_str)
                    
                    if month < 1 or month > 12:
                        print_error("Invalid month!")
                        return
                except ValueError:
                    print_error("Invalid input!")
                    return
            
            report = self.service.get_monthly_report(self.current_user.id, month, year)
            
            if choice == '1':
                self.display_monthly_summary(report)
            else:
                self.display_budget_comparison(report)
    
    def display_monthly_summary(self, report):
        """Display monthly spending summary."""
        print(f"\n--- Monthly Summary: {get_month_name(report['month'])} {report['year']} ---")
        print(f"\nTotal Spending: {format_currency(report['total_spent'])}")
        
        if report['category_spending']:
            print("\nSpending by Category:")
            
            cat_data = [
                {
                    'Category': item['category'],
                    'Amount': format_currency(item['amount']),
                    'Percentage': f"{(item['amount'] / report['total_spent'] * 100):.1f}%"
                }
                for item in report['category_spending']
            ]
            
            print_table(cat_data)
        else:
            print_info("No expenses recorded for this month.")
    
    def display_budget_comparison(self, report):
        """Display budget vs spending comparison."""
        print(f"\n--- Budget Comparison: {get_month_name(report['month'])} {report['year']} ---")
        
        if not report['budget_comparison']:
            print_info("No budgets set for this month.")
            return
        
        comparison_data = []
        
        for item in report['budget_comparison']:
            status = '✓' if item['remaining'] >= 0 else '✗'
            
            comparison_data.append({
                'Category': item['category'],
                'Budget': format_currency(item['budget']),
                'Spent': format_currency(item['spent']),
                'Remaining': format_currency(item['remaining']),
                'Used %': f"{item['percentage_used']:.1f}%",
                'Status': status
            })
        
        print_table(comparison_data)
    
    # ==================== Alerts Management ====================
    
    def alerts_menu(self):
        """Menu for managing alerts."""
        print("\n--- Alert Management ---")
        print("1. Set custom alert threshold")
        print("2. Set category-specific alert")
        print("3. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.set_general_alert()
        elif choice == '2':
            self.set_category_alert()
    
    def set_general_alert(self):
        """Set general alert for all categories."""
        print("\n--- Set General Alert ---")
        
        threshold_str = input("Enter alert threshold percentage (e.g., 10 for 10% remaining): ").strip()
        
        try:
            threshold = int(threshold_str)
            
            if threshold < 0 or threshold > 100:
                print_error("Threshold must be between 0 and 100!")
                return
        except ValueError:
            print_error("Invalid input!")
            return
        
        email_notif = input("Enable email notifications? (y/n): ").strip().lower() == 'y'
        
        self.service.set_custom_alert(
            self.current_user.id,
            None,
            threshold,
            email_notif
        )
    
    def set_category_alert(self):
        """Set alert for specific category."""
        print("\n--- Set Category-Specific Alert ---")
        
        categories = self.service.list_all_categories()
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.name}")
        
        cat_choice = input("\nEnter category number: ").strip()
        
        try:
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(categories):
                print_error("Invalid category!")
                return
            
            category = categories[cat_index]
        except ValueError:
            print_error("Invalid input!")
            return
        
        threshold_str = input("Enter alert threshold percentage: ").strip()
        
        try:
            threshold = int(threshold_str)
            
            if threshold < 0 or threshold > 100:
                print_error("Threshold must be between 0 and 100!")
                return
        except ValueError:
            print_error("Invalid input!")
            return
        
        email_notif = input("Enable email notifications? (y/n): ").strip().lower() == 'y'
        
        self.service.set_custom_alert(
            self.current_user.id,
            category.name,
            threshold,
            email_notif
        )
    
    # ==================== Group Expenses ====================
    
    def group_menu(self):
        """Menu for group expense sharing."""
        print("\n--- Group Expenses (Splitwise) ---")
        print("1. Create new group")
        print("2. Add shared expense")
        print("3. View group balances")
        print("4. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.create_group_menu()
        elif choice == '2':
            self.add_shared_expense_menu()
        elif choice == '3':
            self.view_group_balances_menu()
    
    def create_group_menu(self):
        """Create a new expense-sharing group."""
        print("\n--- Create New Group ---")
        
        name = input("Enter group name: ").strip()
        description = input("Enter description: ").strip()
        
        # Show available users
        users = self.service.list_all_users()
        print("\nAvailable users:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.username} ({user.email})")
        
        member_input = input("\nEnter member numbers (comma-separated, e.g., 1,2): ").strip()
        
        try:
            member_ids = []
            inputs = [x.strip() for x in member_input.split(',')]
            
            for inp in inputs:
                # Try to parse as number first
                try:
                    idx = int(inp) - 1
                    if idx < 0 or idx >= len(users):
                        print_error(f"Invalid user number: {inp}")
                        return
                    member_ids.append(users[idx].id)
                except ValueError:
                    # Try as username
                    user = next((u for u in users if u.username == inp), None)
                    if user:
                        member_ids.append(user.id)
                    else:
                        print_error(f"User not found: {inp}")
                        return
            
            if not member_ids:
                print_error("No valid members selected!")
                return
            
            # Add current user if not included
            if self.current_user.id not in member_ids:
                member_ids.append(self.current_user.id)
            
            self.service.create_group(name, description, self.current_user.id, member_ids)
        
        except Exception as e:
            print_error(f"Error creating group: {str(e)}")
    
    def add_shared_expense_menu(self):
        """Add a shared expense to a group."""
        print("\n--- Add Shared Expense ---")
        
        # Get user's groups
        from database import get_session
        from models import Group
        
        with get_session() as session:
            groups = session.query(Group).join(
                Group.members
            ).filter(User.id == self.current_user.id).all()
            
            if not groups:
                print_info("You are not a member of any groups. Create one first!")
                return
            
            print("\nYour groups:")
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group.name} ({len(group.members)} members)")
            
            group_choice = input("\nEnter group number: ").strip()
            
            try:
                group_index = int(group_choice) - 1
                if group_index < 0 or group_index >= len(groups):
                    print_error("Invalid group!")
                    return
                
                group = groups[group_index]
            except ValueError:
                print_error("Invalid input!")
                return
        
        # Get category
        categories = self.service.list_all_categories()
        print("\nAvailable categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat.name}")
        
        cat_choice = input("\nEnter category number: ").strip()
        
        try:
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(categories):
                print_error("Invalid category!")
                return
            
            category = categories[cat_index]
        except ValueError:
            print_error("Invalid input!")
            return
        
        # Get amount
        amount_str = input("Enter total amount: ").strip()
        
        try:
            amount = validate_positive_number(amount_str, "Amount")
        except ValueError as e:
            print_error(str(e))
            return
        
        description = input("Enter description: ").strip()
        
        split_choice = input("Split equally? (y/n): ").strip().lower()
        split_equally = split_choice == 'y'
        
        self.service.add_shared_expense(
            self.current_user.id,
            group.id,
            category.name,
            amount,
            description,
            split_equally
        )
    
    def view_group_balances_menu(self):
        """View balances for a group."""
        print("\n--- View Group Balances ---")
        
        from database import get_session
        from models import Group
        
        with get_session() as session:
            groups = session.query(Group).join(
                Group.members
            ).filter(User.id == self.current_user.id).all()
            
            if not groups:
                print_info("You are not a member of any groups.")
                return
            
            print("\nYour groups:")
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group.name}")
            
            group_choice = input("\nEnter group number: ").strip()
            
            try:
                group_index = int(group_choice) - 1
                if group_index < 0 or group_index >= len(groups):
                    print_error("Invalid group!")
                    return
                
                group = groups[group_index]
                group_id = group.id
                group_name = group.name
            except ValueError:
                print_error("Invalid input!")
                return
        
        balances = self.service.get_group_balances(group_id)
        
        print(f"\n--- Balances for {group_name} ---")
        
        balance_data = [
            {
                'Member': bal['username'],
                'Total Paid': format_currency(bal['total_paid']),
                'Total Owed': format_currency(bal['total_owed']),
                'Net Balance': format_currency(bal['net_balance']),
                'Status': 'Gets back' if bal['net_balance'] > 0 else 'Owes' if bal['net_balance'] < 0 else 'Settled'
            }
            for bal in balances
        ]
        
        print_table(balance_data)
    
    # ==================== Category Management ====================
    
    def categories_menu(self):
        """Menu for category management."""
        print("\n--- Categories ---")
        print("1. View all categories")
        print("2. Add new category")
        print("3. Back")
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            self.view_categories()
        elif choice == '2':
            self.add_category()
    
    def view_categories(self):
        """Display all categories."""
        categories = self.service.list_all_categories()
        
        print("\n--- All Categories ---")
        
        cat_data = [
            {
                'ID': cat.id,
                'Name': cat.name,
                'Description': cat.description or '-'
            }
            for cat in categories
        ]
        
        print_table(cat_data)
    
    def add_category(self):
        """Add a new category."""
        print("\n--- Add New Category ---")
        
        name = input("Enter category name: ").strip()
        description = input("Enter description (optional): ").strip()
        
        if not name:
            print_error("Category name cannot be empty!")
            return
        
        self.service.create_category(name, description)


def main():
    """Main entry point for the application."""
    try:
        cli = ExpenseTrackerCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n")
        print_info("Application terminated by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
