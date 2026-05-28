# ui/app.py
import html
import re

import gradio as gr

from ui.api_client import client
from ui.components import history_to_dataframe, recipe_to_markdown

USER_ID = 1


def split_ingredients(ingredient_str: str) -> list[str]:
    """Split comma-like text input into ingredient names."""
    return [
        item.strip()
        for item in re.split(r"[,，、\n]+", ingredient_str)
        if item.strip()
    ]


def run_image_recognition(image):
    if image is None:
        return "", "請先上傳圖片"
    try:
        names = client.recognize_image(image)
        ingredient_str = "、".join(names)
        return ingredient_str, f"辨識到 {len(names)} 種食材：{ingredient_str}"
    except Exception as e:
        return "", f"辨識失敗：{e}"


def generate_menu(ingredient_str: str):
    if not ingredient_str.strip():
        return "請先輸入食材", "", ""

    try:
        result = client.recommend_menu(USER_ID, split_ingredients(ingredient_str))
        recipes = result["recipes"]
        profile = result["profile_used"]

        if not recipes:
            return "目前找不到適合的推薦菜單，請調整食材或個人化設定。", "", ""

        profile_note = (
            f"> 使用設定：{profile['diet']}，目標：{profile['goal']}，"
            f"{profile['servings']} 人份\n\n"
        )
        outputs = [
            profile_note + recipe_to_markdown(recipe, i)
            for i, recipe in enumerate(recipes[:3])
        ]
        while len(outputs) < 3:
            outputs.append("")
        return outputs[0], outputs[1], outputs[2]
    except Exception as e:
        return f"推薦失敗：{e}", "", ""


def save_recipe(recipe_md: str, recipe_idx: int, ingredient_str: str):
    if not recipe_md:
        return "目前沒有可儲存的菜單"

    try:
        name_line = next(
            (line for line in recipe_md.splitlines() if line.startswith("##")),
            "",
        )
        display_name = name_line.replace("##", "").strip()
        if not display_name:
            display_name = "未命名菜單"

        recipe_id = f"recipe_{abs(hash(display_name)) % 10000:04d}"
        client.save_history(USER_ID, recipe_id, display_name)
        return f"已儲存：{display_name}"
    except Exception as e:
        return f"儲存失敗：{e}"


def load_profile():
    try:
        profile = client.get_profile(USER_ID)
        return (
            profile["diet"],
            profile["goal"],
            "、".join(profile["allergies"]) if profile["allergies"] else "",
            profile["servings"],
            "個人化設定已載入",
        )
    except Exception as e:
        return "omnivore", "none", "", 1, f"載入失敗：{e}"


def save_profile(diet, goal, allergy_str, servings):
    allergies = split_ingredients(allergy_str)
    try:
        client.update_profile(USER_ID, diet, goal, allergies, int(servings))
        return "個人化設定已儲存"
    except Exception as e:
        return f"儲存失敗：{e}"


def load_history():
    try:
        items = client.get_history(USER_ID)
        if not items:
            return [], "目前沒有歷史菜單"
        return history_to_dataframe(items), f"共 {len(items)} 筆紀錄"
    except Exception as e:
        return [], f"載入失敗：{e}"


def normalize_recipe_name(name: str) -> str:
    """Make saved names such as '🥛 牛奶燕麥粥' match recipe names."""
    name = re.sub(r"\s+", " ", str(name)).strip()
    name = re.sub(r"^[^\w\u4e00-\u9fff]+", "", name).strip()
    return name


def find_recipe_by_history_name(recipe_name: str) -> dict | None:
    saved_name = normalize_recipe_name(recipe_name)
    recipes = client.get_recipe_repo()

    for recipe in recipes:
        data_name = normalize_recipe_name(recipe.get("name", ""))
        display_name = normalize_recipe_name(
            f"{recipe.get('emoji', '')} {recipe.get('name', '')}"
        )
        if saved_name in {data_name, display_name}:
            return recipe
        if saved_name.endswith(data_name) or data_name.endswith(saved_name):
            return recipe
    return None


