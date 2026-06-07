# ui/app.py
# 風格：中華一番動畫風（火焰 × 金龍 × 熱血料理）
# 框架：Gradio
# 配色：暗紅 × 金黃 × 黑

import html
import re
import gradio as gr
from ui.api_client import client
from ui.components import history_to_dataframe, recipe_to_markdown

USER_ID = 1

# ============================================================
# 🎨 中華一番風格 CSS
# ============================================================
CHINESE_ANIME_CSS = """
<style>
@keyframes fireFlicker {
    0%   { text-shadow: 0 0 10px #FF4500, 0 0 20px #FF6347, 0 0 40px #FF4500; }
    25%  { text-shadow: 0 0 15px #FFD700, 0 0 30px #FF8C00, 0 0 50px #FF4500; }
    50%  { text-shadow: 0 0 20px #FF6347, 0 0 40px #FF4500, 0 0 60px #FF0000; }
    75%  { text-shadow: 0 0 12px #FFD700, 0 0 25px #FF6347, 0 0 45px #FF4500; }
    100% { text-shadow: 0 0 10px #FF4500, 0 0 20px #FF6347, 0 0 40px #FF4500; }
}
@keyframes goldenPulse {
    0%   { box-shadow: 0 0 8px rgba(255,215,0,0.4), 0 0 16px rgba(255,165,0,0.2); }
    50%  { box-shadow: 0 0 16px rgba(255,215,0,0.7), 0 0 32px rgba(255,165,0,0.4), 0 0 48px rgba(255,69,0,0.2); }
    100% { box-shadow: 0 0 8px rgba(255,215,0,0.4), 0 0 16px rgba(255,165,0,0.2); }
}
@keyframes borderGlow {
    0%   { border-color: #B8860B; }
    50%  { border-color: #FFD700; }
    100% { border-color: #B8860B; }
}
@keyframes floatMedal {
    0%   { transform: translateY(0px) rotate(0deg); }
    50%  { transform: translateY(-6px) rotate(3deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}
@keyframes revealDish {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* 整體背景 */
.gradio-container {
    background:
        repeating-linear-gradient(45deg, transparent, transparent 30px,
            rgba(139,69,19,0.03) 30px, rgba(139,69,19,0.03) 31px),
        linear-gradient(180deg, #1A0A0A 0%, #2D0F0F 40%, #1A0505 100%) !important;
    color: #F5E6D0 !important;
}
body, .gradio-container, .main { background-color: #1A0A0A !important; }

/* 標題 */
.gradio-container h1 {
    color: #FFD700 !important;
    animation: fireFlicker 2s ease-in-out infinite;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    text-align: center;
}
.gradio-container h2 { color: #FFA500 !important; text-shadow: 0 0 8px rgba(255,165,0,0.5); }
.gradio-container h3 { color: #FFD700 !important; text-shadow: 0 0 6px rgba(255,215,0,0.4); }
.gradio-container p, .gradio-container label { color: #F5E6D0 !important; }

/* 按鈕 */
.gr-button, button.primary, button.secondary {
    background: linear-gradient(135deg, #8B0000 0%, #DC143C 50%, #8B0000 100%) !important;
    color: #FFD700 !important;
    border: 2px solid #DAA520 !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
    letter-spacing: 1px !important;
}
.gr-button:hover, button.primary:hover, button.secondary:hover {
    background: linear-gradient(135deg, #B22222 0%, #FF4500 50%, #B22222 100%) !important;
    box-shadow: 0 0 15px rgba(255,69,0,0.6), 0 0 30px rgba(255,140,0,0.3) !important;
    border-color: #FFD700 !important;
    transform: translateY(-2px) scale(1.03) !important;
}

/* 輸入框 */
textarea, input[type="text"], input[type="number"] {
    background: rgba(30,10,10,0.8) !important;
    color: #F5E6D0 !important;
    border: 2px solid #B8860B !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    animation: borderGlow 3s ease-in-out infinite;
}
textarea:focus, input:focus {
    border-color: #FFD700 !important;
    box-shadow: 0 0 12px rgba(255,215,0,0.4) !important;
}

/* Tab 標籤 */
.tab-nav button {
    color: #D2B48C !important;
    background: rgba(30,10,10,0.6) !important;
    border-bottom: 2px solid #8B4513 !important;
    font-weight: 700 !important;
}
.tab-nav button.selected {
    color: #FFD700 !important;
    border-bottom: 3px solid #FFD700 !important;
    background: rgba(139,0,0,0.3) !important;
}

/* Panel / Block 卡片 */
.gr-panel, .gr-box, .gr-form {
    background: linear-gradient(135deg, rgba(45,15,10,0.8), rgba(26,5,5,0.9)) !important;
    border: 1.5px solid #8B4513 !important;
    border-radius: 12px !important;
    animation: goldenPulse 4s ease-in-out infinite;
}

/* Dataframe 表格 */
.gr-dataframe table { background: rgba(30,10,10,0.8) !important; color: #F5E6D0 !important; }
.gr-dataframe th { background: rgba(139,0,0,0.5) !important; color: #FFD700 !important; border-bottom: 2px solid #DAA520 !important; }
.gr-dataframe tr:hover { background: rgba(139,69,19,0.2) !important; }

/* Markdown 區塊 */
.prose { color: #F5E6D0 !important; }
.prose h2 { color: #FFD700 !important; }
.prose h4 { color: #FFA500 !important; }
.prose table { border-color: #8B4513 !important; }
.prose td, .prose th { border-color: #8B4513 !important; color: #F5E6D0 !important; }

/* 分隔線 */
hr { border-color: #DAA520 !important; opacity: 0.5; }

/* Radio / Slider */
.gr-radio label span, .gr-checkbox label span { color: #F5E6D0 !important; }
input[type="range"] { accent-color: #FFD700 !important; }

/* 上傳區域 */
.upload-container, [data-testid="image"], .gr-image {
    border: 3px dashed #DAA520 !important;
    border-radius: 12px !important;
    background: rgba(30,15,5,0.6) !important;
    animation: borderGlow 3s ease-in-out infinite;
}

/* 食譜詳細資訊卡片 */
.recipe-detail {
    border: 2px solid #DAA520 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    background: linear-gradient(135deg, rgba(45,15,10,0.9), rgba(26,5,5,0.95)) !important;
    color: #F5E6D0 !important;
    animation: revealDish 0.5s ease-out;
}
.recipe-detail h3 { color: #FFD700 !important; animation: fireFlicker 2s ease-in-out infinite; }
.recipe-detail h4 { color: #FFA500 !important; }
.recipe-detail .tag {
    background: linear-gradient(135deg, #8B0000, #DC143C) !important;
    border: 1px solid #DAA520 !important;
    color: #FFD700 !important;
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: bold;
}
.recipe-detail .nutrition div {
    background: rgba(139,69,19,0.2) !important;
    border: 1px solid #8B4513 !important;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
}
.recipe-detail .nutrition b { color: #FFD700 !important; }
.recipe-detail .nutrition span { color: #F5E6D0 !important; margin-top: 4px; display: block; }

/* 獎牌動畫 */
.medal { animation: floatMedal 2s ease-in-out infinite; display: inline-block; }

/* 隱藏 Gradio 頁腳 */
footer { visibility: hidden !important; }
</style>
"""

