# data/prepare_yolo_dataset.py
"""
從 labeled/ 產生 YOLO 訓練所需的 dataset.yaml
並做 train/val split（如果還沒分好）
"""
import random, shutil, yaml
from pathlib import Path

LABELED_DIR = Path("data/labeled")
YOLO_DIR    = Path("data/yolo_dataset")
TRAIN_RATIO = 0.85

CLASSES = [
    "雞蛋", "番茄", "青江菜", "肉片", "豆腐",
    "牛奶", "洋蔥", "紅蘿蔔", "馬鈴薯", "蒜頭",
]

def split_and_copy():
    all_images = list((LABELED_DIR / "images" / "train").glob("*.jpg"))
    random.shuffle(all_images)
    split_idx  = int(len(all_images) * TRAIN_RATIO)
    splits = {
        "train": all_images[:split_idx],
        "val":   all_images[split_idx:],
    }

    for split, imgs in splits.items():
        img_out = YOLO_DIR / "images" / split
        lbl_out = YOLO_DIR / "labels" / split
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        for img_path in imgs:
            lbl_path = (LABELED_DIR / "labels" / "train"
                        / img_path.with_suffix(".txt").name)
            if lbl_path.exists():
                shutil.copy(img_path, img_out / img_path.name)
                shutil.copy(lbl_path, lbl_out / lbl_path.name)

    print(f"train: {split_idx}  val: {len(all_images)-split_idx}")

def write_yaml():
    config = {
        "path":  str(YOLO_DIR.resolve()),
        "train": "images/train",
        "val":   "images/val",
        "nc":    len(CLASSES),
        "names": CLASSES,
    }
    out = YOLO_DIR / "dataset.yaml"
    with open(out, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True,
                  default_flow_style=False)
    print(f"✅ 產生 {out}")

if __name__ == "__main__":
    split_and_copy()
    write_yaml()