import json
from pathlib import Path

VOCAB_PATH = Path("data/ingredient_vocab.json")
RECIPE_PATH = Path("data/recipes.json")
MAX_INGREDIENTS = 20


def normalize_ingredient(name: str) -> str:
    return str(name).strip()


def build_ingredient_vocab(recipe_path: Path = RECIPE_PATH) -> dict[str, int]:
    with open(recipe_path, encoding="utf-8-sig") as f:
        recipes = json.load(f)

    ingredients = set()
    for recipe in recipes:
        for key in ("required_ingredients", "optional_ingredients"):
            for item in recipe.get(key, []):
                item = normalize_ingredient(item)
                if item:
                    ingredients.add(item)

    vocab = {"<PAD>": 0}
    for idx, ingredient in enumerate(sorted(ingredients), start=1):
        vocab[ingredient] = idx
    return vocab


def save_ingredient_vocab(vocab: dict[str, int], path: Path = VOCAB_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(vocab, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_ingredient_vocab(path: Path = VOCAB_PATH) -> dict[str, int]:
    if not path.exists():
        vocab = build_ingredient_vocab()
        save_ingredient_vocab(vocab, path)
        return vocab

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tokenize_ingredients(
    ingredients: list[str],
    vocab: dict[str, int] | None = None,
    max_len: int = MAX_INGREDIENTS,  # 前面有宣告MAX_INGREDIENTS = 20
) -> list[int]:
    vocab = vocab or load_ingredient_vocab()
    ids = [
        vocab.get(normalize_ingredient(ingredient), 0)
        for ingredient in ingredients
    ][:max_len]
    return ids + [0] * (max_len - len(ids))
