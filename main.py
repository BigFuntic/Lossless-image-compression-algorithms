from PIL import Image
import os
import time


def image_to_rle(image_path):
    """Сжимает изображение с помощью RLE и возвращает RLE-данные."""
    img = Image.open(image_path)
    pixels = list(img.getdata())

    if not pixels:
        return []

    rle_data = []
    current_pixel = pixels[0]
    count = 1

    for pixel in pixels[1:]:
        if pixel == current_pixel:
            count += 1
        else:
            rle_data.append((current_pixel, count))
            current_pixel = pixel
            count = 1

    rle_data.append((current_pixel, count))  # Добавляем последний блок
    return rle_data, img.size, img.mode


def save_rle(rle_data, output_path):
    """Сохраняет RLE-данные в текстовый файл."""
    with open(output_path, 'w') as f:
        for pixel, count in rle_data:
            if isinstance(pixel, int):  # Grayscale
                f.write(f"{pixel} {count}\n")
            else:  # RGB
                f.write(f"{' '.join(map(str, pixel))} {count}\n")


def rle_to_image(rle_data, original_size, mode):
    """Восстанавливает изображение из RLE-данных."""
    img = Image.new('RGB' if mode == 'RGB' else 'L', original_size)
    pixels = []

    for pixel, count in rle_data:
        pixels.extend([pixel] * count)

    img.putdata(pixels)
    return img


def format_size(size_bytes):

    return round(size_bytes / 1024)


def print_results(compression_time, decompression_time, original_size, compressed_size):

    print("Результаты сжатия:")
    print(f"Время сжатия: {compression_time:.2f} секунд")
    print(f"Время восстановления: {decompression_time:.2f} секунд")
    print(f"Размер исходного файла: {format_size(original_size)} Кбайт")
    print(f"Размер сжатого файла: {format_size(compressed_size)} Кбайт")
    print(f"Коэффициент сжатия: {original_size / compressed_size:.2f}")


if __name__ == "__main__":
    name = input("Введите название файла: ")
    input_image = "входные данные/" + name  # Путь к исходному изображению
    output_rle = "выходные данные/compressedRLE_"+name+".bin"  # Файл для сохранения RLE-данных
    output_image = "outputRLE.bmp"  # Восстановленное изображение

    # Сжатие с замером времени
    start_compress = time.time()
    rle_data, img_size, img_mode = image_to_rle(input_image)
    save_rle(rle_data, output_rle)
    compression_time = time.time() - start_compress

    # Получение размеров файлов
    original_size = os.path.getsize(input_image)
    compressed_size = os.path.getsize(output_rle)

    # Распаковка с замером времени
    start_decompress = time.time()
    restored_img = rle_to_image(rle_data, img_size, img_mode)
    restored_img.save(output_image)
    decompression_time = time.time() - start_decompress

    # Вывод результатов
    print_results(compression_time, decompression_time, original_size, compressed_size)