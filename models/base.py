"""
Base model with common mixins
"""
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass