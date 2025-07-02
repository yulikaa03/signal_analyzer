import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Безопасность
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key'
    
    # Загрузка файлов
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'sql', 'db'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # База данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'mysql+mysqlconnector://user:password@localhost/signal_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки сессии
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'