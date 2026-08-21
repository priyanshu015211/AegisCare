"""
backend/services/base_service.py

Abstract base class for all services in AegisCare.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.core.logging import get_logger


class BaseService(ABC):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)
