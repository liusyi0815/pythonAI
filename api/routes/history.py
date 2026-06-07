# api/routes/history.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SaveHistoryRequest, HistoryResponse, HistoryItem
from api.dependencies import get_history_repo
from data.repository import HistoryRepo

router = APIRouter(prefix="/history", tags=["history"])

@router.post("/save")
async def save_history(
    body: SaveHistoryRequest,
    history_repo: HistoryRepo = Depends(get_history_repo),
):
    history_repo.save(body.user_id, body.recipe_id, body.recipe_name)
    return {"status": "ok"}

@router.get("/{user_id}", response_model=HistoryResponse)
async def get_history(
    user_id: int,
    limit:   int = 27,
    history_repo: HistoryRepo = Depends(get_history_repo),
):
    items = history_repo.get_recent(user_id, limit)
    return HistoryResponse(
        items=[HistoryItem(**i) for i in items],
        total=len(items),
    )

@router.delete("/{user_id}/{history_id}")
async def delete_history(
    user_id: int,
    history_id: int,
    history_repo: HistoryRepo = Depends(get_history_repo),
):
    deleted = history_repo.delete(user_id, history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="找不到要刪除的歷史紀錄")
    return {"status": "ok"}
