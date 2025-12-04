"""
Database models for the Expense Tracker application.
Uses SQLAlchemy ORM for database abstraction.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, 
    Boolean, Table, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Association table for many-to-many relationship between users and groups
user_group = Table(
    'user_group',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow)
)


class User(Base):
    """
    User model representing application users.
    Each user can have multiple expenses, budgets, and belong to multiple groups.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    budgets = relationship('Budget', back_populates='user', cascade='all, delete-orphan')
    alerts = relationship('Alert', back_populates='user', cascade='all, delete-orphan')
    groups = relationship('Group', secondary=user_group, back_populates='members')
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Category(Base):
    """
    Category model for expense classification.
    Categories help organize expenses into meaningful groups.
    """
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = relationship('Expense', back_populates='category')
    budgets = relationship('Budget', back_populates='category')
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Budget(Base):
    """
    Budget model for tracking spending limits.
    Supports different budgets for different months and categories.
    """
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='budgets')
    category = relationship('Category', back_populates='budgets')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'category_id', 'month', 'year', 
                        name='unique_user_category_month_year'),
        CheckConstraint('amount > 0', name='positive_amount'),
        CheckConstraint('month >= 1 AND month <= 12', name='valid_month'),
    )
    
    def __repr__(self):
        return f"<Budget(user_id={self.user_id}, category_id={self.category_id}, " \
               f"amount={self.amount}, month={self.month}, year={self.year})>"


class Expense(Base):
    """
    Expense model for tracking individual spending records.
    Can be personal or shared among a group.
    """
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    is_shared = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='expenses')
    category = relationship('Category', back_populates='expenses')
    group = relationship('Group', back_populates='expenses')
    splits = relationship('ExpenseSplit', back_populates='expense', cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_expense_amount'),
    )
    
    def __repr__(self):
        return f"<Expense(user_id={self.user_id}, category='{self.category.name}', " \
               f"amount={self.amount}, date={self.date})>"


class Group(Base):
    """
    Group model for shared expenses (Splitwise-like functionality).
    Users can create groups to track and split expenses.
    """
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(200))
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship('User', secondary=user_group, back_populates='groups')
    expenses = relationship('Expense', back_populates='group')
    
    def __repr__(self):
        return f"<Group(name='{self.name}', members={len(self.members)})>"


class ExpenseSplit(Base):
    """
    ExpenseSplit model for tracking how shared expenses are split.
    Records each user's share of a group expense.
    """
    __tablename__ = 'expense_splits'
    
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    expense = relationship('Expense', back_populates='splits')
    user = relationship('User')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='non_negative_split_amount'),
    )
    
    def __repr__(self):
        return f"<ExpenseSplit(expense_id={self.expense_id}, user_id={self.user_id}, " \
               f"amount={self.amount}, paid={self.paid})>"


class Alert(Base):
    """
    Alert model for tracking budget warnings and notifications.
    Supports custom alert thresholds per user and category.
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    threshold_percentage = Column(Integer, default=10)  # Alert when X% budget left
    is_active = Column(Boolean, default=True)
    email_notification = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='alerts')
    category = relationship('Category')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('threshold_percentage >= 0 AND threshold_percentage <= 100', 
                       name='valid_threshold'),
    )
    
    def __repr__(self):
        return f"<Alert(user_id={self.user_id}, category_id={self.category_id}, " \
               f"threshold={self.threshold_percentage}%)>"
