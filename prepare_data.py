import os
import shutil
import random
from PIL import Image, ImageOps

# --- Параметры ---
INPUT_FOLDER = "dataset/raw/"  # Исходные фото
OUTPUT_TRAIN = "dataset/train/"  # Куда сохранять train
OUTPUT_VAL = "dataset/val/"  # Куда сохранять val
IMG_SIZE = (224, 224)  # Размер изображений
VAL_SPLIT = 0.2  # 20% фото уйдёт в валидацию

# --- Фильтруем файлы только по поддерживаемым форматам ---
SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.webp', '.jfif')

# --- Функция обработки изображений ---
def process_image(image_path, output_path):
    with Image.open(image_path) as img:
        img = ImageOps.exif_transpose(img)  # Разворачиваем изображение, если оно перевёрнуто
        img = img.convert("RGB")  # Преобразуем в RGB (избавляемся от альфа-канала)
        img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)  # Изменяем размер

        img.save(output_path, "JPEG", quality=95)  # Сохраняем в JPEG

# --- Создание папок ---
for category in os.listdir(INPUT_FOLDER):
    category_path = os.path.join(INPUT_FOLDER, category)

    if not os.path.isdir(category_path):  # Проверяем, что это папка
        continue

    os.makedirs(os.path.join(OUTPUT_TRAIN, category), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_VAL, category), exist_ok=True)

    # Фильтруем изображения по расширению
    image_files = [f for f in os.listdir(category_path) if f.lower().endswith(SUPPORTED_FORMATS)]
    random.shuffle(image_files)  # Перемешиваем файлы

    val_size = int(len(image_files) * VAL_SPLIT)
    val_files = image_files[:val_size]
    train_files = image_files[val_size:]

    # Обрабатываем и сохраняем изображения
    for file in train_files:
        input_path = os.path.join(category_path, file)
        output_path = os.path.join(OUTPUT_TRAIN, category, os.path.splitext(file)[0] + ".jpg")
        process_image(input_path, output_path)

    for file in val_files:
        input_path = os.path.join(category_path, file)
        output_path = os.path.join(OUTPUT_VAL, category, os.path.splitext(file)[0] + ".jpg")
        process_image(input_path, output_path)

print("✅ Все изображения обработаны, JFIF конвертированы и распределены по train/ и val/!")
