# Вычисление расстояний - Инструкция по запуску

Современное веб-приложение для анализа изображений и видео с автоматическим вычислением расстояний. Темный современный интерфейс с drag-n-drop функциональностью.

## 🚀 Быстрый старт

### 1. Установка зависимостей

Создайте виртуальное окружение и установите зависимости:

```bash
# Создание виртуального окружения
python -m venv distance_calculator_env

# Активация (Windows)
distance_calculator_env\Scripts\activate

# Активация (macOS/Linux)
source distance_calculator_env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Структура проекта

Создайте следующую структуру папок:

```
distance_calculator/
├── app.py                 # Flask сервер анализа расстояний
├── requirements.txt       # Зависимости Python
├── index.html            # Темный веб-интерфейс
├── uploads/              # Папка для загруженных файлов (создается автоматически)
└── processed/            # Папка для результатов анализа (создается автоматически)
```

### 3. Запуск приложения

```bash
# Запуск сервера анализа расстояний
python app.py
```

Сервер запустится на `http://localhost:5000`

### 4. Доступ к приложению

После запуска сервера у вас есть несколько вариантов:

#### Вариант 1: Полный веб-интерфейс (рекомендуется)
Откройте файл `index.html` в браузере - получите полный интерфейс с drag-n-drop

#### Вариант 2: Информационная страница сервера
- `http://localhost:5000/` - JSON информация о сервисе
- `http://localhost:5000/app` - HTML страница с информацией о запуске
- `http://localhost:5000/health` - проверка здоровья сервиса

#### Вариант 3: Прямое использование API
Используйте endpoints напрямую для интеграции с другими приложениями

## ⚠️ Текущее состояние: ЗАГЛУШКА

**ВАЖНО**: Сейчас приложение работает в режиме заглушки и просто возвращает исходный файл без изменений. Это сделано для тестирования интерфейса.

В логах сервера вы увидите сообщения:
- `[ЗАГЛУШКА] Имитируем анализ расстояний для файла: ...`
- `[ЗАГЛУШКА] Файл скопирован как результат анализа: ...`

Когда будете готовы подключить реальный анализ расстояний, замените функцию `send_to_distance_analysis_service()` согласно инструкциям ниже.

### Тестирование заглушки

При тестировании текущей версии:
1. Загрузите любое изображение или видео
2. **Предварительный просмотр остается видимым** во время обработки
3. **Уведомления показывают прогресс** в правом верхнем углу:
   - ℹ️ "Начинаем анализ расстояний..."
   - ⏳ "Загружаем файл на сервер..."
   - ⏳ "Файл загружен, выполняем анализ..."
   - ✅ "Анализ завершен успешно!"
4. Система выполняет "анализ" в течение **2 секунд**
5. В результате вы получите тот же файл в том же формате
6. **Скачивается именно результирующий файл** (пока это копия исходного)
7. **Изображения отображаются как изображения**, **видео как видео**
8. В логах сервера будут сообщения с пометкой `[ЗАГЛУШКА]`

Это нормальное поведение для текущей версии.

## 🔧 **Новые улучшения UX:**

- ✅ **Предварительный просмотр** остается видимым во время обработки
- ✅ **Прогресс-уведомления** с иконками и автоскрытием
- ✅ **Скачивание результата** (сейчас копии исходного файла)
- ✅ **Время обработки** увеличено до 2 секунд для реалистичности

## 🔧 **Исправленные проблемы:**

- ✅ **Убрано дублирование** диалога выбора файла
- ✅ **Сохранение исходного формата** (.jpg остается .jpg, .mp4 остается .mp4)
- ✅ **Корректное отображение** результатов (изображения как изображения, видео как видео)

## 🎯 Основные возможности

- **Темный современный интерфейс** с градиентами и анимациями
- **Drag & Drop загрузка** медиа-файлов
- **Автоматический анализ** расстояний в изображениях и видео (пока заглушка)
- **Предварительный просмотр** загруженных файлов
- **Визуализация результатов** анализа
- **Скачивание результатов** с вычисленными расстояниями

