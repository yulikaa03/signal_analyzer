import os
import subprocess
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def import_sql_file(filepath):
    """Импорт SQL файла в MySQL"""
    # В реальном проекте используйте параметры из конфигурации
    command = [
        'mysql',
        '-u', Config.SQLALCHEMY_DATABASE_URI.split('://')[1].split(':')[0],
        '-p' + Config.SQLALCHEMY_DATABASE_URI.split('://')[1].split(':')[1].split('@')[0],
        '-h', Config.SQLALCHEMY_DATABASE_URI.split('@')[1].split('/')[0],
        Config.SQLALCHEMY_DATABASE_URI.split('/')[-1],
        '<', filepath
    ]
    
    try:
        subprocess.run(' '.join(command), shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error importing SQL file: {str(e)}")