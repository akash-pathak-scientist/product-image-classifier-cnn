"""ProductCNN — a small from-scratch convolutional network for product images.

Design goals: tiny (runs on CPU and free Colab GPUs), fast to converge on
coarse catalogue domains, strong augmentation to avoid overfitting.

    4 x [Conv3x3 -> BatchNorm -> ReLU -> MaxPool2]  with channels 32/64/128/256
    GlobalAveragePool -> FC(128) -> ReLU -> Dropout -> FC(3)

~0.6M parameters at 112x112 input.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class ConvBlock(nn.Sequential):
    def __init__(self, cin: int, cout: int):
        super().__init__(
            nn.Conv2d(cin, cout, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(cout),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )


class ProductCNN(nn.Module):
    def __init__(self, num_classes: int = 3, dropout: float = 0.30):
        super().__init__()
        chs = [32, 64, 128, 256]
        layers: list[nn.Module] = []
        cin = 3
        for cout in chs:
            layers.append(ConvBlock(cin, cout))
            cin = cout
        self.features = nn.Sequential(*layers)
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(chs[-1], 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x))


def build_mobilenetv3s(num_classes: int = 3, dropout: float = 0.20,
                       pretrained: bool = True) -> nn.Module:
    """Small CNN (~2.5M params) with an ImageNet-pretrained MobileNetV3-Small
    backbone - the 'transfer learning' model used for the final classifier."""
    from torchvision.models import (MobileNet_V3_Small_Weights,
                                    mobilenet_v3_small)
    weights = MobileNet_V3_Small_Weights.IMAGENET1K_V1 if pretrained else None
    m = mobilenet_v3_small(weights=weights)
    m.classifier[2] = nn.Dropout(dropout)
    m.classifier[3] = nn.Linear(m.classifier[3].in_features, num_classes)
    return m


# arch registry: name -> (builder, default input size)
ARCHS = {
    "productcnn": (ProductCNN, 112),
    "mobilenetv3s": (build_mobilenetv3s, 160),
}


def build_model(arch: str, num_classes: int = 3, dropout: float = 0.30,
                pretrained: bool = True) -> nn.Module:
    if arch == "productcnn":
        return ProductCNN(num_classes, dropout)
    if arch == "mobilenetv3s":
        return build_mobilenetv3s(num_classes, dropout=dropout,
                                  pretrained=pretrained)
    raise ValueError(f"unknown arch: {arch}")


if __name__ == "__main__":
    m = ProductCNN()
    n = sum(p.numel() for p in m.parameters())
    print(f"ProductCNN parameters: {n/1e6:.2f}M")
    x = torch.randn(2, 3, 112, 112)
    print("output shape:", m(x).shape)
