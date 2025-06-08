from flask import Flask, request, jsonify, send_file, url_for
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
import requests
import tempfile
import logging
from datetime import datetime
import mimetypes

# Импортируем конфигурацию
from config import get_config, DISTANCE_ANALYSIS_CONFIG, API_CONFIG, NOTIFICATION_CONFIG

# Получаем конфигурацию на основе окружения
config_class = get_config()
config = config_class()

# Настройка логирования из конфига
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE) if hasattr(config, 'LOG_FILE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Применяем конфигурацию к Flask приложению
app.config.from_object(config)

# Настройка CORS с конфигурацией
cors_origins = getattr(config, 'CORS_ORIGINS', ['http://localhost:3000', 'http://127.0.0.1:3000'])

# Добавляем file:// протокол для локальной разработки
cors_origins.extend(['file://', 'null'])

CORS(app,
     origins=['*'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)

# Создаем папки из конфигурации
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.PROCESSED_FOLDER, exist_ok=True)

logger.info(f"Запуск в режиме: {config.__class__.__name__}")
logger.info(f"Upload folder: {config.UPLOAD_FOLDER}")
logger.info(f"Processed folder: {config.PROCESSED_FOLDER}")


def allowed_file(filename):
    """Проверяет, разрешен ли тип файла на основе конфигурации"""
    if '.' not in filename:
        return False, None

    extension = filename.rsplit('.', 1)[1].lower()

    if extension in config.ALLOWED_EXTENSIONS['video']:
        return True, 'video'
    elif extension in config.ALLOWED_EXTENSIONS['image']:
        return True, 'image'

    return False, None


def get_file_info(filepath):
    """Получает информацию о файле"""
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка получения информации о файле: {e}")
        return {}


def convert_sets_to_lists(data):
    """Конвертирует set объекты в списки для JSON сериализации"""
    if isinstance(data, dict):
        return {key: convert_sets_to_lists(value) for key, value in data.items()}
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, (list, tuple)):
        return [convert_sets_to_lists(item) for item in data]
    else:
        return data


def get_supported_formats_json():
    """Возвращает поддерживаемые форматы в JSON-совместимом виде"""
    return convert_sets_to_lists(config.ALLOWED_EXTENSIONS)


def send_to_distance_analysis_service(file_path, file_type):
    """
    Отправляет файл в сервис анализа расстояний

    TODO: Здесь будет подключен отдельный Python файл с анализом расстояний
    Например: from distance_analyzer import analyze_distances

    Пример интеграции:
    ------------------------
    from distance_analyzer import DistanceAnalyzer

    analyzer = DistanceAnalyzer(config=DISTANCE_ANALYSIS_CONFIG)
    result = analyzer.process_file(
        file_path=file_path,
        file_type=file_type,
        units=config.DEFAULT_UNITS,
        timeout=config.ANALYSIS_TIMEOUT
    )

    Или функциональный подход:
    ------------------------
    from distance_analysis import calculate_distances

    distances_result = calculate_distances(
        input_file=file_path,
        file_type=file_type,
        units=config.DEFAULT_UNITS,
        config=DISTANCE_ANALYSIS_CONFIG,
        timeout=config.ANALYSIS_TIMEOUT
    )
    """
    try:
        # ВРЕМЕННАЯ ЗАГЛУШКА - возвращаем исходный файл
        # В дальнейшем здесь будет вызов вашего модуля анализа расстояний
        import time
        import shutil

        logger.info(f"[ЗАГЛУШКА] Имитируем анализ расстояний для файла: {file_path}")
        logger.info(f"[ЗАГЛУШКА] Настройки анализа: units={config.DEFAULT_UNITS}, timeout={config.ANALYSIS_TIMEOUT}")

        # Имитируем время анализа - используем настройку из конфига или 2 секунды по умолчанию
        analysis_time = 2 if config.DEBUG else 3
        time.sleep(analysis_time)

        # Генерируем уникальное имя для "обработанного" файла
        # ВАЖНО: Сохраняем исходное расширение файла
        original_extension = os.path.splitext(file_path)[1]  # Получаем .jpg, .png, .mp4 и т.д.
        analysis_filename = f"distance_analysis_{uuid.uuid4().hex}{original_extension}"
        analysis_path = os.path.join(config.PROCESSED_FOLDER, analysis_filename)

        # ЗАГЛУШКА: просто копируем исходный файл с сохранением формата
        # TODO: Заменить на реальный анализ расстояний
        # Важно: ваш модуль анализа должен также сохранять исходный формат или
        # возвращать результат в подходящем формате
        shutil.copy2(file_path, analysis_path)

        logger.info(f"[ЗАГЛУШКА] Файл скопирован как результат анализа: {analysis_path}")

        # Возвращаем результат в формате, который ожидает система
        return {
            'success': True,
            'processed_file': analysis_filename,
            'message': f'[ЗАГЛУШКА] Анализ расстояний выполнен (units: {config.DEFAULT_UNITS})',
            'distances_calculated': True,  # Флаг успешного вычисления расстояний
            'is_placeholder': True,  # Флаг того, что это заглушка
            'analysis_config': {
                'units': config.DEFAULT_UNITS,
                'timeout': config.ANALYSIS_TIMEOUT,
                'algorithm_config': DISTANCE_ANALYSIS_CONFIG.get('algorithms', {}),
                'processing_config': DISTANCE_ANALYSIS_CONFIG.get(
                    'image_processing' if file_type == 'image' else 'video_processing', {})
            }
        }

    except Exception as e:
        logger.error(f"Ошибка в заглушке анализа расстояний: {e}")
        raise


