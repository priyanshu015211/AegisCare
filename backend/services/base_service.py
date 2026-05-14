from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.core.logging import get_logger

log = get_logger(__name__)

class BaseService(ABC):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    def log_info(self, message: str):
        self.logger.info(message)
