import json, torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.recommender.model import MenuRecommender

DATA_PATH  = Path("data/recommender_train.json")
SAVE_PATH  = Path("models/recommender.pt")

BATCH_SIZE = 256
EPOCHS     = 30
LR         = 1e-3


class RecipeDataset(Dataset):
    def __init__(self, samples: list[dict]):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return (
            torch.tensor(s["ingredient_ids"], dtype=torch.long),
            torch.tensor(s["profile_vec"],    dtype=torch.float),
            torch.tensor(s["label"],          dtype=torch.long),
        )


def evaluate(model, loader, criterion, device):
    """評估模型在資料集上的 loss 和 accuracy"""
    model.eval()
    total_loss = 0.0
    correct = total = 0
    with torch.no_grad():
        for ing_ids, prof_vec, labels in loader:
            ing_ids  = ing_ids.to(device)
            prof_vec = prof_vec.to(device)
            labels   = labels.to(device)

            logits = model(ing_ids, prof_vec)
            loss = criterion(logits, labels)
            total_loss += loss.item()

            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total   += labels.size(0)

    avg_loss = total_loss / len(loader)
    acc = correct / total
    return avg_loss, acc


def train():
    print("載入訓練資料...")
    with open(DATA_PATH, encoding="utf-8") as f:
        samples = json.load(f)
    print(f"共 {len(samples)} 筆樣本")

    num_recipes = max(s["label"] for s in samples) + 1
    print(f"食譜數量：{num_recipes}")
    vocab_size = max(
        max((id for id in s["ingredient_ids"] if id != 0), default=0)
        for s in samples
    ) + 1
    print(f"食材種類數：{vocab_size}")

    #  80% 訓練 / 20% 驗證
    dataset = RecipeDataset(samples)
    val_size   = int(len(dataset) * 0.2)
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE,
                          shuffle=True, num_workers=0)
    val_dl   = DataLoader(val_ds, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=0)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用裝置：{device}\n")

    model = MenuRecommender(vocab_size=vocab_size, num_recipes=num_recipes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    best_acc = 0.0

    for epoch in range(EPOCHS):
        # ── 訓練階段 ──
        model.train()
        total_loss = 0.0
        correct = total = 0
        for ing_ids, prof_vec, labels in train_dl:
            ing_ids  = ing_ids.to(device)
            prof_vec = prof_vec.to(device)
            labels   = labels.to(device)

            optimizer.zero_grad()
            logits = model(ing_ids, prof_vec)
            loss   = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            # 計算訓練準確率
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total   += labels.size(0)

        train_loss = total_loss / len(train_dl)
        train_acc  = correct / total

        # ── 驗證階段 ──
        val_loss, val_acc = evaluate(model, val_dl, criterion, device)
        scheduler.step()

        # ── 印出兩組指標 ──
        print(f"Epoch {epoch+1:02d}/{EPOCHS}  "
              f"train_loss={train_loss:.4f}  train_acc={train_acc:.4f}  |  "
              f"val_loss={val_loss:.4f}  val_acc={val_acc:.4f}")

        # 儲存最佳模型
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"  儲存最佳模型 val_acc={val_acc:.4f}")

    print(f"\n訓練完成，最佳 val_acc={best_acc:.4f}")
    print(f"模型儲存於：{SAVE_PATH}")


if __name__ == "__main__":
    train()