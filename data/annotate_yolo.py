# data/annotate_yolo.py
"""
操作方式：
  滑鼠拖曳  → 畫 bounding box
  數字鍵    → 選擇類別（0=雞蛋, 1=番茄, ...）
  Enter     → 確認儲存當前框
  D         → 刪除最後一個框
  N         → 下一張圖
  Q         → 離開
"""
import cv2
import json
from pathlib import Path

CLASSES = [
    "雞蛋", "番茄", "青江菜", "肉片", "豆腐",
    "牛奶", "洋蔥", "紅蘿蔔", "馬鈴薯", "蒜頭",
]
COLORS = [
    (255,  80,  80), (80, 200,  80), (80,  80, 255),
    (255, 200,  80), (200,  80, 255), (80, 200, 200),
    (255, 120, 180), (150, 255, 100), (100, 150, 255),
    (255, 180, 100),
]

IMAGE_DIR = Path("data/raw/custom_photos")
LABEL_DIR = Path("data/labeled/labels/train")
OUTPUT_DIR = Path("data/labeled/images/train")
LABEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class YOLOAnnotator:
    def __init__(self):
        self.boxes: list[dict] = []   # {cls, x1, y1, x2, y2}
        self.current_class = 0
        self.drawing = False
        self.start_x = self.start_y = 0
        self.cur_x   = self.cur_y   = 0
        self.img_orig = None
        self.img_display = None

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_x, self.start_y = x, y
            self.cur_x,   self.cur_y   = x, y

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.cur_x, self.cur_y = x, y
            self._refresh_display()

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            # 確保左上到右下
            x1, x2 = sorted([self.start_x, x])
            y1, y2 = sorted([self.start_y, y])
            if (x2 - x1) > 10 and (y2 - y1) > 10:   # 排除誤點
                self.boxes.append({
                    "cls": self.current_class,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                })
            self._refresh_display()

    def _refresh_display(self):
        self.img_display = self.img_orig.copy()
        h, w = self.img_orig.shape[:2]

        # 畫已確認的框
        for b in self.boxes:
            color = COLORS[b["cls"]]
            cv2.rectangle(self.img_display,
                           (b["x1"], b["y1"]),
                           (b["x2"], b["y2"]),
                           color, 2)
            label = CLASSES[b["cls"]]
            cv2.putText(self.img_display, label,
                        (b["x1"], b["y1"] - 6),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, color, 2)

        # 畫正在拖曳的框
        if self.drawing:
            cv2.rectangle(self.img_display,
                           (self.start_x, self.start_y),
                           (self.cur_x,   self.cur_y),
                           COLORS[self.current_class], 1)

        # 顯示目前選擇的類別
        info = (f"類別：{CLASSES[self.current_class]} "
                f"({self.current_class})  |  "
                f"已標注：{len(self.boxes)} 個框")
        cv2.putText(self.img_display, info, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (255, 255, 255), 2)

    def save_yolo(self, img_path: Path):
        """存成 YOLO 格式的 .txt 標注檔"""
        h, w = self.img_orig.shape[:2]
        lines = []
        for b in self.boxes:
            # YOLO 格式：class cx cy bw bh（全部 normalize 到 0–1）
            cx = ((b["x1"] + b["x2"]) / 2) / w
            cy = ((b["y1"] + b["y2"]) / 2) / h
            bw = (b["x2"] - b["x1"]) / w
            bh = (b["y2"] - b["y1"]) / h
            lines.append(f"{b['cls']} {cx:.6f} {cy:.6f} "
                          f"{bw:.6f} {bh:.6f}")

        label_path = LABEL_DIR / (img_path.stem + ".txt")
        label_path.write_text("\n".join(lines))

        # 同步複製圖片到 labeled/images/
        import shutil
        shutil.copy(img_path, OUTPUT_DIR / img_path.name)
        print(f"  💾 儲存 {len(self.boxes)} 個框 → {label_path.name}")

    def run(self):
        images = sorted(IMAGE_DIR.glob("*.jpg")) + \
                 sorted(IMAGE_DIR.glob("*.png"))
        print(f"找到 {len(images)} 張圖片待標注")

        cv2.namedWindow("Annotator")
        cv2.setMouseCallback("Annotator", self.mouse_callback)

        for img_path in images:
            label_check = LABEL_DIR / (img_path.stem + ".txt")
            if label_check.exists():
                print(f"  ⏩ 跳過已標注：{img_path.name}")
                continue

            print(f"\n📷 {img_path.name}")
            self.img_orig = cv2.imread(str(img_path))
            self.boxes = []
            self._refresh_display()

            while True:
                cv2.imshow("Annotator", self.img_display)
                key = cv2.waitKey(20) & 0xFF

                # 數字鍵切換類別
                if ord('0') <= key <= ord('9'):
                    idx = key - ord('0')
                    if idx < len(CLASSES):
                        self.current_class = idx
                        self._refresh_display()

                elif key == 13:      # Enter：確認儲存
                    self.save_yolo(img_path)
                    break

                elif key == ord('d'):  # 刪除最後一框
                    if self.boxes:
                        self.boxes.pop()
                        self._refresh_display()

                elif key == ord('n'):  # 下一張（不儲存）
                    break

                elif key == ord('q'):  # 離開
                    cv2.destroyAllWindows()
                    return

        cv2.destroyAllWindows()
        print("\n✅ 標注完成")

if __name__ == "__main__":
    annotator = YOLOAnnotator()
    annotator.run()