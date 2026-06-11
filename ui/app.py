"""
智慧菜單推薦器 — Gradio 版
配色：深藍 #1A3550 + 金黃 #D4920B
"""
import gradio as gr
import os
import json
import time
import html as html_lib

# ============================================================
# 路徑 & 設定
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(SCRIPT_DIR, "logo.png")

# ============================================================
# 自訂 CSS
# ============================================================
CUSTOM_CSS = """
/* ── 全域 ── */
.gradio-container {
    background: linear-gradient(180deg, #F8F6F0 0%, #FFFFFF 100%) !important;
    font-family: "Microsoft JhengHei", "Noto Sans TC", sans-serif !important;
}

/* ── 頁籤文字：深藍色（不再是白色看不到） ── */
.tabs > .tab-nav > button {
    color: #1A3550 !important;
    font-size: 1.05rem !important;
    font-weight: bold !important;
    border-bottom: 3px solid transparent !important;
    background: transparent !important;
}
.tabs > .tab-nav > button.selected {
    color: #D4920B !important;
    border-bottom: 3px solid #D4920B !important;
}

/* ── 頂部 Banner ── */
.banner {
    background: linear-gradient(135deg, #1A3550 0%, #2A5580 100%);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(26, 53, 80, 0.3);
}
.banner img { max-height: 120px; margin: 0 auto; }
.banner-title {
    color: #D4920B; font-size: 2.2rem; font-weight: bold;
    letter-spacing: 0.3rem; margin: 0.5rem 0 0.2rem 0;
}
.banner-subtitle { color: #C0CDD8; font-size: 1rem; }

/* ── 區塊標題 ── */
.section-header {
    background: linear-gradient(90deg, #D4920B, #E8A825);
    color: #FFFFFF; padding: 0.6rem 1rem; border-radius: 8px;
    font-size: 1.1rem; font-weight: bold; text-align: center;
    margin-bottom: 0.5rem;
}
.section-subheader {
    background: linear-gradient(90deg, #F0E6C8, #FFF8E7);
    color: #1A3550; padding: 0.4rem 1rem; border-radius: 8px;
    font-size: 0.95rem; text-align: center; margin-bottom: 0.5rem;
}

/* ── 上傳區域：白底 + 深藍框 ── */
.upload-area {
    background: #FFFFFF !important;
    border: 2px solid #1A3550 !important;
    border-radius: 12px !important;
}

/* ── 推薦結果區標題（推薦料理排行 = 亮黃色） ── */
.result-header {
    background: linear-gradient(135deg, #1A3550, #2A5580);
    padding: 1rem; border-radius: 12px;
    text-align: center; margin-bottom: 0.5rem;
}
.result-header h3 {
    margin: 0; font-size: 1.5rem; letter-spacing: 0.2rem;
    color: #FFD700;
}
.result-header p {
    color: #C0CDD8; margin: 0.3rem 0 0 0; font-size: 0.9rem;
}

/* ── 推薦子頁籤文字 ── */
.result-tabs .tab-nav button {
    color: #1A3550 !important; font-weight: bold !important;
}
.result-tabs .tab-nav button.selected {
    color: #D4920B !important;
    border-bottom: 3px solid #D4920B !important;
}

/* ── 推薦卡片 ── */
.dish-card-gold {
    background: #FFFFFF; border: 2px solid #D4920B;
    border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
    box-shadow: 0 3px 12px rgba(212, 146, 11, 0.15);
}
.dish-card-silver {
    background: #FFFFFF; border: 2px solid #8A9BAA;
    border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
    box-shadow: 0 3px 12px rgba(138, 155, 170, 0.15);
}
.dish-card-bronze {
    background: #FFFFFF; border: 2px solid #A0734A;
    border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
    box-shadow: 0 3px 12px rgba(160, 115, 74, 0.15);
}

/* ── 排名橫幅 ── */
.rank-gold {
    background: linear-gradient(135deg, #D4920B, #E8A825);
    color: #FFF; font-weight: bold; font-size: 1.2rem;
    padding: 0.5rem 1rem; border-radius: 8px;
    text-align: center; margin-bottom: 0.8rem;
}
.rank-silver {
    background: linear-gradient(135deg, #7A8B9A, #9AABBA);
    color: #FFF; font-weight: bold; font-size: 1.2rem;
    padding: 0.5rem 1rem; border-radius: 8px;
    text-align: center; margin-bottom: 0.8rem;
}
.rank-bronze {
    background: linear-gradient(135deg, #A0734A, #C08A5A);
    color: #FFF; font-weight: bold; font-size: 1.2rem;
    padding: 0.5rem 1rem; border-radius: 8px;
    text-align: center; margin-bottom: 0.8rem;
}

/* ── 菜名 / 匹配度 / 材料 / 步驟 ── */
.dish-name { color: #1A3550; font-size: 1.8rem; font-weight: bold; margin: 0.3rem 0; }
.match-badge {
    background: linear-gradient(135deg, #1A3550, #2A5580);
    color: #F0E6C8; padding: 0.6rem 1rem; border-radius: 10px;
    text-align: center; display: inline-block;
}
.match-badge .rate { font-size: 1.8rem; font-weight: bold; color: #D4920B; }
.ing-tag {
    display: inline-block; background: #1A3550; color: #F0E6C8;
    padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0.2rem;
    font-size: 0.95rem;
}
.step-item {
    background: #FFFFFF; border-left: 4px solid #D4920B;
    padding: 0.6rem 1rem; margin: 0.4rem 0;
    border-radius: 0 8px 8px 0; color: #1A3550; font-size: 1.05rem;
}

/* ── 個人化設定：白底 + 金黃框 ── */
.pref-card {
    background: #FFFFFF; border: 2px solid #D4920B;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
}

/* ── 歷史卡片（可展開） ── */
.history-item {
    background: #FFFFFF; border: 2px solid #D4920B;
    border-radius: 10px; overflow: hidden;
}
.history-item summary {
    padding: 0.8rem 1.2rem; cursor: pointer; color: #1A3550;
    font-size: 1.05rem; font-weight: 500;
    background: linear-gradient(90deg, #FFFDF5, #FFF8E7);
    list-style: none;
    display: flex; justify-content: space-between; align-items: center;
}
.history-item summary::-webkit-details-marker { display: none; }
.history-item summary::after {
    content: "▶ 點擊展開"; color: #D4920B;
    font-size: 0.85rem; font-weight: bold;
}
.history-item[open] summary::after { content: "▼ 收合"; }
.history-item .detail-content {
    padding: 1rem 1.2rem; border-top: 1px solid #F0E6C8; background: #FFFFFF;
}
.history-item .dish-detail-name {
    color: #1A3550; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;
}
.history-item .section-title {
    color: #1A3550; font-size: 1.1rem; font-weight: bold;
    margin: 0.8rem 0 0.4rem 0;
}
.history-name { color: #1A3550; font-weight: bold; font-size: 1.1rem; }
.history-meta { color: #666; font-size: 0.95rem; }

/* ── 按鈕樣式 ── */
.recommend-btn {
    background: linear-gradient(135deg, #D4920B, #E8A825) !important;
    color: #FFFFFF !important; font-size: 1.2rem !important;
    font-weight: bold !important; border: none !important;
    border-radius: 10px !important; padding: 0.8rem !important;
    box-shadow: 0 4px 12px rgba(212, 146, 11, 0.4) !important;
}
.save-btn {
    background: linear-gradient(135deg, #1A3550, #2A5580) !important;
    color: #D4920B !important; font-weight: bold !important;
    border-radius: 8px !important;
}

/* ── 空狀態 ── */
.empty-state {
    text-align: center; padding: 2rem; color: #8899AA; font-size: 1.1rem;
}
"""

