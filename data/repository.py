# data/repository.py
import sqlite3, json
from pathlib import Path

DB_PATH = "data/users.db"
RECIPE_PATH = "data/recipes.json"

class UserRepo:
    def get(self, user_id: int) -> dict:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM users WHERE id=?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def update_profile(self, user_id: int, diet: str,
                       goal: str, allergies: list[str]):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                UPDATE users
                SET diet=?, goal=?, allergies=?
                WHERE id=?
            """, (diet, goal, ",".join(allergies), user_id))

class HistoryRepo:
    def save(self, user_id: int, recipe_id: str, recipe_name: str):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO history (user_id, recipe_id, recipe_name, saved)
                VALUES (?, ?, ?, 1)
            """, (user_id, recipe_id, recipe_name))

    def get_recent(self, user_id: int, limit=27) -> list[dict]:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT recipe_id, recipe_name, eaten_at
                FROM history
                WHERE user_id=?
                ORDER BY eaten_at DESC LIMIT ?
            """, (user_id, limit)).fetchall()
            return [dict(r) for r in rows]

class RecipeRepo:
    def __init__(self):
        with open(RECIPE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        # 用 dict 讓查詢 O(1)
        self._recipes = {r["id"]: r for r in data}

    def get_all(self) -> list[dict]:
        return list(self._recipes.values())

    def get_by_id(self, recipe_id: str) -> dict:
        return self._recipes.get(recipe_id)

    def filter_by_diet(self, diet: str) -> list[dict]:
        return [r for r in self._recipes.values()
                if diet in r["diet"]]

    def filter_by_ingredients(self,
                               owned: list[str],
                               threshold: float = 0.5) -> list[dict]:
        """至少 threshold 比例的必要食材已擁有才回傳"""
        result = []
        owned_set = set(owned)
        for r in self._recipes.values():
            req = set(r["required_ingredients"])
            if not req:
                continue
            match_ratio = len(req & owned_set) / len(req)
            if match_ratio >= threshold:
                result.append((match_ratio, r))
        result.sort(reverse=True, key=lambda x: x[0])
        return [r for _, r in result]
