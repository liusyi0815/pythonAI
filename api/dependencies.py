# api/dependencies.py
from functools import lru_cache
from models.vision.recognizer import FoodRecognizer
from models.recommender.predictor import MenuPredictor
from data.repository import UserRepo, HistoryRepo, RecipeRepo

@lru_cache(maxsize=1)
def get_recognizer() -> FoodRecognizer:
    return FoodRecognizer()

@lru_cache(maxsize=1)
def get_predictor() -> MenuPredictor:
    return MenuPredictor()

@lru_cache(maxsize=1)
def get_user_repo() -> UserRepo:
    return UserRepo()

@lru_cache(maxsize=1)
def get_history_repo() -> HistoryRepo:
    return HistoryRepo()

@lru_cache(maxsize=1)
def get_recipe_repo() -> RecipeRepo:
    return RecipeRepo()