# ============================================================
# API 呼叫（模擬版，正式串接時替換）
# ============================================================
def call_analyze_api(image_path):
    # 正式版取消下方註解：
    # import requests
    # try:
    #     with open(image_path, "rb") as f:
    #         resp = requests.post("http://localhost:8000/analyze",
    #                              files={"image": (os.path.basename(image_path), f)}, timeout=60)
    #         resp.raise_for_status()
    #         return resp.json().get("ingredients", "")
    # except Exception as e:
    #     return f"辨識失敗：{e}"
    time.sleep(1)
    return "雞蛋 x3\n牛奶 500ml\n紅蘿蔔 x2\n洋蔥 x1\n青椒 x2\n豬肉片 200g\n白飯 1碗"


def call_recommend_api(ingredients_text, preferences):
    # 正式版取消下方註解：
    # import requests
    # try:
    #     data = {"ingredients_text": ingredients_text,
    #             "preferences": json.dumps(preferences, ensure_ascii=False)}
    #     resp = requests.post("http://localhost:8000/recommend", data=data, timeout=90)
    #     resp.raise_for_status()
    #     dishes = resp.json()
    #     if isinstance(dishes, list):
    #         dishes.sort(key=lambda d: d.get("match_rate", 0), reverse=True)
    #         return dishes
    # except Exception as e:
    #     return []
    time.sleep(1)
    return [
        {
            "name": "青椒炒肉絲", "match_rate": 92,
            "ingredients": ["豬肉片 200g", "青椒 x2", "紅蘿蔔 x1",
                            "洋蔥 半顆", "醬油 2大匙", "米酒 1大匙", "太白粉 適量"],
            "steps": ["1. 豬肉片切絲，加醬油、米酒、太白粉醃製 15 分鐘。",
                      "2. 青椒、紅蘿蔔、洋蔥洗淨切絲備用。",
                      "3. 熱鍋加油，肉絲炒至變色後盛出。",
                      "4. 同鍋爆香洋蔥，加入紅蘿蔔翻炒。",
                      "5. 加入青椒快炒 30 秒，倒回肉絲。",
                      "6. 加調味料拌炒均勻，盛盤上桌。"],
        },
        {
            "name": "洋蔥炒蛋", "match_rate": 85,
            "ingredients": ["雞蛋 x3", "洋蔥 x1", "鹽 適量", "油 適量"],
            "steps": ["1. 雞蛋打散，加少許鹽調味。", "2. 洋蔥切絲備用。",
                      "3. 熱鍋加油，先炒洋蔥至透明。", "4. 倒入蛋液，翻炒至凝固即可。"],
        },
        {
            "name": "紅蘿蔔炒蛋", "match_rate": 78,
            "ingredients": ["雞蛋 x2", "紅蘿蔔 x2", "鹽 適量", "油 適量"],
            "steps": ["1. 紅蘿蔔去皮切絲。", "2. 雞蛋打散備用。",
                      "3. 熱鍋加油，先炒紅蘿蔔至軟。", "4. 倒入蛋液翻炒至熟，調味即可。"],
        },
    ]


