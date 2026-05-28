# data/prepare_classifier.py
import shutil, random
from pathlib import Path
from PIL import Image
from tqdm import tqdm

RAW_FOOD101   = Path("data/raw/food101/food-101")
CLASSIFIER_DIR = Path("data/classifier")

# Food-101 英文類別 → 中文食材名稱對照
# 只保留台灣廚房常見的
CATEGORY_MAP = {
    "fried_egg":        "雞蛋",
    "scrambled_eggs":   "雞蛋",
    "deviled_eggs":     "雞蛋",
    "bruschetta":       "番茄",        
    "caprese_salad":    "番茄",
    "pork_chop":        "肉片",
    "baby_back_ribs":   "肉片",
    "carrot_cake":      "紅蘿蔔",
    "onion_rings":      "洋蔥",
    "garlic_bread":     "蒜頭",
    "french_fries":     "馬鈴薯",
    "edamame":          "毛豆",
    "miso_soup":        "豆腐",
    "gyoza":            "豬絞肉",
    # 自行依需求擴充...
}

TRAIN_RATIO = 0.8

def prepare():
    for split in ("train", "val"):
        (CLASSIFIER_DIR / split).mkdir(parents=True, exist_ok=True)

    # 先把所有目標類別的路徑收集好
    class_images: dict[str, list[Path]] = {}

    for en_name, zh_name in CATEGORY_MAP.items():
        img_dir = RAW_FOOD101 / "images" / en_name
        if not img_dir.exists():
            print(f"  ⚠️  找不到 {en_name}，跳過")
            continue
        imgs = list(img_dir.glob("*.jpg"))
        class_images.setdefault(zh_name, []).extend(imgs)

    # 建立資料夾、複製圖片
    for zh_name, paths in class_images.items():
        random.shuffle(paths)
        split_idx = int(len(paths) * TRAIN_RATIO)
        splits = {"train": paths[:split_idx],
                  "val":   paths[split_idx:]}

        for split, imgs in splits.items():
            dest_dir = CLASSIFIER_DIR / split / zh_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            for img_path in tqdm(imgs, desc=f"{split}/{zh_name}"):
                # 統一轉 RGB，避免 RGBA PNG 出問題
                dest = dest_dir / img_path.name
                if not dest.exists():
                    img = Image.open(img_path).convert("RGB")
                    img.save(dest, "JPEG", quality=90)

        print(f"✅ {zh_name}：train={split_idx}  "
              f"val={len(paths)-split_idx}")

if __name__ == "__main__":
    prepare()