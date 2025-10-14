from core.db.models import BaseModel


class ConversationSession(BaseModel):
    class Meta:
        db_table = "restaurant_conversation_session"
