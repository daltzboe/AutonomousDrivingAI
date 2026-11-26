import torch
from torch import nn

class SteeringCNN(nn.Module):
    """Compact NVIDIA-inspired image-to-steering regression baseline."""
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 24, kernel_size=5, stride=2), nn.ReLU(),
            nn.Conv2d(24, 36, kernel_size=5, stride=2), nn.ReLU(),
            nn.Conv2d(36, 48, kernel_size=5, stride=2), nn.ReLU(),
            nn.Conv2d(48, 64, kernel_size=3), nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3), nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 4)),
            nn.Flatten(),
        )
        self.regressor = nn.Sequential(
            nn.Linear(64 * 1 * 4, 100), nn.ReLU(),
            nn.Linear(100, 50), nn.ReLU(),
            nn.Linear(50, 10), nn.ReLU(),
            nn.Linear(10, 1), nn.Tanh(),
        )

    def forward(self, images):
        return self.regressor(self.features(images)).squeeze(1)
