import json
import random
from pathlib import Path

from models.recommender.profile_encoder import encode_profile
from models.recommender.vocab import (
    build_ingredient_vocab,
    save_ingredient_vocab,
    tokenize_ingredients,
)

RECIPE_PATH = Path("data/recipes.json")
OUTPUT_PATH = Path("data/recommender_train.json")

DIET_OPTIONS = ["omnivore", "vegan", "vegetarian", "ovo", "lacto"]
GOAL_OPTIONS = ["none", "lose_fat", "gain_muscle", "blood_sugar"]
ALLERGY_OPTIONS = ["", "peanut", "seafood", "gluten"]


def generate_samples(n_samples: int = 50000) -> list[dict]:
    with open(RECIPE_PATH, encoding="utf-8") as f:
        recipes = json.load(f)

    vocab = build_ingredient_vocab(RECIPE_PATH)
    save_ingredient_vocab(vocab)

    recipe_ids = [recipe["id"] for recipe in recipes]
    all_ingredients = list(vocab.keys())[1:]
    samples = []

    for _ in range(n_samples):
        target_recipe = random.choice(recipes)
        target_idx = recipe_ids.index(target_recipe["id"])

        required = target_recipe.get("required_ingredients", [])
        n_extra = random.randint(0, 5)
        extra_candidates = [item for item in all_ingredients if item not in required]
        extra = random.sample(extra_candidates, min(n_extra, len(extra_candidates)))

        owned = [item for item in required if random.random() > 0.2] + extra
        random.shuffle(owned)

        user_profile = {
            "diet": random.choice(DIET_OPTIONS),
            "goal": random.choice(GOAL_OPTIONS),
            "allergies": random.choice(ALLERGY_OPTIONS),
            "servings": random.randint(1, 4),
        }

        if user_profile["diet"] not in target_recipe.get("diet", []):
            continue

        allergy_set = {item for item in user_profile["allergies"].split(",") if item}
        if allergy_set & set(target_recipe.get("allergens", [])):
            continue

        samples.append({
            "ingredient_ids": tokenize_ingredients(owned, vocab),
            "profile_vec": encode_profile(user_profile),
            "label": target_idx,
        })

    return samples


if __name__ == "__main__":
    print("Generating recommender training data...")
    samples = generate_samples(50000)
    OUTPUT_PATH.write_text(
        json.dumps(samples, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Generated {len(samples)} samples -> {OUTPUT_PATH}")
