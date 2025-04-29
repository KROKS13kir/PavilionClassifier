# image_classifier/classifier.py
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

# Определяем классы
CLASS_NAMES = ['graffiti', 'no_repair', 'scheduled_repair', 'urgent_repair']

# Устройство
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Пути
BASE_DIR = os.path.dirname(__file__)
BEST_MODEL_PATH = os.path.join(BASE_DIR, "model", "best_model.pth")
BEST_ACCURACY_PATH = os.path.join(BASE_DIR, "model", "best_val_accuracy.txt")

# Инициализация модели
model = models.resnet18()
model.fc = nn.Linear(model.fc.in_features, len(CLASS_NAMES))
model.to(device)
model.eval()

# Загружаем текущую лучшую модель
if os.path.exists(BEST_MODEL_PATH) and os.path.exists(BEST_ACCURACY_PATH):
    model.load_state_dict(torch.load(BEST_MODEL_PATH, map_location=device))
    with open(BEST_ACCURACY_PATH, 'r') as f:
        best_val_accuracy = float(f.read())
    print(f"✅ Загружена лучшая модель с точностью {best_val_accuracy:.4f}")
else:
    best_val_accuracy = 0.0
    print("⚠️ Нет сохранённой модели. Начальная точность = 0.0")

# Предобработка изображения
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0).to(device)

# Предсказание одного изображения
def predict_image(image_file):
    if not isinstance(image_file, Image.Image):
        image = Image.open(image_file).convert("RGB")
    else:
        image = image_file.convert("RGB")

    image_tensor = preprocess_image(image)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0).cpu()

    top_prob, top_class = torch.topk(probabilities, 1)
    return CLASS_NAMES[top_class.item()], top_prob.item()

# Функция для проверки и обновления модели после дообучения
def maybe_update_model():
    global best_val_accuracy
    if os.path.exists(os.path.join(BASE_DIR, "model", "last_val_accuracy.txt")):
        with open(os.path.join(BASE_DIR, "model", "last_val_accuracy.txt"), 'r') as f:
            new_accuracy = float(f.read())

        if new_accuracy > best_val_accuracy:
            print(f"🚀 Новая модель лучше! ({new_accuracy:.4f} > {best_val_accuracy:.4f})")
            model.load_state_dict(torch.load(BEST_MODEL_PATH, map_location=device))
            best_val_accuracy = new_accuracy
            with open(BEST_ACCURACY_PATH, 'w') as f:
                f.write(str(best_val_accuracy))
            print("✅ Модель обновлена!")
        else:
            print(f"🔒 Новая модель хуже ({new_accuracy:.4f} <= {best_val_accuracy:.4f}), обновление отменено")
    else:
        print("❌ last_val_accuracy.txt не найден. Пропущено обновление модели.")
