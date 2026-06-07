# ui/api_client.py
import json
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000"


class MenuAPIClient:
    def recognize_image(self, image_path: str) -> list[str]:
        with open(image_path, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/recognize/image",
                files={"file": (Path(image_path).name, f, "image/jpeg")},
                timeout=30,
            )
        resp.raise_for_status()
        data = resp.json()
        return [item["name"] for item in data["ingredients"]]

    def recommend_menu(self, user_id: int, ingredients: list[str]) -> dict:
        resp = requests.post(
            f"{BASE_URL}/recommend/menu",
            json={"user_id": user_id, "ingredients": ingredients},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()

    def get_profile(self, user_id: int) -> dict:
        resp = requests.get(f"{BASE_URL}/profile/{user_id}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def update_profile(
        self,
        user_id: int,
        diet: str,
        goal: str,
        allergies: list[str],
        servings: int,
    ) -> dict:
        resp = requests.put(
            f"{BASE_URL}/profile/{user_id}",
            json={
                "diet": diet,
                "goal": goal,
                "allergies": allergies,
                "servings": servings,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def save_history(self, user_id: int, recipe_id: str, recipe_name: str):
        resp = requests.post(
            f"{BASE_URL}/history/save",
            json={
                "user_id": user_id,
                "recipe_id": recipe_id,
                "recipe_name": recipe_name,
            },
            timeout=10,
        )
        resp.raise_for_status()

    def get_history(self, user_id: int) -> list[dict]:
        resp = requests.get(
            f"{BASE_URL}/history/{user_id}?limit=27",
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["items"]

    def delete_history(self, user_id: int, history_id: int):
        resp = requests.delete(
            f"{BASE_URL}/history/{user_id}/{history_id}",
            timeout=10,
        )
        resp.raise_for_status()

    def get_recipe_repo(self) -> list[dict]:
        with open("data/recipes.json", encoding="utf-8-sig") as f:
            return json.load(f)


client = MenuAPIClient()
