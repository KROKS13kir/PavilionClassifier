import os
import shutil
import random
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import torch.optim as optim
import numpy as np
from sklearn.metrics import f1_score
from PIL import Image, ImageOps
from torchvision.models import ResNet18_Weights
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Для воспроизводимости
seed = 42
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
random.seed(seed)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Абсолютный путь к твоему проекту
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # до PythonProject3

# Путь к папке model
MODEL_DIR = BASE_DIR / 'image_classifier' / 'backend' / 'classifier' / 'model'

MODEL_DIR.mkdir(parents=True, exist_ok=True)  # СОЗДАЁМ если её вдруг нет



# Константы
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.webp', '.jfif')
IMG_SIZE = (224, 224)
VAL_SPLIT = 0.2
batch_size = 32
num_epochs = 20

# 🔹 1. Функция обработки изображения
def process_image(image_path, output_path):
    with Image.open(image_path) as img:
        print(f"{Path(image_path).name}: {img.size}")  # лог размера
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=95)

# 🔹 2. Функция подготовки датасета (train/val)
def prepare_dataset(raw_dir, train_dir, val_dir):
    print(f"🔵 Подготовка датасета из {raw_dir}...")
    if os.path.exists(train_dir):
        shutil.rmtree(train_dir)
    if os.path.exists(val_dir):
        shutil.rmtree(val_dir)

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    for category in os.listdir(raw_dir):
        category_path = os.path.join(raw_dir, category)
        if not os.path.isdir(category_path):
            continue

        os.makedirs(os.path.join(train_dir, category), exist_ok=True)
        os.makedirs(os.path.join(val_dir, category), exist_ok=True)

        images = [f for f in os.listdir(category_path) if f.lower().endswith(SUPPORTED_FORMATS)]
        random.shuffle(images)

        val_size = int(len(images) * VAL_SPLIT)
        val_images = images[:val_size]
        train_images = images[val_size:]

        for img in train_images:
            process_image(os.path.join(category_path, img), os.path.join(train_dir, category, img))
        for img in val_images:
            process_image(os.path.join(category_path, img), os.path.join(val_dir, category, img))

    print("✅ Датасет подготовлен.")

# 🔹 3. Функция обучения модели
def train_model(train_dir, val_dir, save_model_path, save_metrics_path):
    print(f"🔵 Начинаем обучение модели...")

    save_model_path = Path(save_model_path)
    save_model_path.parent.mkdir(parents=True, exist_ok=True)

    save_metrics_path = Path(save_metrics_path)
    save_metrics_path.parent.mkdir(parents=True, exist_ok=True)

    train_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomRotation(10),
        transforms.CenterCrop(224),
        transforms.RandomHorizontalFlip(0.5),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_dataset = ImageFolder(train_dir, transform=train_transforms)
    val_dataset = ImageFolder(val_dir, transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, 4)

    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    best_val_accuracy = 0

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0
        correct = 0
        total = 0
        for images, labels in tqdm(train_loader, desc=f"Эпоха {epoch + 1}/{num_epochs} [Train]"):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        train_accuracy = correct / total

        # Validation
        model.eval()
        val_loss = 0
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in tqdm(val_loader, desc=f"Эпоха {epoch + 1}/{num_epochs} [Val]"):
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        val_accuracy = correct / total
        print(f"Эпоха [{epoch + 1}/{num_epochs}] Train Acc: {train_accuracy:.4f}, Val Acc: {val_accuracy:.4f}")
        MODEL_DIR.mkdir(parents=True, exist_ok=True)

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            torch.save(model.state_dict(), str(save_model_path))
            print(f"🎯 Лучшая модель сохранена с точностью {best_val_accuracy:.4f}")

        with open(str(save_metrics_path), 'w') as f:
            f.write(str(best_val_accuracy))


# 🔹 4. Главная функция запуска переобучения
def retrain_if_needed():
    raw_dir = BASE_DIR / 'dataset' / 'raw'
    train_dir = BASE_DIR / 'dataset' / 'train'
    val_dir = BASE_DIR / 'dataset' / 'val'
    save_model_path = MODEL_DIR / 'best_model.pth'
    save_metrics_path = MODEL_DIR / 'last_val_accuracy.txt'

    MODEL_DIR.mkdir(parents=True, exist_ok=True)  # создать папку, если вдруг нет

    old_accuracy = 0
    if save_metrics_path.exists():
        with open(save_metrics_path, 'r') as f:
            old_accuracy = float(f.read().strip())

    prepare_dataset(raw_dir, train_dir, val_dir)
    train_model(train_dir, val_dir, save_model_path, save_metrics_path)

    new_accuracy = 0
    if save_metrics_path.exists():
        with open(save_metrics_path, 'r') as f:
            new_accuracy = float(f.read().strip())

    if new_accuracy > old_accuracy:
        print(f"✅ Модель обновлена: новая точность {new_accuracy:.4f} (старая была {old_accuracy:.4f})")
    else:
        print(f"⚠️ Новая модель не лучше старой ({new_accuracy:.4f} <= {old_accuracy:.4f})")