# ============================================================
# 輔助函式
# ============================================================
def split_ingredients(ingredient_str: str) -> list[str]:
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
        # 加上獎牌排名
        medals = ["🥇 至尊料理", "🥈 絕品料理", "🥉 佳品料理"]
        outputs = []
        for i, recipe in enumerate(recipes[:3]):
            medal = medals[i] if i < 3 else ""
            md = profile_note + f"### {medal}\n\n" + recipe_to_markdown(recipe, i)
            outputs.append(md)
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
            (
                line
                for line in recipe_md.splitlines()
                if re.match(r"^##(?!#)\s+", line)
            ),
            "",
        )
        display_name = re.sub(r"^##\s+", "", name_line).strip()
        if not display_name:
            display_name = "未命名菜單"
        recipe_id = f"recipe_{abs(hash(display_name)) % 10000:04d}"
        client.save_history(USER_ID, recipe_id, display_name)
        return f"✅ 已收錄：{display_name}"
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
        return "✅ 個人化設定已儲存"
    except Exception as e:
        return f"儲存失敗：{e}"

def load_history():
    try:
        items = client.get_history(USER_ID)
        if not items:
            return [], "目前沒有歷史菜單", []
        return history_to_dataframe(items), f"共 {len(items)} 筆紀錄", items
    except Exception as e:
        return [], f"載入失敗：{e}", []


def reload_history():
    rows, status, items = load_history()
    return rows, status, items, None

def normalize_recipe_name(name: str) -> str:
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

