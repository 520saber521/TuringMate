"""Chat Service - 引导对话业务逻辑层."""
from app.services.base import BaseService
from app.agents.socratic_tutor import socratic_tutor_agent


class ChatService(BaseService):
    """对话服务."""

    service_name = "chat"

    @BaseService.handle_errors("chat", "对话处理失败")
    async def start_session(self, question_id: str, user_id: str) -> dict:
        """开始新的引导对话会话."""
        self.log_info(f"启动引导对话: question_id={question_id}, user_id={user_id}")

        response = await socratic_tutor_agent.generate_response(
            session_id=f"session_{question_id}",
            user_message="[START]",
            question_context={"id": question_id},
        )
        return {
            "session_id": f"session_{question_id}",
            "first_message": response["content"],
            "stage": response["stage"],
        }

    @BaseService.handle_errors("chat", "消息处理失败")
    async def send_message(self, session_id: str, message: str) -> dict:
        """发送用户消息并获取引导回复."""
        self.log_info(f"收到消息: session={session_id}, len={len(message)}")

        response = await socratic_tutor_agent.generate_response(
            session_id=session_id,
            user_message=message,
        )
        return {
            "session_id": session_id,
            "content": response["content"],
            "stage": response["stage"],
            "hint_available": response.get("hint_available", False),
        }

    async def stream_message(self, session_id: str, message: str):
        """流式返回引导回复."""
        self.log_info(f"流式对话: session={session_id}")
        return socratic_tutor_agent.stream_response(
            session_id=session_id,
            user_message=message,
        )


chat_service = ChatService()