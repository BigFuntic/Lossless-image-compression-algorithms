from PIL import Image
import random

def generate_random_image(width, height, output_path="random_image.bmp"):
    # Создаем новое изображение RGB-формата
    image = Image.new("RGB", (width, height))

    # Создаем список случайных пикселей
    pixels = []
    for _ in range(width * height):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        pixels.append((r, g, b))

    # Вставляем пиксели в изображение
    image.putdata(pixels)

    # Сохраняем изображение в формате BMP
    image.save(output_path)
    print(f"Изображение сохранено как {output_path}")

if __name__ == "__main__":
    width = int(input("Введите ширину изображения: "))
    height = int(input("Введите высоту изображения: "))
    generate_random_image(width, height)