def show_history_detail(table_data, history_items, evt: gr.SelectData):
    try:
        if table_data is None or len(table_data) == 0:
            return "<p style='color:#8B7355;'>目前沒有可查看的歷史菜單。</p>", None
        row_idx = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
        row = table_data.iloc[row_idx].tolist() if hasattr(table_data, "iloc") else table_data[row_idx]
        recipe_name = row[0]
        selected_id = None
        if history_items and row_idx < len(history_items):
            selected_id = history_items[row_idx].get("id")
        recipe = find_recipe_by_history_name(recipe_name)
        if not recipe:
            safe_name = html.escape(str(recipe_name))
            return f"<p style='color:#D2B48C;'>找不到「{safe_name}」的詳細食譜資料。</p>", selected_id

        n = recipe.get("nutrition", {})
        tags = "".join(
            f"<span class='tag'>{html.escape(str(tag))}</span> "
            for tag in recipe.get("tags", [])
        )
        required_items = "".join(
            f"<li style='color:#F5E6D0; margin-bottom:6px;'>{html.escape(str(ing))}</li>"
            for ing in recipe.get("required_ingredients", [])
        )
        optional_items = "".join(
            f"<li style='color:#B8860B; margin-bottom:6px;'>{html.escape(str(ing))} <span style=\"color:#8B7355; font-size:12px;\">可選</span></li>"
            for ing in recipe.get("optional_ingredients", [])
        )
        step_items = "".join(
            f"<li style='color:#F5E6D0; margin-bottom:8px; border-left:3px solid #DAA520; padding-left:10px;'>{html.escape(str(step))}</li>"
            for step in recipe.get("steps", [])
        )
        gi_text = n.get("gi_index")
        gi_cell = (
            f"<div style='background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;'>"
            f"<b style='color:#FFD700;display:block;'>GI 值</b>"
            f"<span style='color:#F5E6D0;margin-top:4px;display:block;'>{gi_text}</span></div>"
        ) if gi_text is not None else ""

        detail_html = f"""
<div class="recipe-detail" style="
    border: 2px solid #DAA520;
    border-radius: 14px;
    padding: 22px;
    background: linear-gradient(135deg, rgba(45,15,10,0.95), rgba(26,5,5,0.98));
    color: #F5E6D0;
">
  <h3 style="color:#FFD700; font-size:22px; margin:0 0 8px 0; animation: fireFlicker 2s ease-in-out infinite;">
    <span class="medal">{html.escape(str(recipe.get('emoji', '🍽️')))}</span>
    {html.escape(str(recipe.get('name', '')))}
  </h3>

  <div style="display:flex; flex-wrap:wrap; gap:6px; margin:10px 0 16px;">
    {tags}
  </div>

  <div style="
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
      gap: 8px; margin: 0 0 18px 0;
  ">
    <div style="background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFD700;display:block;">時間</b>
      <span style="color:#F5E6D0;margin-top:4px;display:block;">{recipe.get('time_min', '-')} 分鐘</span>
    </div>
    <div style="background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFD700;display:block;">熱量</b>
      <span style="color:#F5E6D0;margin-top:4px;display:block;">{n.get('calories', '-')} kcal</span>
    </div>
    <div style="background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFD700;display:block;">蛋白質</b>
      <span style="color:#F5E6D0;margin-top:4px;display:block;">{n.get('protein_g', '-')} g</span>
    </div>
    <div style="background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFD700;display:block;">碳水</b>
      <span style="color:#F5E6D0;margin-top:4px;display:block;">{n.get('carb_g', '-')} g</span>
    </div>
    <div style="background:rgba(139,69,19,0.2);border:1px solid #8B4513;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFD700;display:block;">脂肪</b>
      <span style="color:#F5E6D0;margin-top:4px;display:block;">{n.get('fat_g', '-')} g</span>
    </div>
    {gi_cell}
  </div>

  <h4 style="color:#FFA500; margin:16px 0 8px; border-bottom:1px solid #8B4513; padding-bottom:6px;">
    🥕 所需食材
  </h4>
  <ul style="padding-left:20px; margin:0 0 16px 0;">{required_items}{optional_items}</ul>

  <h4 style="color:#FFA500; margin:16px 0 8px; border-bottom:1px solid #8B4513; padding-bottom:6px;">
    👨‍🍳 料理步驟
  </h4>
  <ol style="padding-left:20px; margin:0;">{step_items}</ol>
</div>
"""
        return detail_html, selected_id
    except Exception as e:
        return f"<p style='color:#D2B48C;'>載入詳細內容失敗：{html.escape(str(e))}</p>", None