def create_dummy_video(output_path):
    """Создает демонстрационное видео (заглушка для тестирования)"""
    try:
        # Простая заглушка - создаем минимальное видео
        # В реальности это будет результат обработки от внешнего API
        import subprocess

        # Создаем простое черное видео длительностью 5 секунд
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', 'color=black:size=640x480:duration=5',
            '-c:v', 'libx264',
            '-t', '5',
            output_path
        ]

        # Если ffmpeg не установлен, создаем простой файл-заглушку
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Создаем минимальный MP4 файл как заглушку
            with open(output_path, 'wb') as f:
                # Записываем минимальные заголовки MP4
                f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom')
                f.write(b'\x00' * 1000)  # Заполнитель

    except Exception as e:
        logger.error(f"Ошибка создания демо-видео: {e}")
        # Создаем пустой файл
        with open(output_path, 'wb') as f:
            f.write(b'')


@app.route('/', methods=['GET'])
def index():
    """Главная страница приложения"""
    # Здесь можно либо отдать HTML файл, либо перенаправить
    # Пока просто информируем о доступных endpoints
    return jsonify({
        'service': 'Distance Analysis Service',
        'status': 'running',
        'message': 'Сервис анализа расстояний работает',
        'frontend': 'Откройте index.html в браузере для использования интерфейса',
        'available_endpoints': {
            '/': 'GET - Эта страница',
            '/health': 'GET - Проверка здоровья сервиса',
            '/upload': 'POST - Загрузка файла для анализа',
            '/download/<filename>': 'GET - Скачивание результата',
            '/status/<filename>': 'GET - Статус анализа',
            '/cleanup': 'POST - Очистка временных файлов'
        },
        'note': 'Для использования веб-интерфейса откройте файл index.html в браузере'
    })


