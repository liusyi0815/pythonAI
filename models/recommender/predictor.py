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
        ids = tokenize_ingredients(
            owned_ingredients,
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
        user_diet = user_profile.get("diet", "omnivore")
        # 修正後：同時處理 list 和逗號分隔字串兩種格式
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
