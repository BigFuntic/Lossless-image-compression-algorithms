import heapq
import os
import time
from collections import defaultdict
from PIL import Image
import numpy as np
import pickle


class HuffmanNode:
    def __init__(self, value=None, freq=0, left=None, right=None):
        self.value = value
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_frequency_dict(data):
    frequency = defaultdict(int)
    for pixel in data:
        frequency[pixel] += 1
    return frequency


def build_huffman_tree(frequency):
    heap = []
    for value, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(value=value, freq=freq))

    # Особый случай: если все пиксели одинаковые
    if len(heap) == 1:
        node = heapq.heappop(heap)
        dummy = HuffmanNode(freq=0)  # Создаем фиктивный узел
        return HuffmanNode(freq=node.freq, left=node, right=dummy)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)

    return heapq.heappop(heap)


def build_codebook(root, prefix="", codebook=None):
    if codebook is None:
        codebook = {}

    if root.value is not None:
        codebook[root.value] = prefix
    else:
        build_codebook(root.left, prefix + "0", codebook)
        if root.right.freq > 0:  # Игнорируем фиктивные узлы
            build_codebook(root.right, prefix + "1", codebook)

    return codebook


def encode_data(data, codebook):
    encoded_bits = []
    for pixel in data:
        encoded_bits.append(codebook[pixel])

    encoded_str = ''.join(encoded_bits)

    # Добавляем padding, чтобы длина была кратна 8
    padding = 8 - len(encoded_str) % 8
    if padding == 8: padding = 0
    encoded_str += '0' * padding

    # Конвертируем строку битов в байты
    encoded_bytes = bytearray()
    for i in range(0, len(encoded_str), 8):
        byte = encoded_str[i:i + 8]
        encoded_bytes.append(int(byte, 2))

    return bytes(encoded_bytes), padding


def decode_data(encoded_bytes, padding, root, original_length):
    bit_str = []
    for byte in encoded_bytes:
        bits = bin(byte)[2:].rjust(8, '0')
        bit_str.append(bits)

    bit_str = ''.join(bit_str)
    bit_str = bit_str[:-padding] if padding > 0 else bit_str

    decoded_data = []
    current_node = root

    # Особый случай: если все пиксели одинаковые
    if root.left and root.left.value is not None and root.right.freq == 0:
        value = root.left.value
        decoded_data = [value] * original_length
        return decoded_data

    for bit in bit_str:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.value is not None:
            decoded_data.append(current_node.value)
            current_node = root

    return decoded_data


def compress_image(input_path, output_path):
    start_time = time.time()

    # Загрузка изображения
    img = Image.open(input_path)
    img_array = np.array(img)
    original_shape = img_array.shape

    # Преобразуем в 1D массив
    if len(original_shape) == 3:
        # Для цветных изображений (R, G, B каналы)
        data = []
        for i in range(original_shape[0]):
            for j in range(original_shape[1]):
                for k in range(original_shape[2]):
                    data.append(img_array[i, j, k])
    else:
        # Для grayscale изображений
        data = img_array.flatten().tolist()

    # Построение дерева Хаффмана
    frequency = build_frequency_dict(data)
    huffman_tree = build_huffman_tree(frequency)
    codebook = build_codebook(huffman_tree)

    # Кодирование данных
    encoded_data, padding = encode_data(data, codebook)

    # Сохранение сжатых данных
    with open(output_path, 'wb') as f:
        # Сохраняем метаданные
        pickle.dump({
            'original_shape': original_shape,
            'padding': padding,
            'huffman_tree': huffman_tree,
            'original_length': len(data)
        }, f)
        # Сохраняем закодированные данные
        f.write(encoded_data)

    compression_time = time.time() - start_time
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)

    return compression_time, original_size, compressed_size


def decompress_image(input_path, output_path):
    start_time = time.time()

    # Чтение сжатых данных
    with open(input_path, 'rb') as f:
        metadata = pickle.load(f)
        encoded_data = f.read()

    # Декодирование данных
    decoded_data = decode_data(
        encoded_data,
        metadata['padding'],
        metadata['huffman_tree'],
        metadata['original_length']
    )

    # Восстановление изображения
    if len(metadata['original_shape']) == 3:
        # Для цветных изображений
        img_array = np.zeros(metadata['original_shape'], dtype=np.uint8)
        idx = 0
        for i in range(metadata['original_shape'][0]):
            for j in range(metadata['original_shape'][1]):
                for k in range(metadata['original_shape'][2]):
                    img_array[i, j, k] = decoded_data[idx]
                    idx += 1
    else:
        # Для grayscale изображений
        img_array = np.array(decoded_data, dtype=np.uint8).reshape(metadata['original_shape'])

    # Сохранение восстановленного изображения
    img = Image.fromarray(img_array)
    img.save(output_path)

    decompression_time = time.time() - start_time
    return decompression_time
def main():
    input_image = input("Введите путь к исходному изображению: ")
    compressed_file = "выходные данные/compressedHuffman_"+input_image+".bin"
    output_image = "outputHuffman.bmp"

    # Сжатие
    compress_time, original_size, compressed_size = compress_image("входные данные/" + input_image, compressed_file)

    # Восстановление
    decompress_time = decompress_image(compressed_file, output_image)

    # Вывод результатов
    print("\nРезультаты сжатия:")
    print(f"Время сжатия: {compress_time:.2f} секунд")
    print(f"Время восстановления: {decompress_time:.2f} секунд")
    print(f"Размер исходного файла: {original_size} Кбайт")
    print(f"Размер сжатого файла: {compressed_size} Кбайт")
    print(f"Коэффициент сжатия: {original_size / compressed_size:.2f}")

    # Проверка целостности
    original_img = Image.open("входные данные/" +input_image)
    decompressed_img = Image.open(output_image)

    if np.array_equal(np.array(original_img), np.array(decompressed_img)):
        print("\nПроверка целостности: изображение восстановлено без потерь")
    else:
        print("\nПроверка целостности: обнаружены различия в изображениях")


if __name__ == "__main__":
    main()