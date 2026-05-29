# api/schemas.py
from pydantic import BaseModel
from typing import Optional

# ── recognize ──
class IngredientItem(BaseModel):
    name:       str
    confidence: float
    bbox:       list[int]

class RecognizeResponse(BaseModel):
    ingredients: list[IngredientItem]
    raw_image_size: list[int]

# ── recommend ──
class RecommendRequest(BaseModel):
    user_id:     int
    ingredients: list[str]   # 文字輸入 or 辨識結果合併

class NutritionInfo(BaseModel):
    calories:  int
    protein_g: float
    carb_g:    float
    fat_g:     float
    gi_index:  Optional[int] = None

class RecipeResult(BaseModel):
    id:                   str
    name:                 str
    emoji:                str = "🍽️"
    time_min:             int
    tags:                 list[str]
    nutrition:            NutritionInfo
    required_ingredients: list[str]
    optional_ingredients: list[str]
    steps:                list[str]
    match_ratio:          float   # 使用者已有食材的比例

class RecommendResponse(BaseModel):
    recipes:    list[RecipeResult]
    profile_used: dict            # 回傳套用了哪些偏好，方便前端顯示

# ── profile ──
class ProfileUpdateRequest(BaseModel):
    diet:      str = "omnivore"
    goal:      str = "none"
    allergies: list[str] = []
    servings:  int = 1

class ProfileResponse(BaseModel):
    user_id:   int
    diet:      str
    goal:      str
    allergies: list[str]
    servings:  int

# ── history ──
class SaveHistoryRequest(BaseModel):
    user_id:     int
    recipe_id:   str
    recipe_name: str

class HistoryItem(BaseModel):
    recipe_id:   str
    recipe_name: str
    eaten_at:    str

class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
