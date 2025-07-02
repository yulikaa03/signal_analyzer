from datetime import datetime
from app.extensions import db

class Bus(db.Model):
    """Модель шины данных"""
    __tablename__ = 'buses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    packets = db.relationship('Packet', back_populates='bus', lazy='dynamic')
    
    def __repr__(self):
        return f'<Bus {self.name}>'

class Packet(db.Model):
    """Модель пакета данных"""
    __tablename__ = 'packets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'))
    
    bus = db.relationship('Bus', back_populates='packets')
    data_words = db.relationship('DataWord', back_populates='packet', lazy='dynamic')
    
    def __repr__(self):
        return f'<Packet {self.name}>'

class DataWord(db.Model):
    """Модель слова данных"""
    __tablename__ = 'data_words'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    packet_id = db.Column(db.Integer, db.ForeignKey('packets.id'))
    
    packet = db.relationship('Packet', back_populates='data_words')
    signals = db.relationship('Signal', back_populates='data_word', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataWord {self.name}>'

class Signal(db.Model):
    """Модель сигнала (параметра)"""
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    algorithm = db.Column(db.Text)
    format = db.Column(db.String(1))  # A, C, D
    data_word_id = db.Column(db.Integer, db.ForeignKey('data_words.id'))
    
    data_word = db.relationship('DataWord', back_populates='signals')
    
    def __repr__(self):
        return f'<Signal {self.code}>'
    
    def parse_algorithm(self):
        """Парсинг алгоритма для извлечения параметров"""
        if not self.algorithm:
            return []
            
        # Регулярное выражение для поиска параметров вида X123.45.67
        import re
        return list(set(re.findall(r'[A-Z]\d+\.\d+\.\d+', self.algorithm)))