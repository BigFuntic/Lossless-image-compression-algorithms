import numpy as np
from PIL import Image

def create_chessboard(width, height, cell_size=50):

    # Создаем пустое изображение (черное по умолчанию)
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Заполняем изображение шахматной сеткой
    for y in range(height):
        for x in range(width):
            # Определяем, в какой клетке находимся
            cell_x = x // cell_size
            cell_y = y // cell_size

            # Если сумма индексов клетки четная — белый цвет, иначе — черный
            if (cell_x + cell_y) % 2 == 0:
                img[y, x] = [255, 255, 255]  # Белый цвет

    # Преобразуем массив numpy в изображение
    image = Image.fromarray(img, 'RGB')
    return image


if __name__ == "__main__":
    width = int(input("Введите ширину изображения: "))
    height = int(input("Введите высоту изображения: "))
    cell_size = int(input("Введите размер клетки (по умолчанию 50): ") or 50)

    chessboard = create_chessboard(width, height, cell_size)
    chessboard.save("chessboard.bmp")
    print("Изображение сохранено как 'chessboard.bmp'.")