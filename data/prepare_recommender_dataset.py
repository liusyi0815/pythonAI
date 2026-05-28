# data/prepare_recommender_dataset.py
"""
產生推薦系統的訓練資料：
  輸入：隨機食材子集 + 使用者偏好向量
  標籤：對應的食譜 id
"""
import json, random
import numpy as np
from pathlib import Path
from models.recommender.profile_encoder import encode_profile

RECIPE_PATH = Path("data/recipes.json")
OUTPUT_PATH = Path("data/recommender_train.json")

INGREDIENT_VOCAB = {
    "<PAD>": 0, "雞蛋": 1, "番茄": 2, "青江菜": 3,
    "肉片": 4, "豆腐": 5, "牛奶": 6, "洋蔥": 7,
    "紅蘿蔔": 8, "馬鈴薯": 9, "蒜頭": 10,
}
MAX_ING = 20

DIET_OPTIONS    = ["omnivore", "vegan", "vegetarian", "ovo", "lacto"]
GOAL_OPTIONS    = ["none", "lose_fat", "gain_muscle", "blood_sugar"]
ALLERGY_OPTIONS = ["", "peanut", "seafood", "gluten"]

def tokenize(ingredients: list[str]) -> list[int]:
    ids = [INGREDIENT_VOCAB.get(i, 0)
           for i in ingredients][:MAX_ING]
    return ids + [0] * (MAX_ING - len(ids))

def generate_samples(n_samples: int = 50000) -> list[dict]:
    with open(RECIPE_PATH, encoding="utf-8") as f:
        recipes = json.load(f)
    recipe_ids = [r["id"] for r in recipes]
    recipe_map = {r["id"]: r for r in recipes}

    all_ingredients = list(INGREDIENT_VOCAB.keys())[1:]  # 排除 <PAD>
    samples = []

    for _ in range(n_samples):
        # 隨機抽一道食譜作為目標
        target_recipe = random.choice(recipes)
        target_id     = target_recipe["id"]
        target_idx    = recipe_ids.index(target_id)

        # 組合食材：目標食譜的必要食材 + 一些隨機食材
        required = target_recipe["required_ingredients"]
        n_extra  = random.randint(0, 5)
        extra    = random.sample(
            [i for i in all_ingredients if i not in required],
            min(n_extra, len(all_ingredients) - len(required))
        )
        # 模擬使用者可能只有部分食材（80% 機率保留每樣必要食材）
        owned = [i for i in required if random.random() > 0.2] + extra
        random.shuffle(owned)

        # 隨機使用者偏好
        user_profile = {
            "diet":      random.choice(DIET_OPTIONS),
            "goal":      random.choice(GOAL_OPTIONS),
            "allergies": random.choice(ALLERGY_OPTIONS),
            "servings":  random.randint(1, 4),
        }

        # 只有偏好符合的食譜才作為正樣本
        if user_profile["diet"] not in target_recipe["diet"]:
            continue
        allergy_set = set(user_profile["allergies"].split(","))
        if allergy_set & set(target_recipe.get("allergens", [])):
            continue

        samples.append({
            "ingredient_ids": tokenize(owned),
            "profile_vec":    encode_profile(user_profile),
            "label":          target_idx,
        })

    return samples

if __name__ == "__main__":
    print("產生訓練資料中...")
    samples = generate_samples(50000)
    OUTPUT_PATH.write_text(
        json.dumps(samples, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"✅ 產生 {len(samples)} 筆樣本 → {OUTPUT_PATH}")