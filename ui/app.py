# ui/app.py
# 框架：Gradio
# 配色：白色 × 米色 × 淺黃

import html
import re
import os         
import base64 
import gradio as gr
from ui.api_client import client
from ui.components import history_to_dataframe, recipe_to_markdown

USER_ID = 1

# ============================================================
# Logo 設定
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

def make_banner():
    """生成頂部 Banner HTML（含 Logo）"""
    logo_html = ""
    if os.path.isfile(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64}" style="max-height:130px; margin: 0 auto; display:block;">'
    else:
        logo_html = '<div style="font-size:3rem; margin-bottom:0.5rem;">🍽️</div>'

    return f"""
    <div class="banner-wrap" style="
        background: linear-gradient(135deg, #244D82 0%, #2A5580 100%) !important;
        background-image: linear-gradient(135deg, #244D82 0%, #2A5580 100%) !important;
        border-radius: 16px; padding: 2rem 1.5rem; text-align: center;
        margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(26, 53, 80, 0.3);
    ">
        {logo_html}
        <div style="color: #FFCE39 !important; font-size: 2.2rem; font-weight: bold;
                    letter-spacing: 0.3rem; margin: 0.5rem 0 0.3rem 0;">
            菜單推薦器
        </div>
        <div style="color: #B0BEC5 !important; font-size: 1rem;">
            上傳冰箱照片或輸入食材，為你推薦出相似度最高的三道料理
        </div>
    </div>
    """

