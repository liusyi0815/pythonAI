# ui/components.py


def recipe_to_markdown(recipe: dict, idx: int) -> str:
    """Format one recommended recipe for Gradio Markdown."""
    stars = "★" * round(recipe.get("match_ratio", 0) * 5)
    n = recipe["nutrition"]

    required_lines = "\n".join(
        f"- {ing}" for ing in recipe.get("required_ingredients", [])
    )
    optional_lines = "\n".join(
        f"- {ing} (可選)" for ing in recipe.get("optional_ingredients", [])
    )
    step_lines = "\n".join(
        f"{i + 1}. {step}" for i, step in enumerate(recipe.get("steps", []))
    )
    tags = " ".join(f"`{tag}`" for tag in recipe.get("tags", []))

    return f"""
## {recipe.get('emoji', '')} {recipe['name']}
{stars} 食材符合度：{recipe.get('match_ratio', 0) * 100:.0f}%

| 項目 | 內容 |
|------|------|
| 烹調時間 | {recipe.get('time_min', '-')} 分鐘 |
| 熱量 | {n.get('calories', '-')} kcal |
| 蛋白質 | {n.get('protein_g', '-')} g |
| 碳水 | {n.get('carb_g', '-')} g |
| 脂肪 | {n.get('fat_g', '-')} g |

**標籤：** {tags}

### 需要食材
{required_lines}
{optional_lines}

### 做法
{step_lines}
"""


def history_to_dataframe(items: list[dict]) -> list[list]:
    """Convert API history items into rows for a Gradio Dataframe."""
    return [
        [item["recipe_name"], item["eaten_at"][:10]]
        for item in items
    ]
