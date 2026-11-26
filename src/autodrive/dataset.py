from pathlib import Path
import csv
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset

class SteeringDataset(Dataset):
    """Read RGB demonstration frames and their normalized steering labels."""
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        with self.csv_path.open(newline="", encoding="utf-8") as stream:
            self.rows = list(csv.DictReader(stream))
        if not self.rows:
            raise ValueError(f"No samples found in {self.csv_path}")

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        image_path = (self.csv_path.parent / row["image_path"]).resolve()
        with Image.open(image_path) as image:
            image = image.convert("RGB").resize((200, 66))
            array = np.asarray(image, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(array).permute(2, 0, 1)
        steering = torch.tensor(float(row["steering"]), dtype=torch.float32)
        return tensor, steering