CHINESE_ANIME_CSS = """

/* ============================================
   強制淺色模式（修復深色模式顯示問題）
   ============================================ */
:root, .dark, .gr-theme-soft.dark {
    --background-fill-primary: #F8FAFF !important;
    --background-fill-secondary: #F8FAFF !important;
    --block-background-fill: #F8FAFF !important;
    --block-border-color: #B0BEC5 !important;
    --body-background-fill: #F8FAFF !important;
    --body-text-color: #000000 !important;
    --input-background-fill: #F8FAFF !important;
    --input-border-color: #B0BEC5 !important;
    --panel-background-fill: #F8FAFF !important;
    --block-label-background-fill: #F8FAFF !important;
    --block-label-text-color: #000000 !important;
    --checkbox-background-color: #F8FAFF !important;
    --checkbox-label-background-fill: #F8FAFF !important;
    --color-accent-soft: #FFF3D0 !important;
    --neutral-50: #F8FAFF !important;
    --neutral-100: #F8FAFF !important;
    --neutral-200: #D6DCE0 !important;
    --neutral-700: #000000 !important;
    --neutral-800: #000000 !important;
}

.dark .gradio-container {
    background: linear-gradient(180deg, #F8FAFF 0%, #F8FAFF 100%) !important;
}
.dark .gradio-container * {
    --block-background-fill: #F8FAFF !important;
}
.dark label, .dark .gr-markdown, .dark .gr-markdown h3,
.dark span, .dark p, .dark h1, .dark h2, .dark h3, .dark h4 {
    color: #000000 !important;
}
.dark textarea, .dark input[type="text"], .dark .gr-textbox textarea {
    background: #F8FAFF !important;
    color: #000000 !important;
    border-color: #B0BEC5 !important;
}
.dark .gr-radio, .dark .gr-checkbox-group,
.dark .gr-group, .dark .gr-form,
.dark .gr-panel, .dark .gr-box,
.dark fieldset, .dark .block {
    background: #F8FAFF !important;
    color: #000000 !important;
}
.dark .gr-radio label span,
.dark .gr-checkbox-group label span,
.dark input[type="radio"] + span,
.dark input[type="checkbox"] + span {
    color: #000000 !important;
}
.dark .gr-dropdown, .dark select {
    background: #F8FAFF !important;
    color: #000000 !important;
}
.dark button.secondary {
    color: #000000 !important;
    background: #F8FAFF !important;
    border: 1px solid #B0BEC5 !important;
}
.dark .pref-card, .dark .pref-card * {
    background: #F8FAFF !important;
    color: #000000 !important;
}
.dark .pref-card fieldset,
.dark .pref-card .block,
.dark .pref-card .wrap {
    background: #F8FAFF !important;
    border-color: transparent !important;
}
.dark .upload-area, .dark .upload-area * {
    background: #F8FAFF !important;
    color: #000000 !important;
}
.dark .block .label-wrap span,
.dark .block > label > span {
    background: #F8FAFF !important;
    color: #000000 !important;
}

/* ====== 整體背景 ====== */
body, .gradio-container {
    background: linear-gradient(180deg, #F8FAFF 0%, #F8FAFF 100%) !important;
    color: #000000 !important;
    font-family: "Microsoft JhengHei", "Noto Sans TC", sans-serif !important;
}

/* ====== 區塊面板（白底 + 金黃框） ====== */
.gr-block, .gr-box, .gr-panel, .gr-form, .gr-group {
    background-color: #F8FAFF !important;
    border: 2px solid #FFCE39 !important;
    border-radius: 12px !important;
}

/* ====== HTML 卡片 ====== */
.gr-html, .gr-html div, .gr-html h4, .gr-html p,
.prose h4, .prose p {
    background: transparent !important;
    background-image: none !important;
    color: #000000 !important;
    border-radius: 8px !important;
}

/* ====== Label 標籤 ====== */
label, .gr-label, span.svelte-1gfkn6j,
.label-wrap, .block-label,
div[data-testid="block-label"] {
    background-color: transparent !important;
    background-image: none !important;
    color: #000000 !important;
    font-weight: bold !important;
}

/* ====== 輸入框容器 ====== */
.gr-input-container, .gr-text-input-container,
.gr-image-container, .gr-file-container,
div[data-testid="textbox"], div[data-testid="image"] {
    background-color: #F8FAFF !important;
    background-image: none !important;
}

/* ====== 主按鈕（金黃色） ====== */
button.primary, .gr-button-primary {
    background: #244D82 !important;
    background-image: none !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: bold !important;
    font-size: 1.05em !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(36, 77, 130, 0.3) !important;
    transition: all 0.3s ease !important;
}
button.primary:hover, .gr-button-primary:hover {
    background: #1C3D6A !important;
    box-shadow: 0 6px 18px rgba(36, 77, 130, 0.45) !important;
}

/* ====== 一般按鈕 ====== */
button, .gr-button {
    background: #F8FAFF !important;
    background-image: none !important;
    color: #000000 !important;
    border: 2px solid #FFCE39 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}
button:hover, .gr-button:hover {
    background: #FFFAED !important;
    border-color: #E6B800 !important;
}

/* ====== 停止/刪除按鈕 ====== */
button.stop, .gr-button-stop {
    background: #C0392B !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* ====== 輸入框（白底 + 金黃邊框） ====== */
textarea, input, .gr-input, .gr-text-input {
    background-color: #F8FAFF !important;
    background-image: none !important;
    color: #000000 !important;
    border: 2px solid #FFCE39 !important;
    border-radius: 8px !important;
}
textarea:focus, input:focus {
    border-color: #E6B800 !important;
    box-shadow: 0 0 8px rgba(36, 77, 130, 0.3) !important;
}

/* ====== 圖片上傳區（白底 + 深藍框） ====== */
.upload-container, .gr-image, .gr-file,
div[data-testid="image"] .wrap,
div[data-testid="image"] .upload-area {
    border: 2px solid #244D82 !important;
    background-color: #F8FAFF !important;
    background-image: none !important;
    border-radius: 12px !important;
}

/* ====== Tab 標籤 ====== */
.tab-nav button {
    background: #F8FAFF !important;
    color: #000000 !important;
    border: 1px solid #FFCE39 !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: bold !important;
}
.tab-nav button.selected {
    background: #FFFAED !important;
    color: #FFCE39 !important;
    border-bottom: 3px solid #FFCE39 !important;
    font-weight: bold !important;
}

/* ====== 標題文字（深藍色） ====== */
h1, h2, h3, h4 {
    color: #000000 !important;
    background: transparent !important;
}

/* ====== 表格 ====== */
.gr-dataframe, table {
    background-color: #F8FAFF !important;
    color: #000000 !important;
    border: 2px solid #FFCE39 !important;
    border-radius: 8px !important;
}
table th {
    background-color: #244D82 !important;
    color: #FFF3D0 !important;
    font-weight: bold !important;
}
table tr:hover {
    background-color: #FFFAED !important;
}

/* ====== Markdown ====== */
.markdown-text, .gr-markdown {
    color: #000000 !important;
    background: transparent !important;
}

/* ====== Slider ====== */
input[type="range"] {
    accent-color: #FFCE39 !important;
}

/* ====== 強制清除所有漸層（排除 Banner） ====== */
*:not(.banner-wrap):not(.banner-wrap *),
*:not(.banner-wrap):not(.banner-wrap *)::before,
*:not(.banner-wrap):not(.banner-wrap *)::after {
    background-image: none !important;
}

/* ====== 區塊容器（白底 + 金黃邊） ====== */
.gr-block, .gr-box, .gr-group, .gr-form,
.block, .form, .panel,
div[class*="block"], div[class*="form"] {
    background-color: #F8FAFF !important;
    border-color: #FFCE39 !important;
}

/* ====== 圖片上傳區整塊統一 ====== */
div[data-testid="image"],
div[data-testid="image"] > div,
div[data-testid="image"] .wrap,
div[data-testid="image"] .upload-area,
div[data-testid="image"] .image-container,
div[data-testid="image"] .center,
div[data-testid="image"] button,
div[data-testid="image"] .icon-wrap,
.image-upload, .upload-container,
.gr-image, .gr-file {
    background-color: #F8FAFF !important;
    border: none !important;
    box-shadow: none !important;
}
div[data-testid="image"] {
    border: 2px solid #244D82 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ====== Label 標籤背景 ====== */
.label-wrap, .block-label,
div[data-testid="block-label"],
label {
    background-color: #F8FAFF !important;
}

/* ====== 區塊不溢出 ====== */
.gradio-container, .main, .wrap, .contain,
.gr-block, .block, .row, .column {
    overflow: hidden !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
.row > .column, .gr-row > .gr-column {
    min-width: 0 !important;
    overflow: hidden !important;
}

/* ====== 個人化設定卡片 ====== */
.pref-card {
    background: #F8FAFF !important;
    border: 2px solid #FFCE39 !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
}
/* ====== 所有按鈕統一深藍色（含 hover） ====== */
button.primary,
button.primary:hover,
button.primary:focus,
button.primary:active,
button.lg.primary,
button.lg.primary:hover,
button.lg.primary:focus,
button.lg.primary:active,
button.secondary,
button.secondary:hover,
button.secondary:focus,
button.secondary:active,
button.lg.secondary,
button.lg.secondary:hover,
button.lg.secondary:focus,
button.lg.secondary:active {
    background: #244D82 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(36, 77, 130, 0.3) !important;
}

/* ====== Radio 選取時填滿深藍色圓圈 ====== */
input[type="radio"] {
    appearance: none !important;
    -webkit-appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    border: 2px solid #254f81 !important;
    border-radius: 50% !important;
    background: #FFFFFF !important;
    cursor: pointer !important;
    position: relative !important;
    vertical-align: middle !important;
}

input[type="radio"]:checked {
    background: #254f81 !important;
    border: 2px solid #254f81 !important;
    box-shadow: inset 0 0 0 3px #FFFFFF !important;
}

/* 儲存後選取狀態也保持顏色 */
input[type="radio"]:checked:focus,
input[type="radio"]:checked:active,
input[type="radio"]:checked:hover {
    background: #254f81 !important;
    border: 2px solid #254f81 !important;
    box-shadow: inset 0 0 0 3px #FFFFFF !important;
    outline: none !important;
}
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
            return "<p style='color:#555555;'>目前沒有可查看的歷史菜單。</p>", None
        row_idx = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
        row = table_data.iloc[row_idx].tolist() if hasattr(table_data, "iloc") else table_data[row_idx]
        recipe_name = row[0]
        selected_id = None
        if history_items and row_idx < len(history_items):
            selected_id = history_items[row_idx].get("id")
        recipe = find_recipe_by_history_name(recipe_name)
        if not recipe:
            safe_name = html.escape(str(recipe_name))
            return f"<p style='color:#FFCE39;'>找不到「{safe_name}」的詳細食譜資料。</p>", selected_id

        n = recipe.get("nutrition", {})
        tags = "".join(
            f"<span class='tag'>{html.escape(str(tag))}</span> "
            for tag in recipe.get("tags", [])
        )
        required_items = "".join(
            f"<li style='color:#254f81; margin-bottom:6px;'>{html.escape(str(ing))}</li>"
            for ing in recipe.get("required_ingredients", [])
        )
        optional_items = "".join(        
            f"<li style='color:#254f81; margin-bottom:6px;'>{html.escape(str(ing))} <span style=\"color:#999; font-size:12px;\">可選</span></li>"
            for ing in recipe.get("optional_ingredients", [])
        )
        step_items = "".join(         
            f"<li style='color:#254f81; margin-bottom:8px; border-left:3px solid #FFCE39; padding-left:10px;'>{html.escape(str(step))}</li>"
            for step in recipe.get("steps", [])
        )
        gi_text = n.get("gi_index")
        gi_cell = (  
            f"<div style='background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;'>"
            f"<b style='color:#FFFFFF;display:block;'>GI 值</b>"
            f"<span style='color:#FFFFFF;margin-top:4px;display:block;'>{gi_text}</span></div>"
        ) if gi_text is not None else ""

        detail_html = f"""