- **Темный современный интерфейс** с градиентами и анимациями
- **Drag & Drop загрузка** медиа-файлов
- **Автоматический анализ** расстояний в изображениях и видео (заглушка)
- **Предварительный просмотр** загруженных файлов
- **Визуализация результатов** анализа
- **Скачивание результатов** с вычисленными расстояниями

- **Темный современный интерфейс** с градиентами и анимациями
- **Drag & Drop загрузка** медиа-файлов
- **Автоматический анализ** расстояний в изображениях и видео
- **Предварительный просмотр** загруженных файлов
- **Визуализация результатов** анализа
- **Скачивание результатов** с вычисленными расстояниями

## 🔧 Интеграция с модулем анализа расстояний

### Текущее состояние - ЗАГЛУШКА

Сейчас приложение работает в режиме заглушки и просто возвращает исходный файл. 

### Подключение вашего модуля анализа

В файле `app.py` найдите функцию `send_to_distance_analysis_service()`. Там есть подробные комментарии о том, как интегрировать ваш отдельный Python файл:

#### Вариант 1: Функциональный подход
```python
# В начале app.py добавьте импорт вашего модуля
from your_distance_module import calculate_distances

def send_to_distance_analysis_service(file_path, file_type):
    try:
        # Вызов вашей функции анализа расстояний
        result = calculate_distances(
            input_file=file_path,
            file_type=file_type,
            units='meters',
            calibration_object='auto'
        )
        
        return {
            'success': True,
            'processed_file': result['output_filename'],
            'message': 'Анализ расстояний выполнен',
            'distances_calculated': True,
            'distances_data': result['distances']  # ваши данные о расстояниях
        }
    except Exception as e:
        logger.error(f"Ошибка анализа расстояний: {e}")
        raise
```

#### Вариант 2: Объектно-ориентированный подход
```python
# В начале app.py
from your_distance_module import DistanceAnalyzer

# Создание экземпляра анализатора
analyzer = DistanceAnalyzer()

def send_to_distance_analysis_service(file_path, file_type):
    try:
        result = analyzer.process_file(file_path, file_type)
        return {
            'success': True,
            'processed_file': result.output_filename,
            'message': 'Анализ расстояний выполнен',
            'distances_calculated': True
        }
    except Exception as e:
        logger.error(f"Ошибка анализа расстояний: {e}")
        raise
```

### Структура вашего модуля анализа

Создайте файл `distance_analyzer.py` рядом с `app.py`:

