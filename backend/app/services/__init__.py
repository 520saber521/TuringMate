"""服务层模块.

提供统一的服务层基础设施:
- BaseService: 服务基类
- 各业务服务实例
"""

from app.services.base import BaseService
from app.services.chat_service import chat_service, ChatService
from app.services.diagnosis_service import diagnosis_service, DiagnosisService
from app.services.question_service import question_service, QuestionService
from app.services.correction_service import correction_service, CorrectionService

__all__ = [
    "BaseService",
    "chat_service",
    "ChatService",
    "diagnosis_service",
    "DiagnosisService",
    "question_service",
    "QuestionService",
    "correction_service",
    "CorrectionService",
]