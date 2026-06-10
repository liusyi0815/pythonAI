# models/vision/recognizer.py
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


# CLIP works better with English prompts, but the app should show Chinese names.
# Keep both ingredient labels and prepared-dish labels so cooked egg dishes do not
# have to collapse back to the raw ingredient "雞蛋".
LABEL_CATALOG = [
    {
        "name": "雞蛋",
        "prompts": [
            "a photo of a raw chicken egg",
            "a photo of whole eggs in shells",
            "a photo of fresh eggs",
        ],
    },
    {
        "name": "煎蛋",
        "prompts": [
            "a photo of a fried egg",
            "a photo of a sunny side up egg",
            "a photo of a pan fried egg",
        ],
    },
    {
        "name": "蒸蛋",
        "prompts": [
            "a photo of steamed egg custard",
            "a photo of Chinese steamed egg",
            "a photo of chawanmushi steamed egg",
        ],
    },
    {
        "name": "水煮蛋",
        "prompts": [
            "a photo of a boiled egg",
            "a photo of hard boiled eggs",
            "a photo of sliced boiled egg",
        ],
    },
    {
        "name": "番茄炒蛋",
        "prompts": [
            "a photo of tomato scrambled eggs",
            "a photo of stir fried tomato and egg",
            "a photo of Chinese tomato egg stir fry",
        ],
    },
    {
        "name": "蛋塔",
        "prompts": [
            "a photo of an egg tart",
            "a photo of Portuguese egg tarts",
            "a photo of custard tart",
        ],
    },
    {
        "name": "番茄",
        "prompts": [
            "a photo of a fresh tomato",
            "a photo of raw tomatoes",
            "a photo of sliced tomato",
        ],
    },
    {
        "name": "青江菜",
        "prompts": [
            "a photo of bok choy",
            "a photo of fresh bok choy vegetables",
            "a photo of green bok choy",
        ],
    },
    {
        "name": "豆腐",
        "prompts": [
            "a photo of tofu",
            "a photo of white tofu cubes",
            "a photo of fresh tofu",
        ],
    },
    {
        "name": "牛奶",
        "prompts": [
            "a photo of milk",
            "a photo of a milk bottle",
            "a photo of a glass of milk",
        ],
    },
    {
        "name": "燕麥",
        "prompts": [
            "a photo of oats",
            "a photo of rolled oats",
            "a photo of oatmeal flakes",
        ],
    },
    {
        "name": "牛奶燕麥粥",
        "prompts": [
            "a photo of oatmeal porridge with milk",
            "a photo of a bowl of milk oatmeal",
            "a photo of creamy oatmeal porridge",
        ],
    },
    {
        "name": "肉片",
        "prompts": [
            "a photo of sliced pork",
            "a photo of raw pork slices",
            "a photo of thin sliced meat",
        ],
    },
    {
        "name": "肉片湯麵",
        "prompts": [
            "a photo of noodle soup with sliced pork",
            "a photo of pork noodle soup",
            "a photo of meat noodle soup",
        ],
    },
    {
        "name": "紅蘿蔔",
        "prompts": [
            "a photo of a carrot",
            "a photo of fresh carrots",
            "a photo of sliced carrots",
        ],
    },
    {
        "name": "馬鈴薯",
        "prompts": [
            "a photo of a potato",
            "a photo of raw potatoes",
            "a photo of whole potatoes",
        ],
    },
    {
        "name": "魚",
        "prompts": [
            "a photo of fish",
            "a photo of fresh fish",
            "a photo of cooked fish",
        ],
    },
    {
        "name": "蝦",
        "prompts": [
            "a photo of shrimp",
            "a photo of prawns",
            "a photo of cooked shrimp",
        ],
    },
]


class FoodRecognizer:
    def __init__(self):
        print("Loading CLIP vision model...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model.eval()

        self.prompt_to_label = []
        self.prompts = []
        for item in LABEL_CATALOG:
            for prompt in item["prompts"]:
                self.prompts.append(prompt)
                self.prompt_to_label.append(item["name"])

        print("CLIP vision model loaded.")

    def recognize(self, image_path: str, conf_threshold: float = 0.08) -> list[dict]:
        img = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            text=self.prompts,
            images=img,
            return_tensors="pt",
            padding=True,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)[0]

        label_scores: dict[str, float] = {}
        for label, prob in zip(self.prompt_to_label, probs.tolist()):
            label_scores[label] = max(label_scores.get(label, 0.0), prob)

        all_detections = [
            {
                "name": label,
                "confidence": round(score, 3),
                "bbox": [0, 0, 0, 0],
            }
            for label, score in label_scores.items()
        ]

        all_detections.sort(key=lambda x: x["confidence"], reverse=True)
        detections = [
            item for item in all_detections
            if item["confidence"] >= conf_threshold
        ]
        if not detections:
            detections = all_detections[:5]

        return detections[:5]
