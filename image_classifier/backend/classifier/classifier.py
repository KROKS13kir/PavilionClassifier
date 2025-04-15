# image_classifier/classifier.py
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import os

# Определяем классы
CLASS_NAMES = ['graffity', 'no_repair', 'scheduled_repair', 'urgent_repair']

# Устройство
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Загрузка модели
def load_model():
    model = models.resnet18()
    num_classes = len(CLASS_NAMES)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(os.path.join(os.path.dirname(__file__), "model/best_model.pth"), map_location=device))
    model.to(device)
    model.eval()
    return model

model = load_model()

# Предобработка изображения
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0).to(device)

# Функция предсказания
def predict_image(image_path):
    image = Image.open(image_path)
    image_tensor = preprocess_image(image)

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0).cpu()

    top_prob, top_class = torch.topk(probabilities, 1)
    return CLASS_NAMES[top_class.item()], top_prob.item()
