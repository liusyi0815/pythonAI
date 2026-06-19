from typing import Optional

from pydantic import BaseModel


class IngredientItem(BaseModel):
    name: str
    confidence: float
    bbox: list[int]


class RecognizeResponse(BaseModel):
    ingredients: list[IngredientItem]
    raw_image_size: list[int]


class RecommendRequest(BaseModel):
    user_id: int
    ingredients: list[str]


class NutritionInfo(BaseModel):
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carb_g: Optional[float] = None
    fat_g: Optional[float] = None
    gi_index: Optional[int] = None


class RecipeResult(BaseModel):
    id: str
    name: str
    emoji: str = "🍽️"
    time_min: int
    tags: list[str]
    nutrition: NutritionInfo
    required_ingredients: list[str]
    optional_ingredients: list[str]
    steps: list[str]
    match_ratio: float


class RecommendResponse(BaseModel):
    recipes: list[RecipeResult]
    profile_used: dict


class ProfileUpdateRequest(BaseModel):
    diet: str = "omnivore"
    goal: str = "none"
    allergies: list[str] = []
    servings: int = 1


class ProfileResponse(BaseModel):
    user_id: int
    diet: str
    goal: str
    allergies: list[str]
    servings: int


class SaveHistoryRequest(BaseModel):
    user_id: int
    recipe_id: str
    recipe_name: str


class HistoryItem(BaseModel):
    id: int
    recipe_id: str
    recipe_name: str
    eaten_at: str


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int