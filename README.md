models/loader.py已停用(原使用Yolov8訓練+EfficientNet 分類)
prepare_classifier.py已停用(原使用Yolov8訓練+EfficientNet 分類)
## 簡介
結合深度學習與個人化推薦的智慧菜單系統，核心目標是解決兩個日常痛點：冰箱食材剩餘浪費，以及每天不知道要吃什麼的選擇困難。
## 系統功能
使用者透過兩種方式告訴系統冰箱裡有什麼。
1. 拍照上傳，系統會用 CLIP 視覺模型自動辨識圖片中的食材
2. 手動輸入食材清單。輸入完成後，系統會根據你的個人設定（葷素偏好、飲食目標、過敏原、幾人份）篩選並推薦最符合的三道料理
3. 每道料理附上完整的食材清單、營養資訊與製作步驟。
4. 並且推薦過的菜單可以儲存到歷史紀錄，方便日後查閱。
5. 在歷史紀錄中也可刪除紀錄
## 技術架構
系統分為四層。前端使用 Gradio 建立網頁介面，後端使用 FastAPI 處理 API 請求，深度學習層包含 CLIP 圖像辨識模型與 Transformer 推薦模型，資料層使用 SQLite 儲存使用者資料與歷史記錄，食譜以 JSON 格式儲存。
圖像辨識採用 OpenAI 開源的 CLIP 模型，透過計算圖片與食材文字描述的相似度來辨識食材，不需大量標注資料也能有效運作。推薦系統採用規則式符合率排序，優先推薦使用者已有食材比例最高的料理，同時套用葷素與過敏原的硬性過濾確保推薦結果符合。
## 個人化特色
系統支援高度個人化設定，包含葷食、全素、蛋素、奶素、蛋奶素等飲食類型，以及減脂、增肌、血糖控制、低鈉等飲食目標，還有花生、海鮮、麩質、乳製品、堅果等常見過敏原的篩選。這些設定會在每次推薦時自動套用，確保推薦結果符合個人健康需求。
## 開發環境
Python 3.11、PyTorch 2.6、FastAPI、Gradio、HuggingFace Transformers、SQLite
## 主架構
```text
PythonAITest/
├─ ui/                 使用者畫面
├─ api/                後端 API
├─ models/             AI 模型和模型程式
├─ data/               食譜、使用者資料、訓練資料
├─ runs/               YOLO 訓練結果
├─ train/              訓練相關資料夾
├─ .venv/              Python 虛擬環境
├─ .gradio/            Gradio 介面產生的設定/暫存
├─ .git/               Git 版本控制
├─ yolov8n.pt          YOLO 預訓練模型
├─ yolo26n.pt          另一個 YOLO 模型檔
└─ .gitignore          Git 忽略清單
```
## 次架構
### ui/：使用者看到的畫面
```text
ui/
├─ app.py
├─ api_client.py
└─ components.py
```
### api/：後端，負責接收請求
```text
api/
├─ main.py
├─ dependencies.py
├─ schemas.py
└─ routes/
   ├─ recognize.py
   ├─ recommend.py
   ├─ profile.py
   └─ history.py
```
### models/：AI 模型區
```text
models/
├─ loader.py
├─ efficientnet_food.pt
├─ recommender.pt
├─ yolo_food.pt
├─ vision/
│  ├─ recognizer.py
│  └─ train_classifier.py
└─ recommender/
   ├─ model.py
   ├─ predictor.py
   ├─ profile_encoder.py
   └─ train.py
```
### data/：資料區
```text
data/
├─ recipes.json
├─ users.db
├─ recommender_train.json
├─ repository.py
├─ database.py
├─ classifier/
├─ labeled/
├─ raw/
├─ uploads/
├─ yolo_dataset/
├─ yolo_augmented/
├─ prepare_classifier.py
├─ prepare_recommender_dataset.py
├─ prepare_yolo_dataset.py
├─ download_datasets.py
├─ augment.py
└─ annotate_yolo.py
```
### runs/ 和 train/：訓練產物
```text
runs/
YOLO 訓練或測試後自動產生的結果。
裡面有模型權重、訓練紀錄、預測圖片。
train/
目前是空的
```
### 其他
```text
.venv/                Python 套件環境
.gradio/              Gradio 介面工具產生的暫存/設定
.git/                 版本控制資料
__pycache__/          Python 自動產生的快取
```

## 細則
### UI前端
- `ui/app.py`前端主程式。使用者看到的操作畫面大多在這裡，例如上傳圖片、輸入食材、按下推薦按鈕、顯示推薦結果。
- `ui/api_client.py`前端跟後端溝通的工具。
它會把使用者的操作送到 API，例如：
上傳圖片 → 呼叫 /recognize/image
輸入食材 → 呼叫 /recommend/menu
更新個人資料 → 呼叫 /profile
- `ui/components.py`負責把推薦結果整理成比較好看的格式  → 食譜資料轉成 Markdown 顯示。
### API後端
- `api/main.py`後端程式的入口。它會啟動 FastAPI，並把各種路由掛上去。
- `api/dependencies.py`放共用物件，例如取得圖片辨識模型、推薦模型、資料庫操作工具。
- `api/schemas.py`定義資料格式
- `api/routes/recognize.py`圖片辨識 API。
使用者上傳食材圖片後，這裡會接收圖片，存到data/uploads/，再呼叫模型辨識圖片裡有哪些食材。
- `api/routes/recommend.py`菜單推薦 API。會拿到使用者食材清單和使用者資料，再呼叫推薦模型，最後回傳推薦菜單。
- `api/routes/profile.py`使用者個人設定 API，如葷素、減脂、血糖控制、過敏食材等。
- `api/routes/history.py`歷史紀錄 API。例如儲存使用者看過或收藏過的菜單。
### AI 模型
- `models/loader.py`負責載入模型。載入 YOLO、EfficientNet、Transformer。
- `models/efficientnet_food.pt`訓練好的食材圖片分類模型。[name=目前沒用到]
- `models/recommender.pt`訓練好的菜單Transformer 推薦模型。
- `models/vision/recognizer.py`圖片辨識邏輯。負責拿圖片去判斷裡面有什麼食材。
- `models/vision/train_classifier.py`訓練圖片分類模型用的程式。
- `models/recommender/model.py`Transformer 推薦模型的神經網路架構。也就是推薦系統的大腦結構。
- `models/recommender/predictor.py`實際拿來做推薦的程式。它會把食材和使用者條件丟進模型，算出推薦菜單。
- `models/recommender/profile_encoder.py`把使用者條件轉成模型看得懂的數字。
    ```text
    vegan → 數字向量
    lose_fat → 數字向量
    peanut allergy → 數字向量
    ```
- `models/recommender/train.py`訓練推薦模型用的程式。
### data資料
- `data/recipes.json`食譜資料。有菜名、需要的食材、營養資訊、步驟、標籤等。
- `data/users.db`SQLite 資料庫。存使用者資料、飲食偏好、歷史紀錄。
- `data/recommender_train.json`推薦模型的訓練資料。檔案很大，是拿來訓練推薦系統的。
- `data/repository.py`資料讀寫工具。例如讀取使用者、更新個人資料、讀取食譜、儲存歷史紀錄。
- `data/database.py`建立資料庫表格。如 users、history、fridge。
- `data/classifier/`圖片分類模型的訓練資料。裡面有很多食材圖片
- `data/raw/`原始資料集，還沒整理或處理前的圖片資料。
- `data/uploads/`使用者上傳圖片時，後端暫時存放圖片的地方。
- `data/download_datasets.py`下載資料集用的程式。
