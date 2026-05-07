import zlib
import os
import time
from PIL import Image
import io

def compress_image(input_image_path, compressed_output_path, decompressed_output_path):
    # Чтение исходного изображения
    start_compress = time.time()
    with open(input_image_path, 'rb') as f:
        original_data = f.read()
    original_size = os.path.getsize(input_image_path)

    # Сжатие (Deflate)

    compressed_data = zlib.compress(original_data, level=1)
    compress_time = time.time() - start_compress

    # Сохранение сжатых данных
    with open(compressed_output_path, 'wb') as f:
        f.write(compressed_data)
    compressed_size = os.path.getsize(compressed_output_path)

    # Восстановление
    start_decompress = time.time()
    decompressed_data = zlib.decompress(compressed_data)
    decompress_time = time.time() - start_decompress

    # Сохранение восстановленного изображения
    with open(decompressed_output_path, 'wb') as f:
        f.write(decompressed_data)

    # Проверка целостности данных
    assert original_data == decompressed_data, "Ошибка: восстановленные данные не совпадают с исходными!"

    # Вывод результатов
    compression_ratio = original_size / compressed_size if compressed_size != 0 else 0

    print("Результаты сжатия:")
    print(f"Время сжатия: {compress_time:.2f} секунд")
    print(f"Время восстановления: {decompress_time:.2f} секунд")
    print(f"Размер исходного файла: {original_size / 1024:.2f} Кбайт")
    print(f"Размер сжатого файла: {compressed_size / 1024:.2f} Кбайт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")

input_image = input("Введите путь к исходному изображению: ")

compressed_output = "выходные данные/compressedDeflate_"+input_image+".bin"# Выходной сжатый файл
decompressed_output = "outputDeflate.bmp"  # Восстановленное изображение

compress_image("входные данные/" + input_image, compressed_output, decompressed_output)