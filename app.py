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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для фронтенда

# Конфигурация
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB максимум
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Создаем папки если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Разрешенные расширения файлов для анализа расстояний
ALLOWED_EXTENSIONS = {
    'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
}


def allowed_file(filename):
    """Проверяет, разрешен ли тип файла"""
    if '.' not in filename:
        return False, None

    extension = filename.rsplit('.', 1)[1].lower()

    if extension in ALLOWED_EXTENSIONS['video']:
        return True, 'video'
    elif extension in ALLOWED_EXTENSIONS['image']:
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


def send_to_distance_analysis_service(file_path, file_type):
    """
    Отправляет файл в сервис анализа расстояний

    TODO: Здесь будет подключен отдельный Python файл с анализом расстояний
    Например: from distance_analyzer import analyze_distances

    Пример интеграции:
    ------------------------
    from distance_analyzer import DistanceAnalyzer

    analyzer = DistanceAnalyzer()
    result = analyzer.process_file(file_path, file_type)

    Или функциональный подход:
    ------------------------
    from distance_analysis import calculate_distances

    distances_result = calculate_distances(
        input_file=file_path,
        file_type=file_type,
        units='meters',
        calibration_object='auto'
    )
    """
    try:
        # ВРЕМЕННАЯ ЗАГЛУШКА - возвращаем исходный файл
        # В дальнейшем здесь будет вызов вашего модуля анализа расстояний
        import time
        import shutil

        logger.info(f"[ЗАГЛУШКА] Имитируем анализ расстояний для файла: {file_path}")

        # Имитируем время анализа - 2 секунды как просил пользователь
        time.sleep(2)

        # Генерируем уникальное имя для "обработанного" файла
        # ВАЖНО: Сохраняем исходное расширение файла
        original_extension = os.path.splitext(file_path)[1]  # Получаем .jpg, .png, .mp4 и т.д.
        analysis_filename = f"distance_analysis_{uuid.uuid4().hex}{original_extension}"
        analysis_path = os.path.join(app.config['PROCESSED_FOLDER'], analysis_filename)

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
            'message': '[ЗАГЛУШКА] Анализ расстояний выполнен (возвращен исходный файл)',
            'distances_calculated': True,  # Флаг успешного вычисления расстояний
            'is_placeholder': True  # Флаг того, что это заглушка
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


@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса анализа расстояний"""
    return jsonify({
        'status': 'healthy',
        'service': 'Distance Analysis Service',
        'timestamp': datetime.now().isoformat(),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'processed_folder': app.config['PROCESSED_FOLDER']
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

        # Проверяем тип файла
        is_allowed, file_type = allowed_file(file.filename)
        if not is_allowed:
            return jsonify({
                'success': False,
                'error': 'Неподдерживаемый тип файла для анализа расстояний'
            }), 400

        # Создаем безопасное имя файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # Сохраняем файл
        file.save(file_path)
        logger.info(f"Файл сохранен для анализа: {file_path}")

        # Получаем информацию о файле
        file_info = get_file_info(file_path)

        # Отправляем файл на анализ расстояний
        analysis_result = send_to_distance_analysis_service(file_path, file_type)

        if analysis_result['success']:
            # Формируем URL для скачивания результата анализа
            analysis_file_url = url_for('download_processed',
                                        filename=analysis_result['processed_file'],
                                        _external=True)

            return jsonify({
                'success': True,
                'message': 'Анализ расстояний успешно выполнен',
                'original_file': unique_filename,
                'processed_file': analysis_result['processed_file'],
                'processed_file_url': analysis_file_url,
                'file_type': file_type,
                'file_info': file_info,
                'distances_calculated': analysis_result.get('distances_calculated', False),
                'is_placeholder': analysis_result.get('is_placeholder', False)  # Флаг заглушки
            })
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
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)

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
        processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)

        if os.path.exists(processed_path):
            file_info = get_file_info(processed_path)
            return jsonify({
                'status': 'completed',
                'file_info': file_info,
                'download_url': url_for('download_processed', filename=filename, _external=True)
            })
        else:
            return jsonify({'status': 'processing'})

    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return jsonify({'error': 'Ошибка получения статуса'}), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Очищает временные файлы (для администрирования)"""
    try:
        import shutil

        # Очищаем папки загрузок и обработанных файлов
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
            os.makedirs(app.config['UPLOAD_FOLDER'])

        if os.path.exists(app.config['PROCESSED_FOLDER']):
            shutil.rmtree(app.config['PROCESSED_FOLDER'])
            os.makedirs(app.config['PROCESSED_FOLDER'])

        return jsonify({
            'success': True,
            'message': 'Временные файлы очищены'
        })

    except Exception as e:
        logger.error(f"Ошибка очистки: {e}")
        return jsonify({'error': 'Ошибка очистки файлов'}), 500


@app.errorhandler(413)
def too_large(e):
    """Обработчик ошибки слишком большого файла"""
    return jsonify({
        'success': False,
        'error': 'Файл слишком большой. Максимальный размер: 100MB'
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Обработчик внутренних ошибок сервера"""
    logger.error(f"Внутренняя ошибка: {error}")
    return jsonify({
        'success': False,
        'error': 'Внутренняя ошибка сервера'
    }), 500


if __name__ == '__main__':
    # Проверяем наличие необходимых папок
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        logger.info(f"Создана папка для загрузок: {app.config['UPLOAD_FOLDER']}")

    if not os.path.exists(app.config['PROCESSED_FOLDER']):
        os.makedirs(app.config['PROCESSED_FOLDER'])
        logger.info(f"Создана папка для результатов анализа: {app.config['PROCESSED_FOLDER']}")

    logger.info("Запуск сервиса анализа расстояний...")
    logger.info(f"Максимальный размер файла: {app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)}MB")
    logger.info("Сервер доступен на: http://localhost:5000")

    app.run(debug=True, host='localhost', port=5000)