# ============================================================
# 功能函式
# ============================================================
def format_dish_html(dish, rank_index):
    """將一道菜格式化為 HTML 卡片"""
    rank_configs = [
        ("第 1 推薦 — 至尊料理", "rank-gold", "dish-card-gold"),
        ("第 2 推薦 — 絕品料理", "rank-silver", "dish-card-silver"),
        ("第 3 推薦 — 佳品料理", "rank-bronze", "dish-card-bronze"),
    ]
    label, rank_cls, card_cls = (
        rank_configs[rank_index]
        if rank_index < len(rank_configs)
        else (f"第 {rank_index+1} 推薦", "rank-bronze", "dish-card-bronze")
    )
    ing_tags = "".join(
        f'<span class="ing-tag">{html_lib.escape(i)}</span>'
        for i in dish["ingredients"]
    )
    steps_html = "".join(
        f'<div class="step-item">{html_lib.escape(s)}</div>'
        for s in dish["steps"]
    )
    return f"""
    <div class="{card_cls}">
        <div class="{rank_cls}">{label}</div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="dish-name">{html_lib.escape(dish['name'])}</div>
            <div class="match-badge">
                食材匹配度<br><span class="rate">{dish['match_rate']}%</span>
            </div>
        </div>
        <div style="margin-top:0.8rem;">
            <div style="color:#1A3550; font-size:1.2rem; font-weight:bold; margin-bottom:0.4rem;">
                所需材料
            </div>
            {ing_tags}
        </div>
        <div style="margin-top:0.8rem;">
            <div style="color:#1A3550; font-size:1.2rem; font-weight:bold; margin-bottom:0.4rem;">
                料理步驟
            </div>
            {steps_html}
        </div>
    </div>
    """


def make_history_card_html(dish):
    """生成單筆歷史菜單的可展開 HTML 卡片"""
    name_esc = html_lib.escape(dish["name"])
    ing_tags = "".join(
        f'<span class="ing-tag">{html_lib.escape(ig)}</span>'
        for ig in dish["ingredients"]
    )
    steps_html = "".join(
        f'<div class="step-item">{html_lib.escape(s)}</div>'
        for s in dish["steps"]
    )
    ing_preview = ", ".join(dish["ingredients"][:4])
    if len(dish["ingredients"]) > 4:
        ing_preview += "..."

    return f"""
    <details class="history-item">
        <summary>
            <span>
                <span class="history-name">{name_esc}</span>
                <span class="history-meta">
                    &nbsp;|&nbsp;契合度 {dish['match_rate']}%
                    &nbsp;|&nbsp;材料：{html_lib.escape(ing_preview)}
                </span>
            </span>
        </summary>
        <div class="detail-content">
            <div class="dish-detail-name">{name_esc}</div>
            <div class="match-badge" style="margin-bottom:0.8rem;">
                食材匹配度 <span class="rate">{dish['match_rate']}%</span>
            </div>
            <div class="section-title">所需材料</div>
            {ing_tags}
            <div class="section-title" style="margin-top:1rem;">料理步驟</div>
            {steps_html}
        </div>
    </details>
    """


