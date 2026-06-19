# api/routes/recommend.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (RecommendRequest, RecommendResponse,
                          RecipeResult, NutritionInfo)
from api.dependencies import get_predictor, get_user_repo
from models.recommender.predictor import MenuPredictor
from data.repository import UserRepo

router = APIRouter(prefix="/recommend", tags=["recommend"])


def clean_nutrition(nutrition: dict) -> dict:
    cleaned = {}
    for key in ("calories", "protein_g", "carb_g", "fat_g", "gi_index"):
        value = nutrition.get(key)
        if isinstance(value, (int, float)) or value is None:
            cleaned[key] = value
        else:
            cleaned[key] = None
    return cleaned

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
        top_k=50,
    )

    if not recipes:
        return RecommendResponse(
            recipes=[],
            profile_used={
                "diet":      user["diet"],
                "goal":      user["goal"],
                "allergies": user["allergies"],
                "servings":  user["servings"],
            },
        )


    # 3. 計算每道食譜的食材符合率
    owned_set = set(body.ingredients)

    def calc_match(recipe: dict) -> float:
        req = recipe["required_ingredients"]
        if not req:
            return 1.0
        matched = sum(
            1 for r in req
            if any(ing in r for ing in owned_set)  # 改成「包含」比對
        )
        return round(matched / len(req), 2)

    results = [
    RecipeResult(
        **{k: v for k, v in recipe.items()
           if k in RecipeResult.model_fields
           and k != "nutrition"},        # 加這行排除 nutrition
        nutrition=NutritionInfo(**clean_nutrition(recipe.get("nutrition", {}))),
        match_ratio=calc_match(recipe),
    )
    for recipe in recipes
    ]

    results.sort(key=lambda r: r.match_ratio, reverse=True)
    results = results[:3]

    return RecommendResponse(
        recipes=results,
        profile_used={
            "diet":      user["diet"],
            "goal":      user["goal"],
            "allergies": user["allergies"],
            "servings":  user["servings"],
        },
    )