def show_history_detail(table_data, evt: gr.SelectData) -> str:
    try:
        if table_data is None or len(table_data) == 0:
            return "<p>目前沒有可查看的歷史菜單。</p>"

        row_idx = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
        row = table_data.iloc[row_idx].tolist() if hasattr(table_data, "iloc") else table_data[row_idx]
        recipe_name = row[0]
        recipe = find_recipe_by_history_name(recipe_name)

        if not recipe:
            safe_name = html.escape(str(recipe_name))
            return f"<p>找不到「{safe_name}」的詳細食譜資料。</p>"

        n = recipe.get("nutrition", {})
        tags = "".join(
            f"<span class='tag'>{html.escape(str(tag))}</span>"
            for tag in recipe.get("tags", [])
        )
        required_items = "".join(
            f"<li>{html.escape(str(ing))}</li>"
            for ing in recipe.get("required_ingredients", [])
        )
        optional_items = "".join(
            f"<li>{html.escape(str(ing))} <span class='muted'>可選</span></li>"
            for ing in recipe.get("optional_ingredients", [])
        )
        step_items = "".join(
            f"<li>{html.escape(str(step))}</li>"
            for step in recipe.get("steps", [])
        )

        gi_text = n.get("gi_index")
        gi_cell = f"<div><b>GI</b><span>{gi_text}</span></div>" if gi_text is not None else ""

        return f"""
<style>
.recipe-detail {{
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 18px;
  background: #111827;
  color: #f9fafb;
}}
.recipe-detail h3 {{
  margin: 0 0 8px;
  font-size: 22px;
}}
.recipe-detail .tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0 14px;
}}
.recipe-detail .tag {{
  background: #374151;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
}}
.recipe-detail .nutrition {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 8px;
  margin: 12px 0 18px;
}}
.recipe-detail .nutrition div {{
  background: #1f2937;
  border-radius: 6px;
  padding: 10px;
}}
.recipe-detail .nutrition b,
.recipe-detail .nutrition span {{
  display: block;
}}
.recipe-detail .nutrition span {{
  margin-top: 4px;
  color: #d1d5db;
}}
.recipe-detail h4 {{
  margin: 16px 0 8px;
}}
.recipe-detail li {{
  margin-bottom: 6px;
}}
.recipe-detail .muted {{
  color: #9ca3af;
  font-size: 12px;
}}
</style>
<div class="recipe-detail">
  <h3>{html.escape(str(recipe.get('emoji', '')))} {html.escape(str(recipe.get('name', '')))}</h3>
  <div class="tags">{tags}</div>
  <div class="nutrition">
    <div><b>時間</b><span>{recipe.get('time_min', '-')} 分鐘</span></div>
    <div><b>熱量</b><span>{n.get('calories', '-')} kcal</span></div>
    <div><b>蛋白質</b><span>{n.get('protein_g', '-')} g</span></div>
    <div><b>碳水</b><span>{n.get('carb_g', '-')} g</span></div>
    <div><b>脂肪</b><span>{n.get('fat_g', '-')} g</span></div>
    {gi_cell}
  </div>
  <h4>需要食材</h4>
  <ul>{required_items}{optional_items}</ul>
  <h4>料理步驟</h4>
  <ol>{step_items}</ol>
</div>
"""
    except Exception as e:
        return f"<p>載入詳細內容失敗：{html.escape(str(e))}</p>"