@app.route('/app', methods=['GET'])
def serve_app():
    """Отдает HTML интерфейс приложения"""
    # Простой HTML интерфейс встроенный в Flask
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вычисление расстояний</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            background: rgba(30, 30, 45, 0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #64ffda 0%, #1de9b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 30px;
            color: #a0aec0;
        }
        .btn {
            background: linear-gradient(135deg, #64ffda 0%, #1de9b6 100%);
            color: #1a202c;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(100, 255, 218, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(100, 255, 218, 0.4);
        }
        .note {
            background: rgba(45, 55, 72, 0.6);
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .note h3 {
            color: #64ffda;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Настройка завершена!</h1>
        <p>Сервис анализа расстояний успешно запущен</p>

        <a href="/health" class="btn">Проверить статус сервиса</a>

        <div class="note">
            <h3>📋 Для использования интерфейса:</h3>
            <p style="color: #e0e0e0; margin-bottom: 15px;">
                Откройте файл <strong>index.html</strong> в браузере<br>
                или используйте API endpoints для интеграции
            </p>
            <p style="font-size: 0.9rem; color: #a0aec0;">
                API доступен на: <strong>http://localhost:5000</strong>
            </p>
        </div>
    </div>
</body>
</html>
    """
    return html_content


@app.route('/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    """Тестовый endpoint для проверки CORS"""
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'status': 'preflight_ok'})
    else:
        response = jsonify({
            'status': 'cors_test_success',
            'method': request.method,
            'origin': request.headers.get('Origin', 'no_origin'),
            'user_agent': request.headers.get('User-Agent', 'no_user_agent'),
            'timestamp': datetime.now().isoformat()
        })

    # Добавляем CORS заголовки явно для этого endpoint
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

    return response


@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса анализа расстояний"""

    return jsonify({
        'status': 'healthy',
        'service': 'Distance Analysis Service',
        'version': API_CONFIG.get('version', '1.0'),
        'environment': config.__class__.__name__,
        'timestamp': datetime.now().isoformat(),
        'upload_folder': config.UPLOAD_FOLDER,
        'processed_folder': config.PROCESSED_FOLDER,
        'max_file_size_mb': config.MAX_CONTENT_LENGTH / (1024 * 1024),
        'supported_formats': get_supported_formats_json(),  # Используем helper функцию
        'default_units': config.DEFAULT_UNITS,
        'analysis_timeout': config.ANALYSIS_TIMEOUT,
        'debug_mode': config.DEBUG
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обрабатывает загрузку файла для анализа расстояний"""
    try:
        # Проверяем наличие файла в запросе
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Файл не найден в запросе'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'Файл не выбран'}), 400

        # Проверяем тип файла на основе конфигурации
        is_allowed, file_type = allowed_file(file.filename)
        if not is_allowed:
            # Конвертируем set в list для JSON сериализации
            all_formats = []
            for extensions in config.ALLOWED_EXTENSIONS.values():
                all_formats.extend(list(extensions))
            supported_formats = ', '.join(all_formats)

            return jsonify({
                'success': False,
                'error': f'Неподдерживаемый тип файла для анализа расстояний. Поддерживаются: {supported_formats}'
            }), 400

        # Создаем безопасное имя файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)

        # Сохраняем файл
        file.save(file_path)
        logger.info(f"Файл сохранен для анализа: {file_path}")

        # Получаем информацию о файле
        file_info = get_file_info(file_path)

        # Отправляем файл на анализ расстояний с настройками из конфига
        analysis_result = send_to_distance_analysis_service(file_path, file_type)

        if analysis_result['success']:
            # Формируем URL для скачивания результата анализа
            analysis_file_url = url_for('download_processed',
                                        filename=analysis_result['processed_file'],
                                        _external=True)

            response_data = {
                'success': True,
                'message': 'Анализ расстояний успешно выполнен',
                'original_file': unique_filename,
                'processed_file': analysis_result['processed_file'],
                'processed_file_url': analysis_file_url,
                'file_type': file_type,
                'file_info': file_info,
                'distances_calculated': analysis_result.get('distances_calculated', False),
                'is_placeholder': analysis_result.get('is_placeholder', False),  # Флаг заглушки
                'analysis_settings': {
                    'units': config.DEFAULT_UNITS,
                    'timeout': config.ANALYSIS_TIMEOUT,
                    'environment': config.__class__.__name__
                }
            }

            # Добавляем конфигурацию анализа если есть
            if 'analysis_config' in analysis_result:
                # Конвертируем любые set объекты в списки
                response_data['analysis_config'] = convert_sets_to_lists(analysis_result['analysis_config'])

            return jsonify(response_data)
        else:
            # Удаляем загруженный файл при ошибке
            try:
                os.remove(file_path)
            except:
                pass

            return jsonify({
                'success': False,
                'error': 'Ошибка анализа расстояний'
            }), 500

    except Exception as e:
        logger.error(f"Ошибка при анализе файла: {e}")
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_processed(filename):
    """Возвращает обработанный файл для скачивания"""
    try:
        file_path = os.path.join(config.PROCESSED_FOLDER, filename)

        if not os.path.exists(file_path):
            return jsonify({'error': 'Файл не найден'}), 404

        # Определяем MIME тип
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mime_type
        )

    except Exception as e:
        logger.error(f"Ошибка при скачивании файла: {e}")
        return jsonify({'error': 'Ошибка скачивания файла'}), 500


@app.route('/status/<filename>')
def get_file_status(filename):
    """Получает статус обработки файла"""
    try:
        processed_path = os.path.join(config.PROCESSED_FOLDER, filename)

        if os.path.exists(processed_path):
            file_info = get_file_info(processed_path)
            return jsonify({
                'status': 'completed',
                'file_info': file_info,
                'download_url': url_for('download_processed', filename=filename, _external=True),
                'analysis_settings': {
                    'units': config.DEFAULT_UNITS,
                    'environment': config.__class__.__name__,
                    'supported_formats': get_supported_formats_json()  # Безопасная сериализация
                }
            })
        else:
            return jsonify({
                'status': 'processing',
                'estimated_time': config.ANALYSIS_TIMEOUT
            })

    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return jsonify({'error': 'Ошибка получения статуса'}), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Очищает временные файлы (для администрирования)"""
    try:
        import shutil

        # Очищаем папки загрузок и обработанных файлов
        if os.path.exists(config.UPLOAD_FOLDER):
            shutil.rmtree(config.UPLOAD_FOLDER)
            os.makedirs(config.UPLOAD_FOLDER)

        if os.path.exists(config.PROCESSED_FOLDER):
            shutil.rmtree(config.PROCESSED_FOLDER)
            os.makedirs(config.PROCESSED_FOLDER)

        logger.info("Временные файлы очищены")

        return jsonify({
            'success': True,
            'message': 'Временные файлы очищены',
            'upload_folder': config.UPLOAD_FOLDER,
            'processed_folder': config.PROCESSED_FOLDER
        })

    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        return jsonify({'error': 'Ошибка очистки файлов'}), 500


@app.errorhandler(TypeError)
def handle_json_error(e):
    """Обработчик ошибок JSON сериализации"""
    if "not JSON serializable" in str(e):
        logger.error(f"JSON serialization error: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка формирования ответа сервера',
            'details': 'JSON serialization error' if config.DEBUG else None
        }), 500

    # Если это не JSON ошибка, передаем дальше
    raise e


@app.errorhandler(413)
def too_large(e):
    """Обработчик ошибки слишком большого файла"""
    max_size_mb = config.MAX_CONTENT_LENGTH / (1024 * 1024)
    return jsonify({
        'success': False,
        'error': f'Файл слишком большой. Максимальный размер: {max_size_mb:.0f}MB'
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Обработчик внутренних ошибок сервера"""
    logger.error(f"Внутренняя ошибка: {error}")

    error_response = {
        'success': False,
        'error': 'Внутренняя ошибка сервера'
    }

    # В debug режиме добавляем больше информации
    if config.DEBUG:
        error_response['debug_info'] = {
            'error_type': str(type(error)),
            'error_message': str(error)
        }

    return jsonify(error_response), 500


if __name__ == '__main__':
    # Проверяем наличие необходимых папок
    if not os.path.exists(config.UPLOAD_FOLDER):
        os.makedirs(config.UPLOAD_FOLDER)
        logger.info(f"Создана папка для загрузок: {config.UPLOAD_FOLDER}")

    if not os.path.exists(config.PROCESSED_FOLDER):
        os.makedirs(config.PROCESSED_FOLDER)
        logger.info(f"Создана папка для результатов анализа: {config.PROCESSED_FOLDER}")

    # Информация о запуске с использованием конфигурации
    logger.info("=" * 60)
    logger.info("🚀 Запуск сервиса анализа расстояний")
    logger.info("=" * 60)
    logger.info(f"📊 Режим работы: {config.__class__.__name__}")
    logger.info(f"🐛 Debug режим: {config.DEBUG}")
    logger.info(f"📁 Папка загрузок: {config.UPLOAD_FOLDER}")
    logger.info(f"📁 Папка результатов: {config.PROCESSED_FOLDER}")
    logger.info(f"📦 Максимальный размер файла: {config.MAX_CONTENT_LENGTH / (1024 * 1024):.0f}MB")
    logger.info(f"⏱️  Таймаут анализа: {config.ANALYSIS_TIMEOUT} сек")
    logger.info(f"📏 Единицы измерения по умолчанию: {config.DEFAULT_UNITS}")
    logger.info(f"🎯 Поддерживаемые форматы:")
    for file_type, extensions in config.ALLOWED_EXTENSIONS.items():
        logger.info(f"   {file_type}: {', '.join(extensions)}")
    logger.info(f"🌐 Сервер доступен на: http://localhost:5000")
    logger.info("=" * 60)

    # Запуск приложения с настройками из конфигурации
    app.run(
        debug=config.DEBUG,
        host='localhost',
        port=5000,
        threaded=True  # Разрешаем множественные подключения
    )
