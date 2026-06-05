"""Chat Service - 引导对话业务逻辑层."""
from app.agents.socratic_tutor import socratic_tutor_agent


class ChatService:
    """对话服务."""

    async def start_session(self, question_id: str, user_id: str) -> dict:
        """开始新的引导对话会话."""
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

    async def send_message(self, session_id: str, message: str) -> dict:
        """发送用户消息并获取引导回复."""
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


chat_service = ChatService()
