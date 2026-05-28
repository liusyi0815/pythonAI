# api/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ProfileUpdateRequest, ProfileResponse
from api.dependencies import get_user_repo
from data.repository import UserRepo

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: int,
    user_repo: UserRepo = Depends(get_user_repo),
):
    user = user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="找不到使用者")
    return ProfileResponse(
        user_id=user["id"],
        diet=user["diet"],
        goal=user["goal"],
        allergies=user["allergies"].split(",") if user["allergies"] else [],
        servings=user["servings"],
    )

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: int,
    body:     ProfileUpdateRequest,
    user_repo: UserRepo = Depends(get_user_repo),
):
    user_repo.update_profile(
        user_id=user_id,
        diet=body.diet,
        goal=body.goal,
        allergies=body.allergies,
    )
    return await get_profile(user_id, user_repo)