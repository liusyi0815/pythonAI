# PythonAITest 食材辨識與菜單推薦系統

這是一個以 Python 開發的食材辨識與菜單推薦專案。使用者可以上傳食材照片或手動輸入食材，系統會辨識食材並依照使用者偏好推薦料理，也能儲存、查看與刪除歷史菜單。

## 功能

- 上傳圖片辨識食材
- 手動輸入食材清單
- 依照食材推薦菜單
- 支援個人化設定，例如飲食類型、目標、過敏食材與份量
- 儲存推薦菜單到歷史紀錄
- 查看歷史菜單的做法與營養資訊
- 刪除已儲存的歷史菜單

## 技術架構

- Frontend: Gradio
- Backend: FastAPI
- Vision: CLIP image-text matching
- Recommendation: PyTorch recommender model
- Database: SQLite
- Data: JSON recipes and ingredient vocabulary

## 專案結構

```text
PythonAITest/
├─ api/                    FastAPI 後端 API
│  ├─ main.py
│  ├─ dependencies.py
│  ├─ schemas.py
│  └─ routes/
│     ├─ recognize.py
│     ├─ recommend.py
│     ├─ profile.py
│     └─ history.py
├─ data/                   食譜、資料庫與資料處理程式
│  ├─ recipes.json
│  ├─ ingredient_vocab.json
│  ├─ database.py
│  ├─ repository.py
│  └─ prepare_recommender_dataset.py
├─ models/                 模型程式與推薦模型
│  ├─ recommender.pt
│  ├─ vision/
│  │  └─ recognizer.py
│  └─ recommender/
│     ├─ model.py
│     ├─ predictor.py
│     ├─ profile_encoder.py
│     ├─ train.py
│     └─ vocab.py
├─ ui/                     Gradio 前端
│  ├─ app.py
│  ├─ api_client.py
│  └─ components.py
├─ .gitignore
└─ README.md
```

## 不上傳到 Git 的內容

以下內容屬於本機環境、暫存資料、訓練資料或大型模型檔，不建議推上 GitHub/GitLab：

- `.venv/`
- `.gradio/`
- `__pycache__/`
- `data/users.db`
- `data/uploads/`
- `data/raw/`
- `data/classifier/`
- `data/labeled/`
- `data/yolo_dataset/`
- `data/yolo_augmented/`
- `runs/`
- `train/`
- `models/efficientnet_food.pt`
- YOLO 權重與訓練輸出
- `data/recommender_train.json`

目前 `.gitignore` 有保留 `models/recommender.pt`，因為它是推薦系統需要的小型模型檔。如果不想上傳任何模型權重，可以移除 `.gitignore` 裡的 `!models/recommender.pt`。

## 安裝套件

建議使用 Python 3.11。

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi uvicorn gradio requests pillow torch torchvision transformers
```

如果有另外整理 `requirements.txt`，也可以改用：

```powershell
pip install -r requirements.txt
```

## 啟動後端

```powershell
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

後端啟動後會初始化 SQLite 資料庫，並載入圖片辨識模型與推薦模型。

## 啟動前端

另開一個終端機：

```powershell
python ui/app.py
```

預設 Gradio 會在：

```text
http://localhost:7860
```

## 推薦模型訓練

如果修改了食譜或食材資料，可以重新產生訓練資料並訓練推薦模型：

```powershell
python data/prepare_recommender_dataset.py
python models/recommender/train.py
```

訓練完成後會產生：

```text
models/recommender.pt
```

## 推上 GitHub 或 GitLab

第一次推送前，先設定 Git 身分：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的email@example.com"
```

確認目前會被提交的檔案：

```powershell
git status
```

加入檔案：

```powershell
git add .gitignore README.md api data models ui
```

如果你已經刪除 YOLO 舊檔，也一起提交刪除狀態：

```powershell
git add -A
```

建立 commit：

```powershell
git commit -m "Prepare CLIP recipe recommender project"
```

連接遠端 repository。請把網址換成你的 GitHub 或 GitLab repo：

```powershell
git remote add origin https://github.com/你的帳號/你的repo.git
git branch -M main
git push -u origin main
```

如果已經設定過 `origin`，改用：

```powershell
git remote set-url origin https://github.com/你的帳號/你的repo.git
git push -u origin main
```

## 注意事項

- `data/users.db` 是本機資料庫，不會上傳。其他人 clone 專案後，啟動後端時會自動建立。
- CLIP 模型會透過 Hugging Face Transformers 載入，第一次執行可能需要下載模型。
- 如果 GitHub 顯示檔案太大，請確認 `.venv/`、`runs/`、資料集資料夾和大型 `.pt` 權重沒有被加入 Git。
