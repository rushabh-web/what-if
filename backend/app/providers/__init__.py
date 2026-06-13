"""Data provider abstraction layer."""
from app.providers.base import DataProvider
from app.providers.factory import get_provider

__all__ = ["DataProvider", "get_provider"]
