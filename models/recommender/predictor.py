# models/recommender/predictor.py
from pathlib import Path

import torch

from data.repository import RecipeRepo
from models.recommender.model import MenuRecommender
from models.recommender.profile_encoder import encode_profile
from models.recommender.vocab import (
    MAX_INGREDIENTS,
    load_ingredient_vocab,
    tokenize_ingredients,
)

SAVE_PATH = Path("models/recommender.pt")

# ============================================================
# 飲食類型禁止的食材
# ============================================================
MEAT_KEYWORDS = {
    "豬肉", "豬肉片", "豬絞肉", "梅花肉", "豬肋排", "排骨", "豬油",
    "牛肉", "牛肉片", "牛絞肉", "牛排",
    "雞肉", "雞胸肉", "雞腿肉", "雞翅", "雞絞肉", "烏骨雞", "去骨雞腿排",
    "火雞絞肉", "鴨肉", "羊肉",
    "培根", "香腸", "貢丸", "肉片", "肉絲", "絞肉",
}

SEAFOOD_KEYWORDS = {
    "魚", "魚肉", "鮪魚", "鮪魚罐頭", "鯖魚", "鯖魚罐頭", "鮭魚", "鯛魚",
    "蝦", "蝦子", "蝦米", "章魚", "章魚乾", "花枝", "透抽", "干貝",
    "魚豆腐", "蟳味棒",
}

EGG_KEYWORDS = {
    "雞蛋", "蛋", "蛋黃", "蛋白", "雞蛋液",
    "皮蛋", "鹹蛋", "溫泉蛋", "滷蛋", "茶葉蛋",
}

DAIRY_KEYWORDS = {
    "牛奶", "鮮奶", "起司", "起士", "奶油", "鮮奶油",
    "優格", "希臘式優格", "乳酪絲",
}

DIET_FORBIDDEN = {
    "omnivore":   set(),
    "vegetarian": MEAT_KEYWORDS | SEAFOOD_KEYWORDS,
    "ovo":        MEAT_KEYWORDS | SEAFOOD_KEYWORDS | DAIRY_KEYWORDS,
    "lacto":      MEAT_KEYWORDS | SEAFOOD_KEYWORDS | EGG_KEYWORDS,
    "vegan":      MEAT_KEYWORDS | SEAFOOD_KEYWORDS | EGG_KEYWORDS | DAIRY_KEYWORDS,
}


class MenuPredictor:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ingredient_vocab = load_ingredient_vocab()

        checkpoint = torch.load(SAVE_PATH, map_location=device)
        vocab_size = checkpoint["ingredient_emb.weight"].shape[0]
        num_recipes = checkpoint["head.3.weight"].shape[0]

        self.model = MenuRecommender(
            vocab_size=vocab_size,
            num_recipes=num_recipes,
        ).to(device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        self.device = device
        self.recipe_repo = RecipeRepo()

    def predict(
        self,
        owned_ingredients: list[str],
        user_profile: dict,
        top_k: int = 3,
    ) -> list[dict]:
        # ⭐ 根據飲食類型過濾掉禁止的食材
        user_diet = user_profile.get("diet", "omnivore")
        forbidden = DIET_FORBIDDEN.get(user_diet, set())
        filtered_ingredients = [
            ing for ing in owned_ingredients if ing not in forbidden
        ]

        if not filtered_ingredients:
            return []

        # ⭐ 用 filtered_ingredients 不是 owned_ingredients
        ids = tokenize_ingredients(
            filtered_ingredients,
            vocab=self.ingredient_vocab,
            max_len=MAX_INGREDIENTS,
        )
        ing_tensor = torch.tensor([ids], dtype=torch.long).to(self.device)

        profile = encode_profile(user_profile)
        prof_tensor = torch.tensor([profile], dtype=torch.float).to(self.device)

        with torch.no_grad():
            logits = self.model(ing_tensor, prof_tensor)
            scores = torch.softmax(logits, dim=1)[0]

        all_recipes = self.recipe_repo.get_all()

        # 處理過敏原（同時支援 list 和字串）
        raw = user_profile.get("allergies", "")
        if isinstance(raw, list):
            user_allergies = {a.strip() for a in raw if a.strip()}
        else:
            user_allergies = {
                a.strip()
                for a in str(raw).replace("、", ",").split(",")
                if a.strip()
            }

        candidates = []
        for i, recipe in enumerate(all_recipes):
            if i >= len(scores):
                break
            if user_diet not in recipe["diet"]:
                continue
            if user_allergies & set(recipe.get("allergens", [])):
                continue
            candidates.append((scores[i].item(), recipe))

        candidates.sort(reverse=True, key=lambda x: x[0])
        return [recipe for _, recipe in candidates[:top_k]]