<div class="recipe-detail" style="
    border: 2px solid #FFCE39;
    border-radius: 14px;
    padding: 22px;
    background: #F8FAFF;
    color: #254f81;
">
  <h3 style="color:#FFCE39; font-size:22px; margin:0 0 8px 0;">
    <span>{html.escape(str(recipe.get('emoji', '🍽️')))}</span>
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
    <div style="background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFFFFF;display:block;">時間</b>
      <span style="color:#FFFFFF;margin-top:4px;display:block;">{recipe.get('time_min', '-')} 分鐘</span>
    </div>
    <div style="background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFFFFF;display:block;">熱量</b>
      <span style="color:#FFFFFF;margin-top:4px;display:block;">{n.get('calories', '-')} kcal</span>
    </div>
    <div style="background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFFFFF;display:block;">蛋白質</b>
      <span style="color:#FFFFFF;margin-top:4px;display:block;">{n.get('protein_g', '-')} g</span>
    </div>
    <div style="background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFFFFF;display:block;">碳水</b>
      <span style="color:#FFFFFF;margin-top:4px;display:block;">{n.get('carb_g', '-')} g</span>
    </div>
    <div style="background:#254f81;border:none;border-radius:8px;padding:10px;text-align:center;">
      <b style="color:#FFFFFF;display:block;">脂肪</b>
      <span style="color:#FFFFFF;margin-top:4px;display:block;">{n.get('fat_g', '-')} g</span>
    </div>
    {gi_cell}
  </div>

  <h4 style="color:#FFCE39; margin:16px 0 8px; border-bottom:1px solid #254f81; padding-bottom:6px;">
    🥕 所需食材
  </h4>
  <ul style="padding-left:20px; margin:0 0 16px 0;">{required_items}{optional_items}</ul>

  <h4 style="color:#FFCE39; margin:16px 0 8px; border-bottom:1px solid #254f81; padding-bottom:6px;">
    👨‍🍳 料理步驟
  </h4>
  <ol style="padding-left:20px; margin:0;">{step_items}</ol>
