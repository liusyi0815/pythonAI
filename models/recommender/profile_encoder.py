# models/recommender/profile_encoder.py

DIET_MAP = {
    "omnivore": 0, "vegan": 1, "vegetarian": 2, "ovo": 3, "lacto": 4
}
GOAL_MAP = {
    "none": 0, "lose_fat": 1, "gain_muscle": 2,
    "blood_sugar": 3, "low_sodium": 4
}
ALLERGY_LIST = ["peanut", "seafood", "gluten", "dairy", "nuts"]

def encode_profile(user: dict) -> list[float]:
    """
    把使用者設定編成 15 維 float 向量：
    [diet_onehot×5, goal_onehot×5, allergy_flags×5]
    """
    vec = [0.0] * 15

    # diet one-hot (dim 0–4)
    diet_idx = DIET_MAP.get(user["diet"], 0)
    vec[diet_idx] = 1.0

    # goal one-hot (dim 5–9)
    goal_idx = GOAL_MAP.get(user["goal"], 0)
    vec[5 + goal_idx] = 1.0

    # allergy flags (dim 10–14)
    user_allergies = set(user.get("allergies", "").split(","))
    for i, allergen in enumerate(ALLERGY_LIST):
        vec[10 + i] = 1.0 if allergen in user_allergies else 0.0

    return vec