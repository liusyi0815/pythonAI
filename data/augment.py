# data/augment.py
import albumentations as A
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm

YOLO_DIR   = Path("data/yolo_dataset")
OUTPUT_DIR = Path("data/yolo_augmented")
AUGMENT_TIMES = 5   # 每張原圖產生 5 張增強圖

# 食材圖片適合的增強策略：
# 顏色、亮度、模糊 → 模擬不同光線與鏡頭
# 翻轉、旋轉       → 食材擺放方向不固定
# 不做 CutOut       → 避免食材被遮擋太多影響辨識
transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=30, p=0.6),
    A.RandomBrightnessContrast(
        brightness_limit=0.3,
        contrast_limit=0.3, p=0.7),
    A.HueSaturationValue(
        hue_shift_limit=15,
        sat_shift_limit=30,
        val_shift_limit=20, p=0.6),
    A.GaussianBlur(blur_limit=(3, 5), p=0.3),
    A.ImageCompression(quality_lower=75, p=0.2),
],
    bbox_params=A.BboxParams(
        format="yolo",
        label_fields=["class_labels"],
        min_visibility=0.3,   # 增強後框面積低於 30% 直接捨棄
    )
)

def read_yolo_labels(label_path: Path) -> tuple[list, list]:
    boxes, cls_ids = [], []
    if not label_path.exists():
        return boxes, cls_ids
    for line in label_path.read_text().strip().split("\n"):
        if not line:
            continue
        parts = list(map(float, line.split()))
        cls_ids.append(int(parts[0]))
        boxes.append(parts[1:])    # cx cy bw bh
    return boxes, cls_ids

def augment_split(split: str):
    img_dir = YOLO_DIR / "images" / split
    lbl_dir = YOLO_DIR / "labels" / split
    out_img = OUTPUT_DIR / "images" / split
    out_lbl = OUTPUT_DIR / "labels" / split
    out_img.mkdir(parents=True, exist_ok=True)
    out_lbl.mkdir(parents=True, exist_ok=True)

    images = list(img_dir.glob("*.jpg"))
    print(f"\n{split}：{len(images)} 張原圖 → "
          f"約 {len(images) * AUGMENT_TIMES} 張增強後")

    for img_path in tqdm(images):
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        boxes, cls_ids = read_yolo_labels(
            lbl_dir / img_path.with_suffix(".txt").name
        )

        for i in range(AUGMENT_TIMES):
            try:
                aug = transform(
                    image=img,
                    bboxes=boxes,
                    class_labels=cls_ids,
                )
            except Exception:
                continue

            out_name = f"{img_path.stem}_aug{i}"

            # 儲存圖片
            out_img_path = out_img / f"{out_name}.jpg"
            cv2.imwrite(str(out_img_path),
                        cv2.cvtColor(aug["image"], cv2.COLOR_RGB2BGR))

            # 儲存標注
            out_lbl_path = out_lbl / f"{out_name}.txt"
            lines = [
                f"{cls} " + " ".join(f"{v:.6f}" for v in box)
                for cls, box in zip(aug["class_labels"],
                                     aug["bboxes"])
            ]
            out_lbl_path.write_text("\n".join(lines))

if __name__ == "__main__":
    augment_split("train")
    augment_split("val")
    print("\n✅ 增強完成")