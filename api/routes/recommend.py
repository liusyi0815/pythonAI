# api/routes/recommend.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (RecommendRequest, RecommendResponse,
                          RecipeResult, NutritionInfo)
from api.dependencies import get_predictor, get_user_repo
from models.recommender.predictor import MenuPredictor
from data.repository import UserRepo

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.post("/menu", response_model=RecommendResponse)
async def recommend_menu(
    body:      RecommendRequest,
    predictor: MenuPredictor = Depends(get_predictor),
    user_repo: UserRepo      = Depends(get_user_repo),
):
    # 1. 取出使用者設定
    user = user_repo.get(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="找不到使用者")

    # 2. 推薦
    recipes = predictor.predict(
        owned_ingredients=body.ingredients,
        user_profile=user,
        top_k=3,
    )
    if not recipes:
        raise HTTPException(status_code=204,
                            detail="沒有符合條件的食譜，請調整偏好設定")

    # 3. 計算每道食譜的食材符合率
    owned_set = set(body.ingredients)

    def calc_match(recipe: dict) -> float:
        req = set(recipe["required_ingredients"])
        if not req:
            return 1.0
        return round(len(req & owned_set) / len(req), 2)

    results = [
    RecipeResult(
        **{k: v for k, v in recipe.items()
           if k in RecipeResult.model_fields
           and k != "nutrition"},        # 加這行排除 nutrition
        nutrition=NutritionInfo(**recipe["nutrition"]),
        match_ratio=calc_match(recipe),
    )
    for recipe in recipes
    ]

    return RecommendResponse(
        recipes=results,
        profile_used={
            "diet":      user["diet"],
            "goal":      user["goal"],
            "allergies": user["allergies"],
            "servings":  user["servings"],
        },
    )