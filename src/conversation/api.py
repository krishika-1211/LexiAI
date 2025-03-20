from typing import List

from fastapi import APIRouter, HTTPException, WebSocket, status

from src.conversation.crud import history_crud
from src.conversation.schemas import HistoryResponse
from src.conversation.utils import websocket_conversation
from src.user.utils.deps import authenticated_user

conversation_router = APIRouter()


@conversation_router.websocket("/conversation")
async def conversation(
    websocket: WebSocket,
    authenticated: authenticated_user,
    topic_id: str,
    duration: int,
):
    user, db = authenticated

    await websocket_conversation(websocket, db, user, topic_id, duration)


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
