import time
import os
import pickle
import numpy as np
from PIL import Image


def lzw_compress(uncompressed):
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    w = b""
    result = []

    for c in uncompressed:
        wc = w + bytes([c])
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytes([c])
    if w:
        result.append(dictionary[w])
    return result


def lzw_decompress(compressed):
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}
    result = bytearray()
    w = bytes([compressed.pop(0)])
    result += w

    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + bytes([w[0]])
        else:
            raise ValueError("Ошибка декомпрессии")
        result += entry
        dictionary[dict_size] = w + bytes([entry[0]])
        dict_size += 1
        w = entry

    return result


def compress_image_lzw_rgb(image_path, compressed_path):
    image = Image.open(image_path).convert('RGB')
    r, g, b = image.split()

    width, height = image.size
    original_size = width * height * 3  # 3 канала

    r_bytes = np.array(r).flatten().tobytes()
    g_bytes = np.array(g).flatten().tobytes()
    b_bytes = np.array(b).flatten().tobytes()

    start_time = time.time()
    r_compressed = lzw_compress(r_bytes)
    g_compressed = lzw_compress(g_bytes)
    b_compressed = lzw_compress(b_bytes)
    compression_time = time.time() - start_time

    with open(compressed_path, 'wb') as f:
        pickle.dump(((r_compressed, g_compressed, b_compressed), image.size), f)

    return compression_time, image.size, original_size


def decompress_image_lzw_rgb(compressed_path, output_image_path):
    start_time = time.time()
    with open(compressed_path, 'rb') as f:
        (r_c, g_c, b_c), size = pickle.load(f)

    r_bytes = lzw_decompress(r_c)
    g_bytes = lzw_decompress(g_c)
    b_bytes = lzw_decompress(b_c)
    decompression_time = time.time() - start_time

    width, height = size
    r = np.frombuffer(r_bytes, dtype=np.uint8).reshape((height, width))
    g = np.frombuffer(g_bytes, dtype=np.uint8).reshape((height, width))
    b = np.frombuffer(b_bytes, dtype=np.uint8).reshape((height, width))

    image = Image.merge('RGB', (Image.fromarray(r),
                                Image.fromarray(g),
                                Image.fromarray(b)))
    image.save(output_image_path)

    return decompression_time


def format_size(bytes_size):
    return f"{bytes_size / 1024:.0f} Кбайт"


def main():
    name = input("Введите название файла: ")
    input_image = "входные данные/" + name  # Путь к исходному изображению
    output_lzw = "выходные данные/compressedLZW_"+name+".txt"  # Файл для сохранения LZW-данных
    output_image = "outputLZW.bmp"  # Восстановленное изображение

    compression_time, image_size, original_size = compress_image_lzw_rgb(input_image, output_lzw)
    decompression_time = decompress_image_lzw_rgb(output_lzw, output_image)
    compressed_size = os.path.getsize(output_lzw)
    compression_ratio = original_size / compressed_size if compressed_size != 0 else 0

    print("Результаты сжатия:")
    print(f"Время сжатия: {compression_time:.2f} секунд")
    print(f"Время восстановления: {decompression_time:.2f} секунд")
    print(f"Размер исходного файла: {format_size(original_size)}")
    print(f"Размер сжатого файла: {format_size(compressed_size)}")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")


if __name__ == "__main__":
    main()