```python
# distance_analyzer.py
import cv2
import numpy as np
import os

def calculate_distances(input_file, file_type, units='meters', calibration_object='auto'):
    """
    Главная функция анализа расстояний
    
    Args:
        input_file (str): Путь к входному файлу
        file_type (str): Тип файла ('image' или 'video')
        units (str): Единицы измерения ('meters', 'pixels', 'cm')
        calibration_object (str): Метод калибровки
    
    Returns:
        dict: Результат анализа с путем к выходному файлу
    """
    
    if file_type == 'image':
        return analyze_image_distances(input_file, units, calibration_object)
    elif file_type == 'video':
        return analyze_video_distances(input_file, units, calibration_object)
    else:
        raise ValueError(f"Неподдерживаемый тип файла: {file_type}")

def analyze_image_distances(image_path, units, calibration_object):
    """Анализ расстояний на изображении"""
    # Ваш код анализа изображения
    # ...
    
    # ВАЖНО: Сохраняем исходный формат файла
    original_extension = os.path.splitext(image_path)[1]  # .jpg, .png и т.д.
    output_filename = f"analyzed_{uuid.uuid4().hex}{original_extension}"
    output_path = os.path.join('processed', output_filename)
    
    # Сохраните результат в папку 'processed' с тем же расширением
    # cv2.imwrite(output_path, processed_image)  # для изображений
    
    return {
        'output_filename': output_filename,
        'distances': [...]  # ваши данные о расстояниях
    }

def analyze_video_distances(video_path, units, calibration_object):
    """Анализ расстояний в видео"""
    # Ваш код анализа видео
    # ...
    
    # ВАЖНО: Сохраняем исходный формат видео
    original_extension = os.path.splitext(video_path)[1]  # .mp4, .avi и т.д.
    output_filename = f"analyzed_{uuid.uuid4().hex}{original_extension}"
    output_path = os.path.join('processed', output_filename)
    
    # Сохраните результат в папку 'processed' с тем же расширением
    # Используйте cv2.VideoWriter или ffmpeg для сохранения видео
    
    return {
        'output_filename': output_filename,
        'distances': [...]  # ваши данные о расстояниях
    }
```
```

### Настройка CORS

Если фронтенд размещен на другом домене, обновите настройки CORS в `app.py`:

```python
CORS(app, origins=['http://your-frontend-domain.com'])
```

## 📁 API Endpoints

### POST /upload
Загрузка и анализ файла для вычисления расстояний
- **Параметры**: `file` (multipart/form-data)
- **Поддерживаемые форматы**: MP4, AVI, MOV, JPG, PNG
- **Максимальный размер**: 100MB
- **Возвращает**: результат анализа с вычисленными расстояниями

### GET /download/{filename}
Скачивание файла с результатами анализа расстояний

### GET /status/{filename}
Проверка статуса анализа расстояний

### GET /health
Проверка работоспособности сервиса анализа

## 🎨 Особенности темного интерфейса

- **Темная цветовая схема**: Современные темно-синие и черные оттенки
- **Неоновые акценты**: Cyan/teal градиенты для кнопок и элементов
- **Drag & Drop**: Анимированная зона загрузки файлов
- **Прогресс анализа**: Стильный индикатор обработки
- **Адаптивный дизайн**: Отличное отображение на всех устройствах
- **Стеклянные эффекты**: Backdrop blur и прозрачности

## 🔧 Настройки анализа

### Единицы измерения

В API можно настроить различные единицы измерения:
```python
data = {
    'units': 'meters',     # метры
    'units': 'centimeters', # сантиметры  
    'units': 'pixels',     # пиксели
    'units': 'feet',       # футы
    'units': 'inches'      # дюймы
}
```

### Калибровка расстояний

Для точного измерения можно указать эталонный объект:
```python
data = {
    'reference_object_size': '10cm',  # размер эталонного объекта
    'reference_object_type': 'coin',  # тип объекта (монета, линейка и т.д.)
    'calibration_mode': 'auto'        # автоматическая/ручная калибровка
}
```

## 🚦 Процесс анализа

1. **Загрузка**: Файл загружается через drag-n-drop или кнопку
2. **Предобработка**: Система подготавливает изображение/видео
3. **Анализ**: Алгоритм определяет объекты и вычисляет расстояния
4. **Визуализация**: Создается файл с отмеченными расстояниями
5. **Результат**: Пользователь получает обработанный файл

## 🔒 Безопасность и производительность

- Проверка типов и размеров файлов
- Безопасные имена файлов
- Ограничение размера загрузки (100MB)
- Автоматическая очистка временных файлов
- Обработка ошибок на всех уровнях

## 🐛 Решение проблем

### Файл не загружается
- Проверьте тип файла (поддерживаются JPG, PNG, MP4, AVI, MOV)
- Убедитесь, что размер файла не превышает 100MB

### Долгий анализ
- Большие файлы требуют больше времени для анализа
- Проверьте подключение к внешнему API анализа

### Ошибки API
- Убедитесь, что сервер запущен на localhost:5000
- Проверьте настройки CORS
- Проверьте логи сервера в консоли

## 📚 Дополнительные возможности

### Пакетный анализ
Для обработки нескольких файлов можно добавить:
```python
@app.route('/batch_upload', methods=['POST'])
def batch_upload():
    files = request.files.getlist('files')
    results = []
    for file in files:
        # Анализ каждого файла
        result = analyze_distances(file)
        results.append(result)
    return jsonify(results)
```

### Экспорт результатов
Добавьте различные форматы экспорта:
```python
@app.route('/export/<format>/<filename>')
def export_results(format, filename):
    if format == 'json':
        return export_as_json(filename)
    elif format == 'csv':
        return export_as_csv(filename)
    elif format == 'pdf':
        return export_as_pdf(filename)
```

---

**Проект**: Вычисление расстояний  
**Версия**: 1.0.0  
**Тема**: Темная  
**Сервер**: localhost:5000