from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from src.conversation.crud import (
    conversation_crud,
    conversation_session_crud,
    history_crud,
)
from src.conversation.schemas import HistoryResponse
from src.conversation.utils import recognize_and_send
from src.user.utils.deps import authenticated_user

conversation_router = APIRouter()


@conversation_router.websocket("/conversation")
async def websocket_conversation(
    authenticated: authenticated_user, websocket: WebSocket
):
    user, db = authenticated

    await websocket.accept()

    try:
        session = conversation_session_crud.create(
            db, user_id=user.id, created_by=user.email
        )
        await recognize_and_send(session.id, db, duration=60)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in WebSocket conversation: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        db.close()


@conversation_router.get(
    "/history", response_model=List[HistoryResponse], status_code=status.HTTP_200_OK
)
def get_history(authenticated: authenticated_user):
    user, db = authenticated

    try:
        return history_crud.get_user_history(db, user.id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@conversation_router.post("/start-conversation", status_code=status.HTTP_200_OK)
def start_conversation(authenticated: authenticated_user):
    user, db = authenticated

    permission = conversation_crud.check_conversation_permission(db, user.id)

    return {
        "message": permission["message"],
        "remaining conversations": permission["remaining_conversations"],
    }