with gr.Blocks(title="你的專屬菜單生成器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 你的專屬菜單生成器")
    gr.Markdown("上傳冰箱照片或輸入食材，AI 為你個人化推薦今日菜單")

    with gr.Tab("🥕 生成今日菜單"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 步驟 1：提供食材")
                image_input = gr.Image(
                    type="filepath",
                    label="上傳食材照片",
                    height=200,
                )
                recognize_btn = gr.Button("使用 AI 辨識圖片", variant="secondary")
                recognize_status = gr.Markdown("")

                ingredient_input = gr.Textbox(
                    label="食材清單",
                    placeholder="例如：雞胸肉、番茄、雞蛋",
                    lines=3,
                )
                generate_btn = gr.Button("生成菜單", variant="primary")

            with gr.Column(scale=2):
                gr.Markdown("### 步驟 2：查看推薦")
                with gr.Tabs():
                    with gr.Tab("推薦 1"):
                        recipe_out_1 = gr.Markdown("")
                        save_btn_1 = gr.Button("儲存到歷史", size="sm")
                    with gr.Tab("推薦 2"):
                        recipe_out_2 = gr.Markdown("")
                        save_btn_2 = gr.Button("儲存到歷史", size="sm")
                    with gr.Tab("推薦 3"):
                        recipe_out_3 = gr.Markdown("")
                        save_btn_3 = gr.Button("儲存到歷史", size="sm")

                save_status = gr.Markdown("")

        recognize_btn.click(
            fn=run_image_recognition,
            inputs=[image_input],
            outputs=[ingredient_input, recognize_status],
        )
        generate_btn.click(
            fn=generate_menu,
            inputs=[ingredient_input],
            outputs=[recipe_out_1, recipe_out_2, recipe_out_3],
        )
        save_btn_1.click(
            fn=lambda md, ing: save_recipe(md, 0, ing),
            inputs=[recipe_out_1, ingredient_input],
            outputs=[save_status],
        )
        save_btn_2.click(
            fn=lambda md, ing: save_recipe(md, 1, ing),
            inputs=[recipe_out_2, ingredient_input],
            outputs=[save_status],
        )
        save_btn_3.click(
            fn=lambda md, ing: save_recipe(md, 2, ing),
            inputs=[recipe_out_3, ingredient_input],
            outputs=[save_status],
        )

    with gr.Tab("⚙️ 個人化設定"):
        gr.Markdown("### 飲食條件")
        with gr.Row():
            with gr.Column():
                diet_radio = gr.Radio(
                    choices=["omnivore", "vegan", "vegetarian", "ovo", "lacto"],
                    label="飲食類型",
                    value="omnivore",
                )
                goal_radio = gr.Radio(
                    choices=["none", "lose_fat", "gain_muscle", "blood_sugar", "low_sodium"],
                    label="健康目標",
                    value="none",
                )
            with gr.Column():
                allergy_input = gr.Textbox(
                    label="過敏食材",
                    placeholder="例如：peanut、seafood、gluten",
                )
                servings_slider = gr.Slider(
                    minimum=1,
                    maximum=8,
                    step=1,
                    label="份量",
                    value=1,
                )

        profile_status = gr.Markdown("")
        with gr.Row():
            load_profile_btn = gr.Button("載入設定")
            save_profile_btn = gr.Button("儲存設定", variant="primary")

        load_profile_btn.click(
            fn=load_profile,
            outputs=[diet_radio, goal_radio, allergy_input, servings_slider, profile_status],
        )
        save_profile_btn.click(
            fn=save_profile,
            inputs=[diet_radio, goal_radio, allergy_input, servings_slider],
            outputs=[profile_status],
        )

    with gr.Tab("📋 歷史菜單") as history_tab:
        gr.Markdown("### 過去儲存的菜單")
        gr.Markdown("點選左側任一列查看詳細做法與營養資訊")

        with gr.Row():
            with gr.Column(scale=1):
                history_table = gr.Dataframe(
                    headers=["食譜名稱", "日期"],
                    datatype=["str", "str"],
                    interactive=False,
                    wrap=True,
                    label="歷史紀錄",
                )
                history_status = gr.Markdown("")
                refresh_btn = gr.Button("重新載入")

            with gr.Column(scale=2):
                history_detail = gr.HTML(
                    "<p>請點選左側食譜名稱查看詳細內容。</p>",
                    label="食譜詳細資訊",
                )

        refresh_btn.click(
            fn=load_history,
            outputs=[history_table, history_status],
        )
        history_tab.select(
            fn=load_history,
            outputs=[history_table, history_status],
        )
        history_table.select(
            fn=show_history_detail,
            inputs=[history_table],
            outputs=[history_detail],
        )

    demo.load(
        fn=load_history,
        outputs=[history_table, history_status],
    )


if __name__ == "__main__":
    demo.queue(max_size=2)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
    )
