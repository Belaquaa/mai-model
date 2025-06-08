"""
Конфигурация для приложения вычисления расстояний
"""
import os
from datetime import timedelta

class Config:
    """Базовая конфигурация"""

    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed')

    # Поддерживаемые форматы файлов
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'webm'},
        'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    }

    # Настройки анализа расстояний
    ANALYSIS_TIMEOUT = 300  # 5 минут на анализ
    DEFAULT_UNITS = 'meters'
    SUPPORTED_UNITS = ['meters', 'centimeters', 'pixels', 'feet', 'inches']

    # Настройки очистки временных файлов
    CLEANUP_INTERVAL = timedelta(hours=24)  # Очистка каждые 24 часа
    FILE_RETENTION_DAYS = 7  # Хранить файлы 7 дней

    # CORS настройки
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # Логирование
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'distance_calculator.log')

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True

    # Более подробное логирование в dev режиме
    LOG_LEVEL = 'DEBUG'

    # Меньше ограничений для разработки
    ANALYSIS_TIMEOUT = 60  # 1 минута для быстрого тестирования
    FILE_RETENTION_DAYS = 1  # Очищать файлы каждый день

class ProductionConfig(Config):
    """Конфигурация для production"""
    DEBUG = False

    # Более строгие настройки безопасности
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'must-be-set-in-production'

    # Продакшн настройки
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB в продакшне
    ANALYSIS_TIMEOUT = 600  # 10 минут для сложных анализов

    # Безопасность
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    DEBUG = True

    # Тестовые папки
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'test_uploads')
    PROCESSED_FOLDER = os.path.join(os.getcwd(), 'test_processed')

    # Быстрые настройки для тестов
    ANALYSIS_TIMEOUT = 5  # 5 секунд для тестов
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB для тестовых файлов

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Возвращает конфигурацию на основе переменной окружения"""
    config_name = os.environ.get('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])

# Настройки для анализа расстояний
DISTANCE_ANALYSIS_CONFIG = {
    # Параметры калибровки
    'calibration': {
        'auto_detect_reference': True,
        'reference_objects': ['coin', 'ruler', 'credit_card', 'pen'],
        'reference_sizes': {
            'coin': '2.4cm',  # Стандартная монета
            'ruler': '30cm',  # Стандартная линейка
            'credit_card': '8.5cm',  # Стандартная кредитная карта
            'pen': '14cm'  # Стандартная ручка
        }
    },

    # Алгоритмы анализа
    'algorithms': {
        'edge_detection': 'canny',
        'object_detection': 'contours',
        'distance_calculation': 'euclidean',
        'scale_detection': 'template_matching'
    },

    # Настройки обработки изображений
    'image_processing': {
        'max_resolution': (1920, 1080),  # Максимальное разрешение для обработки
        'blur_kernel_size': 5,
        'canny_low_threshold': 50,
        'canny_high_threshold': 150,
        'contour_min_area': 100
    },

    # Настройки обработки видео
    'video_processing': {
        'fps_limit': 30,  # Максимальный FPS для обработки
        'frame_skip': 1,  # Обрабатывать каждый N-й кадр
        'output_format': 'mp4',
        'codec': 'h264'
    },

    # Выходные форматы
    'output': {
        'formats': ['image', 'video', 'json', 'csv'],
        'default_format': 'image',
        'include_metadata': True,
        'overlay_measurements': True,
        'measurement_color': (0, 255, 0),  # Зеленый цвет для измерений
        'font_scale': 0.7,
        'line_thickness': 2
    }
}

# Настройки API
API_CONFIG = {
    'version': 'v1',
    'rate_limiting': {
        'enabled': True,
        'requests_per_minute': 10,
        'requests_per_hour': 100
    },
    'authentication': {
        'required': False,  # Пока отключено
        'method': 'api_key',  # или 'jwt', 'oauth'
        'token_expiry': timedelta(hours=24)
    },
    'response_format': {
        'include_timestamps': True,
        'include_processing_time': True,
        'include_file_metadata': True
    }
}

# Настройки уведомлений
NOTIFICATION_CONFIG = {
    'enable_progress_notifications': True,
    'notification_types': ['info', 'progress', 'success', 'error'],
    'auto_hide_timeout': {
        'info': 2000,      # 2 секунды
        'progress': 2000,   # 2 секунды
        'success': 3000,    # 3 секунды
        'error': 0          # Не скрывать автоматически
    },
    'max_notifications': 5  # Максимум уведомлений на экране
}