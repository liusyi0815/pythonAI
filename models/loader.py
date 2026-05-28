# models/loader.py
import torch
from functools import lru_cache

@lru_cache(maxsize=1)
def load_vision_model():
    from ultralytics import YOLO
    # 直接用官方預訓練模型，會自動下載 yolov8n.pt
    return YOLO("yolov8n.pt")

@lru_cache(maxsize=1)
def load_classifier_model():
    import torchvision.models as models
    import torch.nn as nn
    
    # 如果 efficientnet 還沒訓練完，先用預訓練模型頂著
    model = models.efficientnet_b4(weights="IMAGENET1K_V1")
    
    model_path = "models/efficientnet_food.pt"
    try:
        state = torch.load(model_path, map_location="cpu")
        # 嘗試載入自訓練權重
        in_features = model.classifier[1].in_features
        num_classes = list(state.values())[-1].shape[0]
        model.classifier[1] = nn.Linear(in_features, num_classes)
        model.load_state_dict(state)
        print(f"✅ 載入自訓練分類器：{num_classes} 類")
    except Exception as e:
        print(f"⚠️  使用 ImageNet 預訓練分類器（{e}）")
    
    model.eval()
    return model

@lru_cache(maxsize=1)
def load_recommender_model():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models.recommender.model import MenuRecommender
    import json

    model_path = "models/recommender.pt"
    
    # 從訓練資料推算食譜數量
    try:
        with open("data/recommender_train.json", encoding="utf-8") as f:
            samples = json.load(f)
        num_recipes = max(s["label"] for s in samples) + 1
    except Exception:
        num_recipes = 5  # 對應 recipes.json 的食譜數量

    model = MenuRecommender(num_recipes=num_recipes)
    
    try:
        state = torch.load(model_path, map_location="cpu")
        model.load_state_dict(state)
        print(f"✅ 載入推薦模型：{num_recipes} 道食譜")
    except Exception as e:
        print(f"⚠️  推薦模型使用隨機初始權重（{e}）")
    
    model.eval()
    return model