def analyze_image(image):
    if image is None:
        return "請先上傳冰箱照片"
    return call_analyze_api(image)


def do_recommend(image, ingredients, diet, allergies, fitness, blood_sugar):
    if not ingredients or not ingredients.strip():
        empty = '<div class="empty-state">請先輸入食材或上傳照片分析</div>'
        return empty, empty, empty, []

    preferences = {
        "diet": diet,
        "allergies": allergies if allergies else [],
        "fitness": fitness,
        "blood_sugar": blood_sugar,
    }
    dishes = call_recommend_api(ingredients, preferences)

    if not dishes:
        empty = '<div class="empty-state">找不到適合的推薦菜單</div>'
        return empty, empty, empty, []

    results = []
    for i in range(3):
        if i < len(dishes):
            results.append(format_dish_html(dishes[i], i))
        else:
            results.append('<div class="empty-state">暫無更多推薦</div>')

    return results[0], results[1], results[2], dishes


def save_dish_n(n, current_dishes, saved_menus):
    """儲存第 n 道推薦菜到歷史"""
    saved_menus = list(saved_menus) if saved_menus else []
    if n < len(current_dishes):
        dish = current_dishes[n]
        if not any(m["name"] == dish["name"] for m in saved_menus):
            new_saved = [dish.copy()] + saved_menus
            gr.Info(f"「{dish['name']}」已儲存！")
            return new_saved
        gr.Info(f"「{dish['name']}」已在歷史菜單中")
        return saved_menus
    gr.Warning("沒有可儲存的菜單")
    return saved_menus


def save_dish_1(cd, sv):
    return save_dish_n(0, cd, sv)


def save_dish_2(cd, sv):
    return save_dish_n(1, cd, sv)


def save_dish_3(cd, sv):
    return save_dish_n(2, cd, sv)


def make_banner():
    """生成頂部 Banner HTML（含 Logo）"""
    logo_html = ""
    if os.path.isfile(LOGO_PATH):
        import base64
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{b64}" style="max-height:130px;">'
    else:
        logo_html = ""

    return f"""
    <div class="banner">
        {logo_html}
        <div class="banner-title">菜單推薦器</div>
        <div class="banner-subtitle">
            上傳冰箱照片或輸入食材，為你推薦出相似度最高的三道料理
        </div>
    </div>
    """


