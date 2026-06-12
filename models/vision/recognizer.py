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
    {
        "name": "雞胸肉", 
        "prompts": [
            "a photo of raw chicken breast", 
            "a photo of boneless chicken breast fillet", 
            "a photo of sliced chicken breast meat"
        ],
    },
    
 {
        "name": "雞腿肉",
        "prompts": [
            "a photo of raw chicken thigh",
            "a photo of boneless chicken leg meat",
            "a photo of chicken thigh fillet",
        ],
    },
    
{
        "name": "雞翅",
        "prompts": [
            "a photo of raw chicken wings",
            "a photo of chicken wing mid-joint",
            "a photo of uncooked chicken wings on a plate",
        ],
    },
    {
        "name": "豬肉片",
        "prompts": [
            "a photo of sliced pork",
            "a photo of thin pork belly slices",
            "a photo of raw pork slices on a plate",
        ],
    }, 
    {
        "name": "豬絞肉",
        "prompts": [
            "a photo of ground pork",
            "a photo of minced pork meat",
            "a photo of raw pork mince",
        ],
    },
    {
        "name": "牛肉片",
        "prompts": [
            "a photo of sliced beef",
            "a photo of thin beef slices",
            "a photo of raw beef strips",
        ],
    },   
    {
        "name": "香腸",
        "prompts": [
            "a photo of Chinese sausage",
            "a photo of cured pork sausage",
            "a photo of lap cheong sausage",
        ],
    },
    {
        "name": "培根",
        "prompts": [
            "a photo of bacon strips",
            "a photo of raw bacon slices",
            "a photo of smoked bacon",
        ],
    },
    {
        "name": "鮪魚罐頭",
        "prompts": [
            "a photo of canned tuna",
            "a photo of tuna can opened",
            "a photo of tuna fish in a tin",
        ],
    },
    {
        "name": "鯖魚罐頭",
        "prompts": [
            "a photo of canned mackerel in tomato sauce",
            "a photo of mackerel tin",
            "a photo of canned fish",
        ],
    },
    {
        "name": "番茄",
        "prompts": [
            "a photo of fresh tomatoes",
            "a photo of red ripe tomatoes",
            "a photo of tomatoes on a cutting board",
        ],
    },
    {
        "name": "洋蔥",
        "prompts": [
            "a photo of onions",
            "a photo of yellow onion",
            "a photo of whole and sliced onion",
        ],
    },
    {
        "name": "馬鈴薯",
        "prompts": [
            "a photo of potatoes",
            "a photo of raw peeled potatoes",
            "a photo of potato slices",
        ],
    },
    {
        "name": "青江菜",
        "prompts": [
            "a photo of bok choy",
            "a photo of Chinese green bok choy",
            "a photo of baby bok choy",
        ],
    },    
    {
        "name": "高麗菜",
        "prompts": [
            "a photo of cabbage",
            "a photo of green cabbage head",
            "a photo of Taiwanese round cabbage",
        ],
    },
    {
        "name": "小黃瓜",
        "prompts": [
            "a photo of cucumber",
            "a photo of Japanese cucumber",
            "a photo of fresh small cucumbers",
        ],
    },  
    {
        "name": "苦瓜",
        "prompts": [
            "a photo of bitter melon",
            "a photo of bitter gourd",
            "a photo of green bitter melon",
        ],
    },
    {
        "name": "南瓜",
        "prompts": [
            "a photo of pumpkin",
            "a photo of kabocha squash",
            "a photo of Japanese pumpkin",
        ],
    },
    {
        "name": "節瓜",
        "prompts": [
            "a photo of zucchini",
            "a photo of courgette",
            "a photo of green zucchini squash",
        ],
    },
    {
        "name": "蘆筍",
        "prompts": [
            "a photo of asparagus",
            "a photo of green asparagus spears",
            "a photo of asparagus bunch",
        ],
    },
    {
        "name": "菠菜",
        "prompts": [
            "a photo of fresh spinach",
            "a photo of spinach leaves",
            "a photo of raw baby spinach",
        ],
    },
    {
        "name": "四季豆",
        "prompts": [
            "a photo of green beans",
            "a photo of string beans",
            "a photo of fresh snap beans",
        ],
    },
    {
        "name": "玉米筍",
        "prompts": [
            "a photo of baby corn",
            "a photo of mini corn cobs",
            "a photo of fresh baby corn",
        ],
    },
    {
        "name": "竹筍",
        "prompts": [
            "a photo of bamboo shoots",
            "a photo of fresh bamboo shoot",
            "a photo of peeled bamboo shoots",
        ],
    },
    {
        "name": "花椰菜",
        "prompts": [
            "a photo of broccoli",
            "a photo of fresh broccoli florets",
            "a photo of green broccoli head",
        ],
    },
    {
        "name": "茄子",
        "prompts": [
            "a photo of eggplant",
            "a photo of Chinese long eggplant",
            "a photo of purple aubergine",
        ],
    },
    {
        "name": "山藥",
        "prompts": [
            "a photo of Chinese yam",
            "a photo of nagaimo yam",
            "a photo of fresh mountain yam",
        ],
    },
    
   {
        "name": "青木瓜",
        "prompts": [
            "a photo of green papaya",
            "a photo of unripe papaya",
            "a photo of shredded green papaya",
        ],
    },
    {
        "name": "地瓜",
        "prompts": [
            "a photo of sweet potato",
            "a photo of orange sweet potato",
            "a photo of raw sweet potatoes",
        ],
    },    
   {
        "name": "大白菜",
        "prompts": [
            "a photo of napa cabbage",
            "a photo of Chinese cabbage",
            "a photo of whole napa cabbage",
        ],
    },
    {
        "name": "小白菜",
        "prompts": [
            "a photo of baby bok choy",
            "a photo of small Chinese cabbage",
            "a photo of Shanghai bok choy",
        ],
    },
    {
        "name": "大陸妹",
        "prompts": [
            "a photo of romaine lettuce",
            "a photo of Chinese lettuce",
            "a photo of green leaf lettuce",
        ],
    },
    {
        "name": "冬瓜",
        "prompts": [
            "a photo of winter melon",
            "a photo of wax gourd",
            "a photo of sliced winter melon",
        ],
    },
    {
        "name": "西瓜",
        "prompts": [
            "a photo of watermelon",
            "a photo of sliced watermelon",
            "a photo of watermelon rind",
        ],
    },
    {
        "name": "金針菇",
        "prompts": [
            "a photo of enoki mushrooms",
            "a photo of golden needle mushrooms",
            "a photo of long thin white mushrooms",
        ],
    },
    {
        "name": "香菇",
        "prompts": [
            "a photo of shiitake mushrooms",
            "a photo of dried shiitake",
            "a photo of Chinese black mushrooms",
        ],
    },
    {
        "name": "鴻禧菇",
        "prompts": [
            "a photo of shimeji mushrooms",
            "a photo of beech mushrooms",
            "a photo of brown shimeji cluster",
        ],
    },
    {
        "name": "洋菇",
        "prompts": [
            "a photo of button mushrooms",
            "a photo of white champignon mushrooms",
            "a photo of sliced mushrooms",
        ],
    },
    {
        "name": "黑木耳",
        "prompts": [
            "a photo of black wood ear fungus",
            "a photo of dried black fungus",
            "a photo of cloud ear mushroom",
        ],
    },    
    {
        "name": "雪白菇",
        "prompts": [
            "a photo of white beech mushrooms",
            "a photo of bunapi shimeji",
            "a photo of white shimeji mushrooms",
        ],
    },
    {
        "name": "蔥",
        "prompts": [
            "a photo of green onion",
            "a photo of scallion",
            "a photo of spring onion stalks",
        ],
    },
    {
        "name": "蒜頭",
        "prompts": [
            "a photo of garlic cloves",
            "a photo of whole garlic bulb",
            "a photo of peeled garlic",
        ],
    },
    {
        "name": "辣椒",
        "prompts": [
            "a photo of red chili pepper",
            "a photo of fresh hot chili peppers",
            "a photo of sliced red chili",
        ],
    }, 
    {
        "name": "薑",
        "prompts": [
            "a photo of fresh ginger root",
            "a photo of ginger slices",
            "a photo of raw ginger",
        ],
    },
    {
        "name": "香菜",
        "prompts": [
            "a photo of fresh cilantro",
            "a photo of coriander leaves",
            "a photo of Chinese parsley",
        ],
    }, 
    {
        "name": "豆乾",
        "prompts": [
            "a photo of pressed dried tofu",
            "a photo of Chinese dried bean curd",
            "a photo of brown tofu squares",
        ],
    },
    {
        "name": "皮蛋",
        "prompts": [
            "a photo of century egg",
            "a photo of preserved duck egg",
            "a photo of thousand year egg",
        ],
    },
    {
        "name": "白飯",
        "prompts": [
            "a photo of steamed white rice",
            "a photo of a bowl of cooked rice",
            "a photo of plain white rice",
        ],
    },
    {
        "name": "義大利麵",
        "prompts": [
            "a photo of spaghetti pasta",
            "a photo of dried Italian pasta",
            "a photo of uncooked spaghetti",
        ],
    },
    {
        "name": "吐司",
        "prompts": [
            "a photo of sliced bread",
            "a photo of white toast bread",
            "a photo of sandwich bread slices",
        ],
    }, 
    {
        "name": "海帶",
        "prompts": [
            "a photo of kelp seaweed",
            "a photo of Japanese kombu",
            "a photo of dried seaweed strips",
        ],
    },
    {
        "name": "起司",
        "prompts": [
            "a photo of cheese slices",
            "a photo of shredded mozzarella cheese",
            "a photo of cheese block",
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
