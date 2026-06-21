# models/vision/recognizer.py
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


# CLIP works better with English prompts, but the app should show Chinese names.
# Keep both ingredient labels and prepared-dish labels so cooked egg dishes do not
# have to collapse back to the raw ingredient "雞蛋".
LABEL_CATALOG = [
    # ── 蛋類 ──
    {
        "name": "雞蛋",
        "prompts": [
            "a photo of brown and white eggshells in a paper carton",
            "a photo of a cracked egg showing yellow yolk and clear egg white",
            "a photo of whole raw eggs on a wooden kitchen counter",
        ],
    },
    {
        "name": "煎蛋",
        "prompts": [
            "a photo of a sunny side up fried egg with runny yellow yolk on a white plate",
            "a photo of a pan fried egg with crispy golden edges",
            "a photo of a fried egg with bright orange yolk sitting on rice",
        ],
    },
    {
        "name": "蒸蛋",
        "prompts": [
            "a photo of smooth pale yellow steamed egg custard in a ceramic bowl",
            "a photo of Chinese chawanmushi with silky soft egg surface and toppings",
            "a photo of glossy steamed egg in a small white dish with soy sauce drizzle",
        ],
    },
    {
        "name": "水煮蛋",
        "prompts": [
            "a photo of peeled hard boiled eggs with white surface and yellow center",
            "a photo of sliced boiled egg halves showing bright yolk and soft white",
            "a photo of boiled eggs in their shells in a bowl of cold water",
        ],
    },
    {
        "name": "番茄炒蛋",
        "prompts": [
            "a photo of red tomato chunks and golden scrambled eggs on a white plate",
            "a photo of Chinese stir fried tomato and egg with bright sauce in a ceramic bowl",
            "a photo of tomato egg stir fry over steamed rice in a Chinese restaurant",
        ],
    },
    {
        "name": "蛋塔",
        "prompts": [
            "a photo of golden brown Portuguese egg tarts with caramelized custard tops",
            "a photo of Hong Kong style egg tart with smooth yellow filling in flaky crust",
            "a photo of mini egg tarts arranged on a bakery tray",
        ],
    },

    # ── 蔬菜 ──
    {
        "name": "青江菜",
        "prompts": [
            "a photo of fresh bok choy with white stalks and dark green leaves",
            "a photo of baby bok choy bundles on a wet market display",
            "a photo of washed bok choy leaves on a wooden cutting board",
        ],
    },
    {
        "name": "番茄",
        "prompts": [
            "a photo of bright red ripe tomatoes with green stems on the top",
            "a photo of sliced tomato showing juicy red flesh and seeds inside",
            "a photo of round shiny tomatoes piled in a wooden basket",
        ],
    },
    {
        "name": "洋蔥",
        "prompts": [
            "a photo of whole yellow onions with thin papery brown skin",
            "a photo of a sliced onion showing white concentric rings",
            "a photo of diced onion pieces on a cutting board next to a knife",
        ],
    },
    {
        "name": "馬鈴薯",
        "prompts": [
            "a photo of brown skinned russet potatoes with rough texture",
            "a photo of peeled white potato halves on a cutting board",
            "a photo of small round potatoes washed and stacked in a basket",
        ],
    },
    {
        "name": "高麗菜",
        "prompts": [
            "a photo of a round green cabbage head with tightly packed leaves",
            "a photo of cabbage cut in half showing layered white inner core",
            "a photo of shredded green cabbage in a glass bowl",
        ],
    },
    {
        "name": "小黃瓜",
        "prompts": [
            "a photo of long thin green cucumbers with bumpy dark skin",
            "a photo of sliced cucumber rounds showing pale green flesh and seeds",
            "a photo of fresh small cucumbers in a market box with water drops",
        ],
    },
    {
        "name": "紅蘿蔔",
        "prompts": [
            "a photo of bright orange whole carrots with green leafy tops",
            "a photo of peeled and sliced carrot rounds on a cutting board",
            "a photo of long thick carrots arranged on a wooden surface",
        ],
    },
    {
        "name": "苦瓜",
        "prompts": [
            "a photo of pale green bitter melon with bumpy wrinkled skin",
            "a photo of bitter gourd cut in half showing white spongy interior",
            "a photo of sliced bitter melon rings on a white plate",
        ],
    },
    {
        "name": "南瓜",
        "prompts": [
            "a photo of a green skinned kabocha pumpkin with thick orange flesh",
            "a photo of a pumpkin cut in half showing bright orange interior and seeds",
            "a photo of sliced pumpkin chunks arranged on a wooden board",
        ],
    },
    {
        "name": "櫛瓜",
        "prompts": [
            "a photo of long dark green zucchini with smooth glossy skin",
            "a photo of sliced zucchini rounds showing pale flesh and small seeds",
            "a photo of fresh green courgettes lying on a wooden cutting board",
        ],
    },
    {
        "name": "蘆筍",
        "prompts": [
            "a photo of bright green asparagus spears with pointed tips",
            "a photo of a bunch of fresh asparagus tied with a rubber band",
            "a photo of cut asparagus pieces in a steel colander",
        ],
    },
    {
        "name": "菠菜",
        "prompts": [
            "a photo of dark green spinach leaves with reddish pink stems",
            "a photo of fresh baby spinach piled in a wooden bowl",
            "a photo of washed spinach leaves on a kitchen towel",
        ],
    },
    {
        "name": "四季豆",
        "prompts": [
            "a photo of long thin bright green string beans tied in a bundle",
            "a photo of fresh snap beans with crisp shiny pods",
            "a photo of trimmed green beans arranged in a metal strainer",
        ],
    },
    {
        "name": "玉米筍",
        "prompts": [
            "a photo of small yellow baby corn cobs with tender kernels",
            "a photo of mini corn arranged on a green leaf",
            "a photo of fresh baby corn lined up in a plastic container",
        ],
    },
    {
        "name": "竹筍",
        "prompts": [
            "a photo of brown skinned fresh bamboo shoots with pointed tips",
            "a photo of peeled white bamboo shoot showing tender interior",
            "a photo of sliced bamboo shoots in a market basket",
        ],
    },
    {
        "name": "花椰菜",
        "prompts": [
            "a photo of a whole green broccoli head with thick stem",
            "a photo of fresh broccoli florets on a white plate",
            "a photo of cut broccoli pieces washed in a colander",
        ],
    },
    {
        "name": "茄子",
        "prompts": [
            "a photo of long purple Chinese eggplant with glossy skin",
            "a photo of dark purple aubergine cut showing pale white flesh",
            "a photo of sliced eggplant rounds on a wooden cutting board",
        ],
    },
    {
        "name": "山藥",
        "prompts": [
            "a photo of long beige Chinese yam with rough brown skin",
            "a photo of peeled white yam showing sticky moist flesh",
            "a photo of fresh nagaimo mountain yam on a kitchen counter",
        ],
    },
    {
        "name": "青木瓜",
        "prompts": [
            "a photo of an unripe green papaya with smooth firm skin",
            "a photo of shredded green papaya strips in a glass bowl",
            "a photo of cut green papaya showing pale white flesh inside",
        ],
    },
    {
        "name": "地瓜",
        "prompts": [
            "a photo of reddish purple sweet potatoes with rough skin",
            "a photo of orange sweet potato cut showing bright flesh inside",
            "a photo of whole raw sweet potatoes piled on wooden surface",
        ],
    },
    {
        "name": "大白菜",
        "prompts": [
            "a photo of a long oval napa cabbage with pale green leaves and white stems",
            "a photo of Chinese cabbage cut in half showing tightly layered leaves",
            "a photo of fresh napa cabbage in a market crate",
        ],
    },
    {
        "name": "小白菜",
        "prompts": [
            "a photo of small bok choy with bright green leaves and white stems",
            "a photo of Shanghai bok choy bundles on a wet market table",
            "a photo of washed baby bok choy on a black plate",
        ],
    },
    {
        "name": "大陸妹",
        "prompts": [
            "a photo of green romaine lettuce with long crisp leaves",
            "a photo of Chinese lettuce leaves loosely arranged in a bowl",
            "a photo of fresh green leaf lettuce on a wooden cutting board",
        ],
    },
    {
        "name": "冬瓜",
        "prompts": [
            "a photo of a large green winter melon with waxy skin",
            "a photo of sliced winter melon showing white flesh and seeds",
            "a photo of wax gourd chunks on a wooden chopping board",
        ],
    },
    {
        "name": "西瓜",
        "prompts": [
            "a photo of a green striped watermelon with thick rind",
            "a photo of sliced red watermelon with black seeds",
            "a photo of watermelon wedges arranged on a white plate",
        ],
    },

    # ── 菇類 ──
    {
        "name": "金針菇",
        "prompts": [
            "a photo of long thin white enoki mushrooms with small caps",
            "a photo of golden needle mushrooms in a plastic packaging",
            "a photo of a bunch of enoki mushrooms tied at the base",
        ],
    },
    {
        "name": "香菇",
        "prompts": [
            "a photo of brown shiitake mushrooms with thick caps",
            "a photo of dried dark brown shiitake mushrooms in a wooden bowl",
            "a photo of sliced shiitake showing pale gills underneath",
        ],
    },
    {
        "name": "鴻禧菇",
        "prompts": [
            "a photo of brown shimeji mushrooms with small caps clustered together",
            "a photo of beech mushroom bunches in plastic packaging",
            "a photo of brown shimeji mushrooms on a white plate",
        ],
    },
    {
        "name": "洋菇",
        "prompts": [
            "a photo of white round button mushrooms with smooth caps",
            "a photo of sliced champignon mushrooms showing brown gills",
            "a photo of fresh button mushrooms in a brown paper bag",
        ],
    },
    {
        "name": "黑木耳",
        "prompts": [
            "a photo of fresh black wood ear fungus with soft jelly texture",
            "a photo of dried wrinkled black fungus in a glass bowl",
            "a photo of soaked black cloud ear mushrooms in water",
        ],
    },
    {
        "name": "雪白菇",
        "prompts": [
            "a photo of bright white bunapi shimeji mushrooms in a cluster",
            "a photo of small white beech mushrooms in plastic packaging",
            "a photo of fresh white shimeji on a black plate",
        ],
    },

    # ── 辛香料 ──
    {
        "name": "蔥",
        "prompts": [
            "a photo of long green and white scallion stalks tied in a bunch",
            "a photo of chopped green onion rings on a wooden cutting board",
            "a photo of fresh spring onions with white roots and green tops",
        ],
    },
    {
        "name": "蒜頭",
        "prompts": [
            "a photo of a whole white garlic bulb with papery skin",
            "a photo of peeled garlic cloves in a small ceramic bowl",
            "a photo of minced garlic on a wooden cutting board",
        ],
    },
    {
        "name": "辣椒",
        "prompts": [
            "a photo of bright red chili peppers with shiny smooth skin",
            "a photo of sliced red chili rings showing white seeds inside",
            "a photo of fresh hot chili peppers piled in a small bowl",
        ],
    },
    {
        "name": "薑",
        "prompts": [
            "a photo of a beige fresh ginger root with knobby shape",
            "a photo of peeled ginger slices showing pale yellow flesh",
            "a photo of grated ginger paste in a small ceramic dish",
        ],
    },
    {
        "name": "香菜",
        "prompts": [
            "a photo of green cilantro leaves with thin stems tied in a bunch",
            "a photo of chopped coriander leaves in a small white bowl",
            "a photo of fresh Chinese parsley sprigs on a kitchen towel",
        ],
    },

    # ── 肉類 ──
    {
        "name": "雞胸肉",
        "prompts": [
            "a photo of pink raw chicken breast on a white plate",
            "a photo of boneless skinless chicken breast on a wooden cutting board",
            "a photo of thinly sliced chicken breast meat with pale color",
        ],
    },
    {
        "name": "雞腿肉",
        "prompts": [
            "a photo of raw chicken thigh with pink flesh and yellow skin",
            "a photo of boneless chicken leg meat on a black tray",
            "a photo of fresh chicken thigh fillets in plastic packaging",
        ],
    },
    {
        "name": "雞翅",
        "prompts": [
            "a photo of raw pink chicken wings with yellow skin on a tray",
            "a photo of chicken wing mid-joints arranged on a white plate",
            "a photo of fresh uncooked chicken wings in a butcher display",
        ],
    },
    {
        "name": "肉片",
        "prompts": [
            "a photo of thin sliced raw pork with pink and white marbling",
            "a photo of stacked meat slices on parchment paper",
            "a photo of thinly sliced raw meat on a black tray",
        ],
    },
    {
        "name": "豬肉片",
        "prompts": [
            "a photo of thin pork belly slices with pink meat and white fat layers",
            "a photo of raw pork slices arranged on a white plate",
            "a photo of fresh sliced pork in plastic packaging from a market",
        ],
    },
    {
        "name": "豬絞肉",
        "prompts": [
            "a photo of fresh pink ground pork piled in a glass bowl",
            "a photo of minced pork meat on a wooden cutting board",
            "a photo of raw pork mince in clear plastic packaging",
        ],
    },
    {
        "name": "牛肉片",
        "prompts": [
            "a photo of thin red sliced beef on a black plate",
            "a photo of raw beef strips with marbled white fat",
            "a photo of fresh beef slices arranged on parchment paper",
        ],
    },
    {
        "name": "香腸",
        "prompts": [
            "a photo of dark red Chinese lap cheong sausages tied in pairs",
            "a photo of cured pork sausages hanging at a Chinese market",
            "a photo of sliced Chinese sausage showing red and white speckles",
        ],
    },
    {
        "name": "培根",
        "prompts": [
            "a photo of long pink bacon strips with white fat streaks",
            "a photo of raw bacon slices arranged on parchment paper",
            "a photo of smoked bacon strips in plastic packaging",
        ],
    },

    # ── 海鮮 ──
    {
        "name": "魚",
        "prompts": [
            "a photo of whole silver fresh fish on a bed of ice",
            "a photo of raw fish fillet with pale pink flesh on a plate",
            "a photo of fresh fish in a market display with scales visible",
        ],
    },
    {
        "name": "蝦",
        "prompts": [
            "a photo of raw pink shrimp with translucent shells",
            "a photo of fresh prawns piled on crushed ice",
            "a photo of peeled pink shrimp in a clear glass bowl",
        ],
    },
    {
        "name": "鮪魚罐頭",
        "prompts": [
            "a photo of an opened tuna can showing flaked light brown fish",
            "a photo of a metal tuna can with pull tab on a kitchen counter",
            "a photo of canned tuna emptied into a small white bowl",
        ],
    },
    {
        "name": "鯖魚罐頭",
        "prompts": [
            "a photo of canned mackerel in red tomato sauce in an open tin",
            "a photo of a mackerel can with colorful label on a shelf",
            "a photo of canned mackerel fish chunks on a small plate",
        ],
    },

    # ── 豆製品 / 蛋製品 ──
    {
        "name": "豆腐",
        "prompts": [
            "a photo of white tofu cubes in a glass dish with water",
            "a photo of soft fresh tofu blocks on a wooden cutting board",
            "a photo of Chinese bean curd in plastic packaging",
        ],
    },
    {
        "name": "豆乾",
        "prompts": [
            "a photo of brown pressed tofu squares stacked on a plate",
            "a photo of Chinese dried bean curd with dark soy color",
            "a photo of sliced firm tofu strips on a wooden surface",
        ],
    },
    {
        "name": "皮蛋",
        "prompts": [
            "a photo of a peeled century egg with dark amber egg white and dark green yolk",
            "a photo of preserved duck eggs in their dark grey coating",
            "a photo of sliced thousand year egg quarters on a white plate",
        ],
    },

    # ── 主食 ──
    {
        "name": "白飯",
        "prompts": [
            "a photo of steaming white rice piled in a porcelain bowl",
            "a photo of cooked white rice grains on a wooden serving spoon",
            "a photo of plain steamed rice in a Chinese rice bowl",
        ],
    },
    {
        "name": "義大利麵",
        "prompts": [
            "a photo of dry yellow spaghetti pasta in a tall glass container",
            "a photo of long uncooked Italian spaghetti strands tied with string",
            "a photo of dried pasta on a wooden chopping board",
        ],
    },
    {
        "name": "吐司",
        "prompts": [
            "a photo of soft white sliced sandwich bread on a wooden board",
            "a photo of golden toasted bread slices on a plate",
            "a photo of a loaf of white bread cut into thick slices",
        ],
    },
    {
        "name": "燕麥",
        "prompts": [
            "a photo of beige rolled oats piled in a wooden bowl",
            "a photo of dry oat flakes spilling from a glass jar",
            "a photo of uncooked oatmeal in a paper packaging",
        ],
    },

    # ── 乳製品 ──
    {
        "name": "牛奶",
        "prompts": [
            "a photo of white milk being poured into a clear glass",
            "a photo of a white milk bottle on a wooden kitchen counter",
            "a photo of a glass full of fresh white milk",
        ],
    },
    {
        "name": "起司",
        "prompts": [
            "a photo of yellow cheese slices stacked on parchment paper",
            "a photo of shredded white mozzarella cheese in a plastic bag",
            "a photo of a yellow cheese block with creamy texture",
        ],
    },

    # ── 其他食材 ──
    {
        "name": "海帶",
        "prompts": [
            "a photo of dark green dried kelp sheets folded on a plate",
            "a photo of soaked kombu seaweed strips in a clear bowl of water",
            "a photo of dried Japanese kelp pieces in plastic packaging",
        ],
    },

    # ── 已調理料理 ──
    {
        "name": "牛奶燕麥粥",
        "prompts": [
            "a photo of creamy white oatmeal porridge with milk in a ceramic bowl",
            "a photo of warm oats cooked in milk with steam rising from a bowl",
            "a photo of breakfast oatmeal topped with fruits on a kitchen table",
        ],
    },
    {
        "name": "肉片湯麵",
        "prompts": [
            "a photo of Chinese pork noodle soup with sliced meat and green vegetables",
            "a photo of a steaming bowl of meat noodle soup with chopsticks on the side",
            "a photo of clear broth noodle soup topped with pork slices and scallions",
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
