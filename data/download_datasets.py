# data/download_datasets.py
"""
下載策略：
  Food-101   → EfficientNet 分類用（101 類食物，每類 1000 張）
  Open Images → YOLO 偵測用（有 bounding box 標注）
"""
import os, shutil, tarfile, zipfile
from pathlib import Path
import requests
from tqdm import tqdm

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, dest: Path):
    """帶進度條的下載"""
    resp = requests.get(url, stream=True, timeout=60)
    total = int(resp.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(
        total=total, unit="B", unit_scale=True,
        desc=dest.name
    ) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

def download_food101():
    """
    Food-101：史丹佛大學公開資料集
    101 種食物，每類 750 train + 250 test，共 101,000 張
    """
    url  = "http://data.vision.ee.ethz.ch/cvl/food-101.tar.gz"
    dest = RAW_DIR / "food-101.tar.gz"

    if not dest.exists():
        print("下載 Food-101...")
        download_file(url, dest)

    extract_dir = RAW_DIR / "food101"
    if not extract_dir.exists():
        print("解壓縮 Food-101...")
        with tarfile.open(dest, "r:gz") as tar:
            tar.extractall(RAW_DIR)
        (RAW_DIR / "food-101").rename(extract_dir)

    print(f"✅ Food-101 解壓完成：{extract_dir}")

def download_open_images_subset(classes: list[str],
                                  max_per_class: int = 200):
    """
    用 fiftyone 下載 Open Images 指定類別的圖片與 bounding box
    需先安裝：pip install fiftyone
    """
    try:
        import fiftyone as fo
        import fiftyone.zoo as foz
    except ImportError:
        print("請先執行：pip install fiftyone")
        return

    save_dir = RAW_DIR / "open_images"
    save_dir.mkdir(exist_ok=True)

    for cls in classes:
        print(f"下載 Open Images：{cls}")
        dataset = foz.load_zoo_dataset(
            "open-images-v7",
            split="train",
            label_types=["detections"],
            classes=[cls],
            max_samples=max_per_class,
            dataset_dir=str(save_dir / cls),
        )
        print(f"  → {len(dataset)} 張")

if __name__ == "__main__":
    download_food101()

    # Open Images 只下載台灣常見食材對應的英文類別
    OPEN_IMAGES_CLASSES = [
        "Egg", "Tomato", "Cabbage", "Pork", "Tofu",
        "Milk", "Onion", "Carrot", "Potato", "Garlic",
    ]
    download_open_images_subset(OPEN_IMAGES_CLASSES, max_per_class=300)