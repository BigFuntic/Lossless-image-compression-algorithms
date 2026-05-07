import numpy as np
from PIL import Image
import zlib
import time
import os


def load_image(image_path):
    image = Image.open(image_path).convert('RGB')
    return np.array(image)


def save_image(array, path):
    image = Image.fromarray(array.astype(np.uint8))
    image.save(path)


def predict_channel(channel, predictor_type):
    """Применяет выбранный предсказатель к каналу изображения"""
    height, width = channel.shape
    residual = np.zeros_like(channel, dtype=np.int16)

    for y in range(height):
        for x in range(width):
            current = np.int32(channel[y, x])  # Работаем в int32

            # Получаем соседние пиксели (приводим к int32)
            left = np.int32(channel[y, x - 1]) if x > 0 else np.int32(0)
            top = np.int32(channel[y - 1, x]) if y > 0 else np.int32(0)
            top_left = np.int32(channel[y - 1, x - 1]) if (x > 0 and y > 0) else np.int32(0)

            # Применяем выбранный предсказатель
            if predictor_type == 0:  # Нет предсказания
                pred = np.int32(0)
            elif predictor_type == 1:  # A (левый пиксель)
                pred = left
            elif predictor_type == 2:  # B (верхний пиксель)
                pred = top
            elif predictor_type == 3:  # C (верхний левый пиксель)
                pred = top_left
            elif predictor_type == 4:  # A + B - C
                pred = left + top - top_left
            elif predictor_type == 5:  # A + (B - C)/2
                pred = left + (top - top_left) // 2
            elif predictor_type == 6:  # B + (A - C)/2
                pred = top + (left - top_left) // 2
            elif predictor_type == 7:  # (A + B)/2 (JPEG-LS медианный)
                pred = (left + top) // 2
            else:
                raise ValueError("Неизвестный тип предсказателя")

            # Ограничиваем предсказание и вычисляем разницу
            pred = np.clip(pred, 0, 255).astype(np.int32)
            residual[y, x] = np.int16(current - pred)  # Сохраняем как int16

    return residual


def unpred_channel(residual, predictor_type):
    """Восстанавливает канал изображения из остатков с учетом предсказателя"""
    height, width = residual.shape
    channel = np.zeros_like(residual, dtype=np.int32)  # Промежуточные вычисления в int32

    for y in range(height):
        for x in range(width):
            # Получаем соседние пиксели (уже восстановленные)
            left = channel[y, x - 1] if x > 0 else np.int32(0)
            top = channel[y - 1, x] if y > 0 else np.int32(0)
            top_left = channel[y - 1, x - 1] if (x > 0 and y > 0) else np.int32(0)

            # Применяем тот же предсказатель
            if predictor_type == 0:
                pred = np.int32(0)
            elif predictor_type == 1:
                pred = left
            elif predictor_type == 2:
                pred = top
            elif predictor_type == 3:
                pred = top_left
            elif predictor_type == 4:
                pred = left + top - top_left
            elif predictor_type == 5:
                pred = left + (top - top_left) // 2
            elif predictor_type == 6:
                pred = top + (left - top_left) // 2
            elif predictor_type == 7:
                pred = (left + top) // 2
            else:
                raise ValueError("Неизвестный тип предсказателя")

            # Ограничиваем и восстанавливаем значение
            pred = np.clip(pred, 0, 255).astype(np.int32)
            channel[y, x] = np.int32(residual[y, x]) + pred

    return np.clip(channel, 0, 255).astype(np.uint8)

def compress_image(image, predictor_type=7):
    """Сжимает изображение с выбранным предсказателем (по умолчанию медианный JPEG-LS)"""
    residuals = []
    compressed_channels = []

    for c in range(3):  # R, G, B
        residual = predict_channel(image[:, :, c], predictor_type)
        residuals.append(residual)
        compressed = zlib.compress(residual.astype(np.int16).tobytes(), level=zlib.Z_BEST_COMPRESSION)
        compressed_channels.append(compressed)

    return compressed_channels, image.shape[:2]


def decompress_image(compressed_channels, shape, predictor_type=7):
    """Восстанавливает изображение с учетом типа предсказателя"""
    channels = []

    for compressed in compressed_channels:
        decompressed = zlib.decompress(compressed)
        residual = np.frombuffer(decompressed, dtype=np.int16).reshape(shape)
        channel = unpred_channel(residual, predictor_type)
        channels.append(channel)

    reconstructed_image = np.stack(channels, axis=-1)
    return reconstructed_image


def main(image_path, predictor_type=7):
    # === Загрузка изображения ===
    original_image = load_image(image_path)

    # === Сжатие ===
    start_time = time.time()
    compressed_channels, shape = compress_image(original_image, predictor_type)
    compression_time = time.time() - start_time

    # === Сохранение сжатого файла ===
    os.makedirs("выходные данные", exist_ok=True)
    compressed_file = f"выходные данные/compressedJPEG_{os.path.basename(image_path)}.bin"
    with open(compressed_file, 'wb') as f:
        # Записываем тип предсказателя в заголовок
        f.write(predictor_type.to_bytes(1, 'big'))
        for comp in compressed_channels:
            f.write(len(comp).to_bytes(4, 'big'))  # Заголовок: длина каждого блока
            f.write(comp)

    # === Восстановление ===
    start_time = time.time()
    with open(compressed_file, 'rb') as f:
        # Читаем тип предсказателя
        predictor_type = int.from_bytes(f.read(1), 'big')
        compressed_channels_read = []
        for _ in range(3):
            length = int.from_bytes(f.read(4), 'big')
            comp = f.read(length)
            compressed_channels_read.append(comp)

    reconstructed_image = decompress_image(compressed_channels_read, shape, predictor_type)
    decompression_time = time.time() - start_time

    # === Сохранение восстановленного изображения ===
    os.makedirs("восстановленные", exist_ok=True)
    output_path = f"восстановленные/{os.path.basename(image_path)}_reconstructed.bmp"
    save_image(reconstructed_image, output_path)

    # === Статистика ===
    original_size = os.path.getsize(image_path) / 1024  # в Кбайтах
    compressed_size = os.path.getsize(compressed_file) / 1024  # в Кбайтах
    compression_ratio = original_size / compressed_size if compressed_size != 0 else 0

    print("\nРезультаты сжатия:")
    print(f"Использован предсказатель типа: {predictor_type}")
    print(f"Время сжатия: {compression_time:.2f} секунд")
    print(f"Время восстановления: {decompression_time:.2f} секунд")
    print(f"Размер исходного файла: {original_size:.2f} Кбайт")
    print(f"Размер сжатого файла: {compressed_size:.2f} Кбайт")
    print(f"Коэффициент сжатия: {compression_ratio:.2f}")


if __name__ == '__main__':
    image_path = input("Введите путь к исходному изображению: ")

    predictor_type = int(input("Выберите тип предсказателя (0-7, по умолчанию 7): ") or "7")

    main("входные данные/" +image_path, predictor_type)