def delete_selected_history(selected_history_id):
    if not selected_history_id:
        rows, status, items = load_history()
        return (
            rows,
            "請先點選一筆要刪除的歷史菜單",
            "<p style='color:#8B7355;'>請點選左側食譜名稱查看詳細內容。</p>",
            None,
            items,
        )
    try:
        client.delete_history(USER_ID, int(selected_history_id))
        rows, status, items = load_history()
        return (
            rows,
            f"✅ 已刪除，{status}",
            "<p style='color:#8B7355;'>已刪除選取的歷史菜單。</p>",
            None,
            items,
        )
    except Exception as e:
        rows, status, items = load_history()
        return (
            rows,
            f"刪除失敗：{e}",
            "<p style='color:#D2B48C;'>刪除失敗，請重新選取後再試一次。</p>",
            None,
            items,
        )


# ============================================================
# 建立 Gradio 介面
# ============================================================
with gr.Blocks(
    title="🐉 黃金大廚！菜單推薦器",
    theme=gr.themes.Base(),
    css=CHINESE_ANIME_CSS,
) as demo:

    # 標題
    gr.HTML("""
    <div style="text-align:center; padding:20px 0 10px;">
        <div style="font-size:0.9em; color:#B8860B; letter-spacing:8px;">
            ── 傳說中的廚具正在發光 ──
        </div>
        <h1 style="font-size:2.6em; margin:8px 0 4px; color:#FFD700;">
            🐉 黃金大廚！菜單推薦器 🐉
        </h1>
        <div style="font-size:1em; color:#D2B48C; letter-spacing:2px;">
            上傳冰箱照片或輸入食材，讓特級廚師為你獻上最完美的料理！
        </div>
    </div>
    """)

    # ── Tab 1：生成今日菜單 ──
    with gr.Tab("🔥 生成今日菜單"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="background:linear-gradient(135deg,rgba(139,0,0,0.3),rgba(45,15,10,0.6));
                            border:2px solid #DAA520;border-radius:14px;padding:12px 18px;
                            text-align:center;">
                    <h3 style="margin:0;">📷 上傳冰箱照片</h3>
                    <span style="font-size:0.85em;color:#B8860B;">支援 JPG / PNG</span>
                </div>""")
                image_input = gr.Image(
                    type="filepath",
                    label="上傳食材照片",
                    height=200,
                )
                recognize_btn    = gr.Button("🔍 AI 辨識食材", variant="secondary")
                recognize_status = gr.Markdown("")
                gr.HTML("""
                <div style="background:linear-gradient(135deg,rgba(139,0,0,0.3),rgba(45,15,10,0.6));
                            border:2px solid #DAA520;border-radius:14px;padding:12px 18px;
                            text-align:center; margin-top:12px;">
                    <h3 style="margin:0;">📝 食材清單</h3>
                    <span style="font-size:0.85em;color:#B8860B;">可自行輸入或修改</span>
                </div>""")
                ingredient_input = gr.Textbox(
                    label="食材清單",
                    placeholder="例如：雞胸肉、番茄、雞蛋",
                    lines=4,
                )
                generate_btn = gr.Button("🐉 開始進行推薦！", variant="primary")

            with gr.Column(scale=2):
                gr.HTML("""
                <div style="text-align:center; padding:6px 0;">
                    <div style="font-size:0.8em; color:#B8860B; letter-spacing:6px;">
                        ── 特級廚師鑑定完畢 ──
                    </div>
                    <h2 style="font-size:1.6em; margin:4px 0;">🔥 推薦料理排行 🔥</h2>
                </div>""")
                with gr.Tabs():
                    with gr.Tab("🥇 至尊料理"):
                        recipe_out_1 = gr.Markdown("")
                        save_btn_1   = gr.Button("💾 收錄此料理", size="sm")
                    with gr.Tab("🥈 絕品料理"):
                        recipe_out_2 = gr.Markdown("")
                        save_btn_2   = gr.Button("💾 收錄此料理", size="sm")
                    with gr.Tab("🥉 佳品料理"):
                        recipe_out_3 = gr.Markdown("")
                        save_btn_3   = gr.Button("💾 收錄此料理", size="sm")
                save_status = gr.Markdown("")

        recognize_btn.click(fn=run_image_recognition, inputs=[image_input], outputs=[ingredient_input, recognize_status])
        generate_btn.click(fn=generate_menu, inputs=[ingredient_input], outputs=[recipe_out_1, recipe_out_2, recipe_out_3])
        save_btn_1.click(fn=lambda md, ing: save_recipe(md, 0, ing), inputs=[recipe_out_1, ingredient_input], outputs=[save_status])
        save_btn_2.click(fn=lambda md, ing: save_recipe(md, 1, ing), inputs=[recipe_out_2, ingredient_input], outputs=[save_status])
        save_btn_3.click(fn=lambda md, ing: save_recipe(md, 2, ing), inputs=[recipe_out_3, ingredient_input], outputs=[save_status])

    # ── Tab 2：個人化設定 ──
    with gr.Tab("🏮 個人化設定"):
        gr.HTML("""
        <div style="text-align:center; padding:10px 0;">
            <p style="color:#D2B48C;">「料理是為了讓人們幸福而存在的！」— 設定您的專屬口味</p>
        </div>""")
        with gr.Row():
            with gr.Column():
                diet_radio = gr.Radio(
                    choices=["omnivore", "vegan", "vegetarian", "ovo", "lacto"],
                    label="🥩 飲食類型",
                    value="omnivore",
                )
                goal_radio = gr.Radio(
                    choices=["none", "lose_fat", "gain_muscle", "blood_sugar", "low_sodium"],
                    label="💪 健康目標",
                    value="none",
                )
            with gr.Column():
                allergy_input = gr.Textbox(
                    label="⚠️ 過敏食材",
                    placeholder="例如：peanut、seafood、gluten",
                )
                servings_slider = gr.Slider(
                    minimum=1, maximum=8, step=1,
                    label="🍽️ 份量（幾人份）",
                    value=1,
                )
        profile_status = gr.Markdown("")
        with gr.Row():
            load_profile_btn = gr.Button("📜 載入設定")
            save_profile_btn = gr.Button("🔥 儲存設定", variant="primary")

        load_profile_btn.click(fn=load_profile, outputs=[diet_radio, goal_radio, allergy_input, servings_slider, profile_status])
        save_profile_btn.click(fn=save_profile, inputs=[diet_radio, goal_radio, allergy_input, servings_slider], outputs=[profile_status])

    # ── Tab 3：歷史菜單 ──
    with gr.Tab("📜 歷史菜單") as history_tab:
        gr.HTML("""
        <div style="text-align:center; padding:10px 0;">
            <h2 style="font-size:1.8em;">📜 歷史菜單</h2>
            <div style="font-size:0.9em; color:#B8860B; letter-spacing:3px;">
                ── 特級廚師的料理紀錄簿 ──
            </div>
        </div>""")
        gr.Markdown("點選左側任一列查看詳細做法與營養資訊")
        with gr.Row():
            with gr.Column(scale=1):
                history_items_state = gr.State([])
                selected_history_id = gr.State(None)
                history_table = gr.Dataframe(
                    headers=["食譜名稱", "日期"],
                    datatype=["str", "str"],
                    interactive=False,
                    wrap=True,
                    label="歷史紀錄",
                )
                history_status = gr.Markdown("")
                refresh_btn = gr.Button("🔄 重新載入")
                delete_history_btn = gr.Button("🗑️ 刪除選取菜單", variant="stop")
            with gr.Column(scale=2):
                history_detail = gr.HTML(
                    "<div style='text-align:center;padding:60px 20px;'>"
                    "<div style='font-size:3em;'>🏮</div>"
                    "<p style='color:#8B7355;margin-top:10px;'>請點選左側食譜名稱<br>查看詳細內容</p>"
                    "</div>"
                )

        refresh_btn.click(
            fn=reload_history,
            outputs=[
                history_table,
                history_status,
                history_items_state,
                selected_history_id,
            ],
        )
        history_tab.select(
            fn=reload_history,
            outputs=[
                history_table,
                history_status,
                history_items_state,
                selected_history_id,
            ],
        )
        history_table.select(
            fn=show_history_detail,
            inputs=[history_table, history_items_state],
            outputs=[history_detail, selected_history_id],
        )
        delete_history_btn.click(
            fn=delete_selected_history,
            inputs=[selected_history_id],
            outputs=[
                history_table,
                history_status,
                history_detail,
                selected_history_id,
                history_items_state,
            ],
        )

    demo.load(
        fn=reload_history,
        outputs=[
            history_table,
            history_status,
            history_items_state,
            selected_history_id,
        ],
    )


if __name__ == "__main__":
    demo.queue(max_size=2)
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
    )
