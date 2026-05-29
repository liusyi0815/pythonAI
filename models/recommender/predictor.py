# models/recommender/predictor.py
import torch
from models.recommender.model import MenuRecommender
from models.recommender.profile_encoder import encode_profile
from data.repository import RecipeRepo
from pathlib import Path

SAVE_PATH = Path("models/recommender.pt")

INGREDIENT_VOCAB = {
    "<PAD>": 0, "雞蛋": 1, "番茄": 2, "青江菜": 3,
    "肉片": 4, "豆腐": 5, "牛奶": 6,
    "洋蔥": 7, "紅蘿蔔": 8, "馬鈴薯": 9, "蒜頭": 10,
}
MAX_ING = 20

class MenuPredictor:
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # 從 checkpoint 自動推算正確的維度
        checkpoint  = torch.load(SAVE_PATH, map_location=device)
        vocab_size  = checkpoint["ingredient_emb.weight"].shape[0]
        num_recipes = checkpoint["head.3.weight"].shape[0]

        self.model = MenuRecommender(
            vocab_size=vocab_size,
            num_recipes=num_recipes,
        ).to(device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        self.device      = device
        self.recipe_repo = RecipeRepo()

    def predict(self,
                owned_ingredients: list[str],
                user_profile: dict,
                top_k: int = 3) -> list[dict]:

        # 1. 食材 token 化 + padding
        ids = [INGREDIENT_VOCAB.get(ing, 0)
               for ing in owned_ingredients][:MAX_ING]
        ids += [0] * (MAX_ING - len(ids))
        ing_tensor = torch.tensor([ids], dtype=torch.long).to(self.device)

        # 2. 使用者偏好向量
        profile     = encode_profile(user_profile)
        prof_tensor = torch.tensor([profile], dtype=torch.float).to(self.device)

        # 3. 模型推理
        with torch.no_grad():
            logits = self.model(ing_tensor, prof_tensor)
            scores = torch.softmax(logits, dim=1)[0]

        # 4. 硬性過濾 + 分數排序
        all_recipes    = self.recipe_repo.get_all()
        user_diet      = user_profile.get("diet", "omnivore")
        user_allergies = set(
            a for a in user_profile.get("allergies", "").split(",") if a
        )

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
        return [r for _, r in candidates[:top_k]]