"""
Core service layer for Expense Tracker application.
Implements business logic for expense tracking, budgets, and reporting.
"""

from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, and_, extract
from sqlalchemy.exc import IntegrityError

from database import get_session
from models import User, Category, Expense, Budget, Group, ExpenseSplit, Alert
from email_service import EmailService
from utils import (
    print_success, print_error, print_warning, print_info,
    format_currency, get_current_month_year
)
from config import Config


class ExpenseTrackerService:
    """
    Main service class containing all business logic for the expense tracker.
    Handles user management, expenses, budgets, alerts, and reporting.
    """
    
    def __init__(self):
        """Initialize the service with email support."""
        self.email_service = EmailService()
    
    # ==================== User Management ====================
    
    def create_user(self, username: str, email: str) -> Optional[User]:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            email: User's email address
        
        Returns:
            User object if created successfully, None otherwise
        """
        try:
            with get_session() as session:
                user = User(username=username, email=email)
                session.add(user)
                session.flush()
                
                user_id = user.id
                user_username = user.username
                user_email = user.email
                user_created_at = user.created_at
                
                # Create default alert settings
                default_alert = Alert(
                    user_id=user_id,
                    threshold_percentage=Config.DEFAULT_ALERT_THRESHOLD,
                    email_notification=Config.is_email_configured()
                )
                session.add(default_alert)
                session.flush()
                
                print_success(f"User '{username}' created successfully!")
            
            # Return a detached user object with values copied
            new_user = User()
            new_user.id = user_id
            new_user.username = user_username
            new_user.email = user_email
            new_user.created_at = user_created_at
            return new_user
        
        except IntegrityError:
            print_error(f"User with username '{username}' or email '{email}' already exists.")
            return None
        except Exception as e:
            print_error(f"Error creating user: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User object if found, None otherwise
        """
        with get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                # Create a detached copy
                user_copy = User()
                user_copy.id = user.id
                user_copy.username = user.username
                user_copy.email = user.email
                user_copy.created_at = user.created_at
                return user_copy
            return None
    
    def list_all_users(self) -> List[User]:
        """
        Get list of all users.
        
        Returns:
            List of all User objects
        """
        with get_session() as session:
            users = session.query(User).all()
            # Create detached copies
            user_copies = []
            for user in users:
                user_copy = User()
                user_copy.id = user.id
                user_copy.username = user.username
                user_copy.email = user.email
                user_copy.created_at = user.created_at
                user_copies.append(user_copy)
            return user_copies
    
    # ==================== Category Management ====================
    
    def create_category(self, name: str, description: str = "") -> Optional[Category]:
        """
        Create a new expense category.
        
        Args:
            name: Category name
            description: Optional category description
        
        Returns:
            Category object if created successfully, None otherwise
        """
        try:
            with get_session() as session:
                category = Category(name=name, description=description)
                session.add(category)
                print_success(f"Category '{name}' created successfully!")
                return category
        
        except IntegrityError:
            print_error(f"Category '{name}' already exists.")
            return None
        except Exception as e:
            print_error(f"Error creating category: {str(e)}")
            return None
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Retrieve category by name.
        
        Args:
            name: Category name to search for
        
        Returns:
            Category object if found, None otherwise
        """
        with get_session() as session:
            category = session.query(Category).filter(Category.name == name).first()
            if category:
                session.expunge(category)
            return category
    
    def list_all_categories(self) -> List[Category]:
        """
        Get list of all categories.
        
        Returns:
            List of all Category objects
        """
        with get_session() as session:
            categories = session.query(Category).all()
            for cat in categories:
                session.expunge(cat)
            return categories
    
    def initialize_default_categories(self):
        """
        Create default expense categories if they don't exist.
        """
        for cat_name in Config.DEFAULT_CATEGORIES:
            existing = self.get_category_by_name(cat_name)
            if not existing:
                self.create_category(cat_name)
    
    # ==================== Expense Management ====================
    
    def add_expense(self, user_id: int, category_name: str, amount: float,
                   description: str = "", date: datetime = None) -> Optional[Expense]:
        """
        Add a new expense for a user.
        
        Args:
            user_id: User's ID
            category_name: Name of expense category
            amount: Expense amount
            description: Optional expense description
            date: Expense date (defaults to now)
        
        Returns:
            Expense object if created successfully, None otherwise
        """
        try:
            category = self.get_category_by_name(category_name)
            if not category:
                print_error(f"Category '{category_name}' not found.")
                return None
            
            if date is None:
                date = datetime.now()
            
            with get_session() as session:
                expense = Expense(
                    user_id=user_id,
                    category_id=category.id,
                    amount=amount,
                    description=description,
                    date=date
                )
                session.add(expense)
                session.flush()
                
                print_success(f"Expense of {format_currency(amount)} added to '{category_name}'!")
                
                # Check budget and send alerts if necessary
                self._check_budget_alerts(session, user_id, category.id, date.month, date.year)
                
                return expense
        
        except Exception as e:
            print_error(f"Error adding expense: {str(e)}")
            return None
    
    def get_user_expenses(self, user_id: int, month: int = None, 
                         year: int = None, category_name: str = None) -> List[Expense]:
        """
        Get expenses for a user with optional filters.
        
        Args:
            user_id: User's ID
            month: Optional month filter (1-12)
            year: Optional year filter
            category_name: Optional category filter
        
        Returns:
            List of Expense objects
        """
        with get_session() as session:
            query = session.query(Expense).join(Category).filter(Expense.user_id == user_id)
            
            if month and year:
                query = query.filter(
                    and_(
                        extract('month', Expense.date) == month,
                        extract('year', Expense.date) == year
                    )
                )
            
            if category_name:
                category = self.get_category_by_name(category_name)
                if category:
                    query = query.filter(Expense.category_id == category.id)
            
            expenses = query.order_by(Expense.date.desc()).all()
            
            # Create detached copies with eagerly loaded relationships
            expense_copies = []
            for expense in expenses:
                exp_copy = Expense()
                exp_copy.id = expense.id
                exp_copy.user_id = expense.user_id
                exp_copy.category_id = expense.category_id
                exp_copy.amount = expense.amount
                exp_copy.description = expense.description
                exp_copy.date = expense.date
                exp_copy.group_id = expense.group_id
                exp_copy.is_shared = expense.is_shared
                exp_copy.created_at = expense.created_at
                
                # Create category copy
                cat_copy = Category()
                cat_copy.id = expense.category.id
                cat_copy.name = expense.category.name
                cat_copy.description = expense.category.description
                exp_copy.category = cat_copy
                
                expense_copies.append(exp_copy)
            
            return expense_copies
    
    # ==================== Budget Management ====================
    
    def set_budget(self, user_id: int, category_name: str, amount: float,
                  month: int = None, year: int = None) -> Optional[Budget]:
        """
        Set or update budget for a category.
        
        Args:
            user_id: User's ID
            category_name: Category name
            amount: Budget amount
            month: Month (defaults to current month)
            year: Year (defaults to current year)
        
        Returns:
            Budget object if set successfully, None otherwise
        """
        try:
            category = self.get_category_by_name(category_name)
            if not category:
                print_error(f"Category '{category_name}' not found.")
                return None
            
            if month is None or year is None:
                month, year = get_current_month_year()
            
            with get_session() as session:
                # Check if budget already exists
                existing_budget = session.query(Budget).filter(
                    and_(
                        Budget.user_id == user_id,
                        Budget.category_id == category.id,
                        Budget.month == month,
                        Budget.year == year
                    )
                ).first()
                
                if existing_budget:
                    existing_budget.amount = amount
                    print_success(f"Budget for '{category_name}' updated to {format_currency(amount)}!")
                    return existing_budget
                else:
                    budget = Budget(
                        user_id=user_id,
                        category_id=category.id,
                        amount=amount,
                        month=month,
                        year=year
                    )
                    session.add(budget)
                    print_success(f"Budget for '{category_name}' set to {format_currency(amount)}!")
                    return budget
        
        except Exception as e:
            print_error(f"Error setting budget: {str(e)}")
            return None
    
    def get_user_budgets(self, user_id: int, month: int = None, 
                        year: int = None) -> List[Budget]:
        """
        Get budgets for a user.
        
        Args:
            user_id: User's ID
            month: Optional month filter
            year: Optional year filter
        
        Returns:
            List of Budget objects
        """
        with get_session() as session:
            query = session.query(Budget).join(Category).filter(Budget.user_id == user_id)
            
            if month and year:
                query = query.filter(
                    and_(Budget.month == month, Budget.year == year)
                )
            
            budgets = query.all()
            
            # Create detached copies
            budget_copies = []
            for budget in budgets:
                budget_copy = Budget()
                budget_copy.id = budget.id
                budget_copy.user_id = budget.user_id
                budget_copy.category_id = budget.category_id
                budget_copy.amount = budget.amount
                budget_copy.month = budget.month
                budget_copy.year = budget.year
                budget_copy.created_at = budget.created_at
                
                # Create category copy
                cat_copy = Category()
                cat_copy.id = budget.category.id
                cat_copy.name = budget.category.name
                cat_copy.description = budget.category.description
                budget_copy.category = cat_copy
                
                budget_copies.append(budget_copy)
            
            return budget_copies
    
    # ==================== Alert Management ====================
    
    def set_custom_alert(self, user_id: int, category_name: str = None,
                        threshold_percentage: int = 10,
                        email_notification: bool = True) -> Optional[Alert]:
        """
        Set custom alert for budget warnings.
        
        Args:
            user_id: User's ID
            category_name: Optional category name (None for all categories)
            threshold_percentage: Alert when this % of budget remains
            email_notification: Whether to send email alerts
        
        Returns:
            Alert object if created successfully, None otherwise
        """
        try:
            category_id = None
            if category_name:
                category = self.get_category_by_name(category_name)
                if not category:
                    print_error(f"Category '{category_name}' not found.")
                    return None
                category_id = category.id
            
            with get_session() as session:
                # Check if alert exists
                query = session.query(Alert).filter(Alert.user_id == user_id)
                if category_id:
                    query = query.filter(Alert.category_id == category_id)
                else:
                    query = query.filter(Alert.category_id.is_(None))
                
                existing_alert = query.first()
                
                if existing_alert:
                    existing_alert.threshold_percentage = threshold_percentage
                    existing_alert.email_notification = email_notification
                    existing_alert.is_active = True
                    print_success("Alert settings updated!")
                    return existing_alert
                else:
                    alert = Alert(
                        user_id=user_id,
                        category_id=category_id,
                        threshold_percentage=threshold_percentage,
                        email_notification=email_notification
                    )
                    session.add(alert)
                    print_success("Custom alert created!")
                    return alert
        
        except Exception as e:
            print_error(f"Error setting alert: {str(e)}")
            return None
    
    def _check_budget_alerts(self, session, user_id: int, category_id: int,
                           month: int, year: int):
        """
        Internal method to check if budget alerts should be triggered.
        
        Args:
            session: Database session
            user_id: User's ID
            category_id: Category ID
            month: Month to check
            year: Year to check
        """
        # Get budget
        budget = session.query(Budget).filter(
            and_(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.month == month,
                Budget.year == year
            )
        ).first()
        
        if not budget:
            return
        
        # Calculate total spent
        spent = session.query(func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.category_id == category_id,
                extract('month', Expense.date) == month,
                extract('year', Expense.date) == year
            )
        ).scalar() or 0
        
        # Get user and category info
        user = session.query(User).filter(User.id == user_id).first()
        category = session.query(Category).filter(Category.id == category_id).first()
        
        # Check if budget exceeded
        if spent > budget.amount:
            overspent = spent - budget.amount
            print_warning(
                f"Budget exceeded for {category.name}! "
                f"Spent: {format_currency(spent)}, Budget: {format_currency(budget.amount)}, "
                f"Over: {format_currency(overspent)}"
            )
            
            # Send email if configured
            alerts = session.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.is_active == True,
                    Alert.email_notification == True
                )
            ).filter(
                (Alert.category_id == category_id) | (Alert.category_id.is_(None))
            ).all()
            
            if alerts and self.email_service.is_configured:
                self.email_service.send_budget_exceeded_alert(
                    user.email, user.username, category.name,
                    spent, budget.amount, overspent
                )
        else:
            # Check threshold alerts
            percentage_left = ((budget.amount - spent) / budget.amount) * 100
            
            alerts = session.query(Alert).filter(
                and_(
                    Alert.user_id == user_id,
                    Alert.is_active == True
                )
            ).filter(
                (Alert.category_id == category_id) | (Alert.category_id.is_(None))
            ).all()
            
            for alert in alerts:
                if percentage_left <= alert.threshold_percentage:
                    print_warning(
                        f"Budget alert for {category.name}! "
                        f"Only {percentage_left:.1f}% remaining. "
                        f"Spent: {format_currency(spent)}, Budget: {format_currency(budget.amount)}"
                    )
                    
                    if alert.email_notification and self.email_service.is_configured:
                        self.email_service.send_budget_alert(
                            user.email, user.username, category.name,
                            spent, budget.amount, percentage_left
                        )
    
    # ==================== Reporting ====================
    
    def get_monthly_report(self, user_id: int, month: int = None, 
                          year: int = None) -> Dict:
        """
        Generate monthly spending report.
        
        Args:
            user_id: User's ID
            month: Month (defaults to current)
            year: Year (defaults to current)
        
        Returns:
            Dictionary containing report data
        """
        if month is None or year is None:
            month, year = get_current_month_year()
        
        with get_session() as session:
            # Get total spending
            total_spent = session.query(func.sum(Expense.amount)).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('month', Expense.date) == month,
                    extract('year', Expense.date) == year
                )
            ).scalar() or 0
            
            # Get spending by category
            category_spending = session.query(
                Category.name,
                func.sum(Expense.amount).label('total')
            ).join(
                Expense, Expense.category_id == Category.id
            ).filter(
                and_(
                    Expense.user_id == user_id,
                    extract('month', Expense.date) == month,
                    extract('year', Expense.date) == year
                )
            ).group_by(Category.name).all()
            
            # Get budgets
            budgets = session.query(Budget, Category.name).join(
                Category, Budget.category_id == Category.id
            ).filter(
                and_(
                    Budget.user_id == user_id,
                    Budget.month == month,
                    Budget.year == year
                )
            ).all()
            
            budget_comparison = []
            for budget, cat_name in budgets:
                spent = next((s[1] for s in category_spending if s[0] == cat_name), 0)
                budget_comparison.append({
                    'category': cat_name,
                    'budget': budget.amount,
                    'spent': spent,
                    'remaining': budget.amount - spent,
                    'percentage_used': (spent / budget.amount * 100) if budget.amount > 0 else 0
                })
            
            return {
                'month': month,
                'year': year,
                'total_spent': total_spent,
                'category_spending': [{'category': c[0], 'amount': c[1]} for c in category_spending],
                'budget_comparison': budget_comparison
            }
    
    # ==================== Group Expense Sharing ====================
    
    def create_group(self, name: str, description: str, created_by: int,
                    member_ids: List[int]) -> Optional[Group]:
        """
        Create a group for shared expenses.
        
        Args:
            name: Group name
            description: Group description
            created_by: User ID of creator
            member_ids: List of user IDs to add as members
        
        Returns:
            Group object if created successfully, None otherwise
        """
        try:
            with get_session() as session:
                group = Group(
                    name=name,
                    description=description,
                    created_by=created_by
                )
                
                # Add members
                for user_id in member_ids:
                    user = session.query(User).filter(User.id == user_id).first()
                    if user:
                        group.members.append(user)
                
                session.add(group)
                session.flush()
                print_success(f"Group '{name}' created with {len(group.members)} members!")
                return group
        
        except Exception as e:
            print_error(f"Error creating group: {str(e)}")
            return None
    
    def add_shared_expense(self, user_id: int, group_id: int, category_name: str,
                          amount: float, description: str = "", 
                          split_equally: bool = True,
                          custom_splits: Dict[int, float] = None) -> Optional[Expense]:
        """
        Add a shared expense to a group.
        
        Args:
            user_id: User ID who paid for the expense
            group_id: Group ID
            category_name: Category name
            amount: Total expense amount
            description: Expense description
            split_equally: Whether to split equally among members
            custom_splits: Optional custom split amounts {user_id: amount}
        
        Returns:
            Expense object if created successfully, None otherwise
        """
        try:
            category = self.get_category_by_name(category_name)
            if not category:
                print_error(f"Category '{category_name}' not found.")
                return None
            
            with get_session() as session:
                # Get group and members
                group = session.query(Group).filter(Group.id == group_id).first()
                if not group:
                    print_error(f"Group not found.")
                    return None
                
                # Create expense
                expense = Expense(
                    user_id=user_id,
                    category_id=category.id,
                    amount=amount,
                    description=description,
                    group_id=group_id,
                    is_shared=True,
                    date=datetime.now()
                )
                session.add(expense)
                session.flush()
                
                # Create splits
                member_count = len(group.members)
                
                if split_equally:
                    split_amount = amount / member_count
                    for member in group.members:
                        split = ExpenseSplit(
                            expense_id=expense.id,
                            user_id=member.id,
                            amount=split_amount,
                            paid=(member.id == user_id)
                        )
                        session.add(split)
                else:
                    if custom_splits:
                        for member_id, split_amt in custom_splits.items():
                            split = ExpenseSplit(
                                expense_id=expense.id,
                                user_id=member_id,
                                amount=split_amt,
                                paid=(member_id == user_id)
                            )
                            session.add(split)
                
                print_success(f"Shared expense of {format_currency(amount)} added to group '{group.name}'!")
                return expense
        
        except Exception as e:
            print_error(f"Error adding shared expense: {str(e)}")
            return None
    
    def get_group_balances(self, group_id: int) -> List[Dict]:
        """
        Calculate balances for group members (who owes whom).
        
        Args:
            group_id: Group ID
        
        Returns:
            List of balance information
        """
        with get_session() as session:
            # Get all splits for the group
            splits = session.query(ExpenseSplit, Expense, User).join(
                Expense, ExpenseSplit.expense_id == Expense.id
            ).join(
                User, ExpenseSplit.user_id == User.id
            ).filter(Expense.group_id == group_id).all()
            
            # Calculate net balance for each user
            balances = {}
            for split, expense, user in splits:
                if user.id not in balances:
                    balances[user.id] = {
                        'user_id': user.id,
                        'username': user.username,
                        'total_paid': 0,
                        'total_owed': 0,
                        'net_balance': 0
                    }
                
                if split.paid:
                    # This user paid for this split
                    balances[user.id]['total_paid'] += expense.amount
                
                # This user owes this split amount
                balances[user.id]['total_owed'] += split.amount
            
            # Calculate net balance
            for user_id in balances:
                balances[user_id]['net_balance'] = (
                    balances[user_id]['total_paid'] - balances[user_id]['total_owed']
                )
            
            return list(balances.values())
