# models/vision/train_classifier.py
import torch
import torch.nn as nn
from torchvision import models, datasets
import torchvision.transforms as T
from torch.utils.data import DataLoader

def build_efficientnet(num_classes: int):
    """載入預訓練 EfficientNet-B4，替換最後一層"""
    model = models.efficientnet_b4(weights="IMAGENET1K_V1")
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, num_classes)
    return model

def train(data_dir: str, epochs=20, lr=1e-4):
    transform_train = T.Compose([
        T.RandomResizedCrop(224),
        T.RandomHorizontalFlip(),
        T.ColorJitter(brightness=0.3, contrast=0.3),
        T.ToTensor(),
        T.Normalize([0.485,0.456,0.406],
                    [0.229,0.224,0.225]),
    ])
    transform_val = T.Compose([
        T.Resize(256), T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize([0.485,0.456,0.406],
                    [0.229,0.224,0.225]),
    ])

    # data_dir 結構：train/雞蛋/*.jpg  val/雞蛋/*.jpg
    train_ds = datasets.ImageFolder(f"{data_dir}/train", transform_train)
    val_ds   = datasets.ImageFolder(f"{data_dir}/val",   transform_val)
    train_dl = DataLoader(train_ds, batch_size=32, shuffle=True,  num_workers=4)
    val_dl   = DataLoader(val_ds,   batch_size=32, shuffle=False, num_workers=4)

    model = build_efficientnet(num_classes=len(train_ds.classes))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model  = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_acc = 0.0
    for epoch in range(epochs):
        # ── train ──
        model.train()
        for imgs, labels in train_dl:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()
            optimizer.step()

        # ── validate ──
        model.eval()
        correct = total = 0
        with torch.no_grad():
            for imgs, labels in val_dl:
                imgs, labels = imgs.to(device), labels.to(device)
                preds = model(imgs).argmax(dim=1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        acc = correct / total
        scheduler.step()
        print(f"Epoch {epoch+1}/{epochs}  val_acc={acc:.4f}")

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), "models/efficientnet_food.pt")

if __name__ == "__main__":
    train("data/classifier", epochs=20)