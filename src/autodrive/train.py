"""Train and validate the camera-to-steering imitation model."""
import argparse
import csv
import random
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset

from autodrive.config import SETTINGS
from autodrive.dataset import SteeringDataset
from autodrive.model import SteeringCNN
from autodrive.metrics import steering_mae

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    csv_path = SETTINGS.data_dir / "labels.csv"
    dataset = SteeringDataset(csv_path)
    indices = list(range(len(dataset)))
    random.Random(args.seed).shuffle(indices)
    split = max(1, int(0.8 * len(indices)))
    if split >= len(indices):
        split = len(indices) - 1
    train_loader = DataLoader(Subset(dataset, indices[:split]), batch_size=args.batch_size, shuffle=True)
    valid_loader = DataLoader(Subset(dataset, indices[split:]), batch_size=args.batch_size, shuffle=False)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SteeringCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    SETTINGS.artifacts_dir.mkdir(parents=True, exist_ok=True)
    history = []
    best_mae = float("inf")
    for epoch in range(args.epochs):
        model.train()
        train_losses = []
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(images), targets)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        model.eval()
        predictions, targets_all = [], []
        with torch.no_grad():
            for images, targets in valid_loader:
                predictions.extend(model(images.to(device)).cpu().tolist())
                targets_all.extend(targets.tolist())
        mae = steering_mae(predictions, targets_all)
        row = {"epoch": epoch + 1, "train_mse": sum(train_losses) / len(train_losses), "validation_steering_mae": mae}
        history.append(row)
        print(row)
        if mae < best_mae:
            best_mae = mae
            torch.save({"model_state_dict": model.state_dict(), "image_width": 200,
                        "image_height": 66, "seed": args.seed, "epoch": epoch + 1},
                       SETTINGS.artifacts_dir / "steering_cnn.pth")
    with (SETTINGS.artifacts_dir / "training_history.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)
    print(f"Best held-out steering MAE: {best_mae:.6f}")

if __name__ == "__main__":
    main()