# ============================================================
# 建立 Gradio 介面
# ============================================================
with gr.Blocks(
    css=CUSTOM_CSS,
    title="智慧菜單推薦器",
    theme=gr.themes.Soft(),
) as demo:

    # ── 全域狀態 ──
    current_dishes_state = gr.State([])
    saved_state = gr.State([])

    # ── Banner ──
    gr.HTML(make_banner())

    # ── 三個主頁籤 ──
    with gr.Tabs():

        # ==========================================
        # 頁籤 1：生成今日菜單
        # ==========================================
        with gr.TabItem("生成今日菜單"):
            with gr.Row():

                # ── 左側：上傳 & 食材 ──
                with gr.Column(scale=1):
                    gr.HTML('<div class="section-header">上傳冰箱照片</div>')
                    gr.HTML('<div class="section-subheader">支援 JPG / PNG</div>')
                    img_input = gr.Image(
                        label="上傳食材照片",
                        type="filepath",
                        height=250,
                        elem_classes=["upload-area"],
                    )
                    analyze_btn = gr.Button("辨識食材", variant="secondary")

                    gr.HTML('<div class="section-header">食材清單</div>')
                    gr.HTML('<div class="section-subheader">可自行輸入或修改</div>')
                    ingredients_input = gr.Textbox(
                        label="食材清單",
                        placeholder="例如：雞胸肉、番茄、雞蛋\n每行一項食材",
                        lines=6,
                    )
                    recommend_btn = gr.Button(
                        "開始進行推薦！",
                        variant="primary",
                        elem_classes=["recommend-btn"],
                    )

                # ── 右側：推薦結果 ──
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="result-header">
                        <p>—— 情報廚師鑑定完畢 ——</p>
                        <h3>推薦料理排行</h3>
                    </div>
                    """)

                    with gr.Tabs(elem_classes=["result-tabs"]):
                        with gr.TabItem("Top 1 至尊料理"):
                            result_1 = gr.HTML(
                                '<div class="empty-state">等待推薦中...</div>'
                            )
                            save_btn_1 = gr.Button(
                                "收藏此料理", elem_classes=["save-btn"]
                            )

                        with gr.TabItem("Top 2 絕品料理"):
                            result_2 = gr.HTML(
                                '<div class="empty-state">等待推薦中...</div>'
                            )
                            save_btn_2 = gr.Button(
                                "收藏此料理", elem_classes=["save-btn"]
                            )

                        with gr.TabItem("Top 3 佳品料理"):
                            result_3 = gr.HTML(
                                '<div class="empty-state">等待推薦中...</div>'
                            )
                            save_btn_3 = gr.Button(
                                "收藏此料理", elem_classes=["save-btn"]
                            )

        # ==========================================
        # 頁籤 2：個人化設定
        # ==========================================
        with gr.TabItem("個人化設定"):
            gr.HTML('<div class="section-header">個人化偏好設定</div>')

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 1. 飲食類型")
                    with gr.Group(elem_classes=["pref-card"]):
                        diet_radio = gr.Radio(
                            choices=["葷", "素"], value="葷", label="飲食類型"
                        )
                with gr.Column():
                    gr.Markdown("### 2. 過敏原（可複選）")
                    with gr.Group(elem_classes=["pref-card"]):
                        allergy_check = gr.CheckboxGroup(
                            choices=["海鮮", "蛋奶", "酒精", "堅果"],
                            value=[],
                            label="過敏原",
                        )

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 3. 減脂 / 增肌需求")
                    with gr.Group(elem_classes=["pref-card"]):
                        fitness_radio = gr.Radio(
                            choices=["是（減脂）", "是（增肌）", "否"],
                            value="否",
                            label="健身目標",
                        )
                with gr.Column():
                    gr.Markdown("### 4. 是否需控制血糖")
                    with gr.Group(elem_classes=["pref-card"]):
                        sugar_radio = gr.Radio(
                            choices=["是", "否"], value="否", label="血糖控制"
                        )

            gr.HTML(
                '<div style="text-align:center; color:#8899AA; margin-top:1rem;">'
                "設定會自動套用到下次推薦，不需額外儲存"
                "</div>"
            )

        # ==========================================
        # 頁籤 3：歷史菜單（每筆旁有刪除按鈕）
        # ==========================================
        with gr.TabItem("歷史菜單"):
            gr.HTML('<div class="section-header">歷史菜單</div>')

            # 使用 @gr.render 動態渲染每筆歷史菜單 + 刪除按鈕
            @gr.render(inputs=[saved_state])
            def render_history(menus):
                if not menus:
                    gr.HTML(
                        '<div class="empty-state">'
                        "尚未儲存任何菜單<br>"
                        '推薦完成後點「收藏此料理」即可在這裡查看'
                        "</div>"
                    )
                    return

                for i, dish in enumerate(menus):
                    with gr.Row():
                        with gr.Column(scale=6):
                            gr.HTML(make_history_card_html(dish))
                        with gr.Column(scale=1, min_width=80):
                            del_btn = gr.Button(
                                "刪除", variant="stop", size="sm"
                            )
                            del_btn.click(
                                fn=lambda s, idx=i: s[:idx] + s[idx + 1 :],
                                inputs=[saved_state],
                                outputs=[saved_state],
                            )

            # 刪除所有菜單按鈕
            clear_all_btn = gr.Button("刪除所有菜單", variant="stop")

    # ============================================================
    # 事件綁定
    # ============================================================

    # 辨識食材
    analyze_btn.click(
        fn=analyze_image,
        inputs=[img_input],
        outputs=[ingredients_input],
    )

    # 開始推薦
    recommend_btn.click(
        fn=do_recommend,
        inputs=[
            img_input,
            ingredients_input,
            diet_radio,
            allergy_check,
            fitness_radio,
            sugar_radio,
        ],
        outputs=[result_1, result_2, result_3, current_dishes_state],
    )

    # 儲存按鈕
    save_btn_1.click(
        fn=save_dish_1,
        inputs=[current_dishes_state, saved_state],
        outputs=[saved_state],
    )
    save_btn_2.click(
        fn=save_dish_2,
        inputs=[current_dishes_state, saved_state],
        outputs=[saved_state],
    )
    save_btn_3.click(
        fn=save_dish_3,
        inputs=[current_dishes_state, saved_state],
        outputs=[saved_state],
    )

    # 刪除所有菜單
    clear_all_btn.click(fn=lambda: [], outputs=[saved_state])


# ============================================================
# 啟動
# ============================================================
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )