# models/vision/recognizer.py
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

INGREDIENT_LIST = [
    "雞蛋", "番茄", "青江菜", "肉片", "豆腐",
    "牛奶", "洋蔥", "紅蘿蔔", "馬鈴薯", "蒜頭",
    "花椰菜", "高麗菜", "菠菜", "豬肉", "雞肉",
    "魚", "蝦", "豆芽", "香菇", "木耳",
]

ZH_TO_EN = {
    "雞蛋": "egg", "番茄": "tomato", "青江菜": "bok choy",
    "肉片": "pork slices", "豆腐": "tofu", "牛奶": "milk bottle",
    "洋蔥": "onion", "紅蘿蔔": "carrot", "馬鈴薯": "potato",
    "蒜頭": "garlic", "花椰菜": "broccoli", "高麗菜": "cabbage",
    "菠菜": "spinach", "豬肉": "pork meat", "雞肉": "chicken meat",
    "魚": "fish", "蝦": "shrimp", "豆芽": "bean sprouts",
    "香菇": "shiitake mushroom", "木耳": "black fungus",
}

class FoodRecognizer:
    def __init__(self):
        print("載入 CLIP 模型...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.eval()
        self.labels_en = [
            f"a photo of {ZH_TO_EN[zh]}" for zh in INGREDIENT_LIST
        ]
        print("✅ CLIP 模型載入完成")

    # ===============================================
    # 調高conf_threshold可以減少誤判，
    # 0.0~1信心度的門檻。0.08~0.1是預設值
    # 0.20以上是超嚴格可能甚麼都跑不到出來
    # ===============================================
    def recognize(self, image_path: str,
                  conf_threshold: float = 0.08) -> list[dict]:

        img = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            text=self.labels_en,
            images=img,
            return_tensors="pt",
            padding=True,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        detections = []
        for zh_name, prob in zip(INGREDIENT_LIST, probs.tolist()):
            if prob >= conf_threshold:
                detections.append({
                    "name":       zh_name,
                    "confidence": round(prob, 3),
                    "bbox":       [0, 0, 0, 0],
                })

        detections.sort(key=lambda x: x["confidence"], reverse=True)
        return detections[:5]