</div>
"""
        return detail_html, selected_id
    except Exception as e:
        return f"<p style='color:#FFCE39;'>載入詳細內容失敗：{html.escape(str(e))}</p>", None


def delete_selected_history(selected_history_id):
    if not selected_history_id:
        rows, status, items = load_history()
        return (
            rows,
            "請先點選一筆要刪除的歷史菜單",
            "<p style='color:#555555;'>請點選左側食譜名稱查看詳細內容。</p>",
            None,
            items,
        )
    try:
        client.delete_history(USER_ID, int(selected_history_id))
        rows, status, items = load_history()
        return (
            rows,
            f"已刪除，{status}",
            "<p style='color:#555555;'>已刪除選取的歷史菜單。</p>",
            None,
            items,
        )
    except Exception as e:
        rows, status, items = load_history()
        return (
            rows,
            f"刪除失敗：{e}",
            "<p style='color:#FFCE39;'>刪除失敗，請重新選取後再試一次。</p>",
            None,
            items,
        )


# ============================================================
# 建立 Gradio 介面
# ============================================================
with gr.Blocks(

    title="菜單推薦器",
    theme=gr.themes.Soft(),
    css=CHINESE_ANIME_CSS,
) as demo:
    
    gr.HTML(make_banner())

    # ── Tab 1：生成今日菜單 ──
    with gr.Tab("生成今日菜單"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                    <h4 style="text-align:center; color:#B22222; margin:0;">📷 上傳冰箱照片</h4>
                    <p style="text-align:center; color:#B22222; margin:0; font-size:0.9em;">支援 JPG / PNG</p>
                """)
                image_input = gr.Image(
                    type="filepath",
                    label="上傳食材照片",
                    height=200,
                )
                recognize_btn    = gr.Button("食材清單", variant="secondary")
                recognize_status = gr.Markdown("")
                gr.HTML("""                
                <h4 style="text-align:center; color:#B22222; margin:0;">📝 食材清單</h4>
                <p style="text-align:center; color:#B22222; margin:0; font-size:0.9em;">可自行輸入或修改</p>
                """)
                ingredient_input = gr.Textbox(
                    label="食材清單",
                    placeholder="例如：雞胸肉、番茄、雞蛋",
                    lines=4,
                )
                generate_btn = gr.Button("開始進行推薦！", variant="primary")

            with gr.Column(scale=2):
                gr.HTML("""
                <div style="text-align:center; padding:6px 0;">
                    <div style="font-size:0.8em; color:#E6B800; letter-spacing:6px;">
                        ── 特級廚師鑑定完畢 ──
                    </div>
                    <h2 style="font-size:1.6em; margin:4px 0;"> 推薦料理排行 </h2>
                </div>""")
                with gr.Tabs():
                    with gr.Tab("Top 1 至尊料理"):
                        recipe_out_1 = gr.Markdown("")
                        save_btn_1   = gr.Button("💾 收錄此料理", size="sm")
                    with gr.Tab("Top 2 絕品料理"):
                        recipe_out_2 = gr.Markdown("")
                        save_btn_2   = gr.Button("💾 收錄此料理", size="sm")
                    with gr.Tab("Top 3 佳品料理"):
                        recipe_out_3 = gr.Markdown("")
                        save_btn_3   = gr.Button("💾 收錄此料理", size="sm")
                save_status = gr.Markdown("")

        recognize_btn.click(fn=run_image_recognition, inputs=[image_input], outputs=[ingredient_input, recognize_status])
        generate_btn.click(fn=generate_menu, inputs=[ingredient_input], outputs=[recipe_out_1, recipe_out_2, recipe_out_3])
        save_btn_1.click(fn=lambda md, ing: save_recipe(md, 0, ing), inputs=[recipe_out_1, ingredient_input], outputs=[save_status])
        save_btn_2.click(fn=lambda md, ing: save_recipe(md, 1, ing), inputs=[recipe_out_2, ingredient_input], outputs=[save_status])
        save_btn_3.click(fn=lambda md, ing: save_recipe(md, 2, ing), inputs=[recipe_out_3, ingredient_input], outputs=[save_status])

    # ── Tab 2：個人化設定 ──
    with gr.Tab("個人化設定"):
        gr.HTML("""     
        <div style="background-color:#FFFAED; padding:12px; border-radius:10px; text-align:center;">
        <span style="color:#B22222; font-weight:bold; font-size:1.05em;">
        設定您的專屬口味
        </span>
        </div>
        """)
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
            <div style="font-size:0.9em; color:#E6B800; letter-spacing:3px;">
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
                    "<p style='color:#555555;margin-top:10px;'>請點選左側食譜名稱<br>查看詳細內容</p>"
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