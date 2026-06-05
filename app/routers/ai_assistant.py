from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth_dependency import require_staff_or_admin
from app.models.user import User
from app.schemas.ai_assistant import AIQuestion, AIResponse
from app.services.ai_assistant_service import answer_ai_question

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIResponse)
def chat_with_ai_assistant(
    question: AIQuestion,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_admin)
):
    return answer_ai_question(db=db, question=question.question)
