from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from werkzeug.utils import secure_filename
from app.init import app, db
from app.models import Bus, Packet, DataWord, Signal
from app.utils import allowed_file, import_sql_file
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Проверка наличия файла в запросе
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        
        # Если пользователь не выбрал файл
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Импорт SQL файла в базу данных
                import_sql_file(filepath)
                flash('Database imported successfully')
                return redirect(url_for('signals'))
            except Exception as e:
                flash(f'Error importing database: {str(e)}')
                return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/signals')
def signals():
    # Фильтрация сигналов
    bus_id = request.args.get('bus_id')
    packet_id = request.args.get('packet_id')
    data_word_id = request.args.get('data_word_id')
    
    query = Signal.query
    
    if data_word_id:
        query = query.filter_by(data_word_id=data_word_id)
    elif packet_id:
        query = query.join(DataWord).filter(DataWord.packet_id == packet_id)
    elif bus_id:
        query = query.join(DataWord).join(Packet).filter(Packet.bus_id == bus_id)
    
    signals = query.order_by(Signal.code).all()
    
    # Получаем данные для фильтров
    buses = Bus.query.order_by(Bus.name).all()
    packets = Packet.query.order_by(Packet.name).all()
    data_words = DataWord.query.order_by(DataWord.name).all()
    
    return render_template('signals/list.html',
                         signals=signals,
                         buses=buses,
                         packets=packets,
                         data_words=data_words)

@app.route('/signal/<int:signal_id>')
def signal_detail(signal_id):
    signal = Signal.query.get_or_404(signal_id)
    related_params = []
    
    if signal.algorithm:
        param_codes = signal.parse_algorithm()
        related_params = Signal.query.filter(Signal.code.in_(param_codes)).all()
    
    return render_template('signals/detail.html',
                         signal=signal,
                         related_params=related_params)

@app.route('/api/signal/<signal_code>')
def get_signal_info(signal_code):
    signal = Signal.query.filter_by(code=signal_code).first_or_404()
    
    return jsonify({
        'code': signal.code,
        'algorithm': signal.algorithm,
        'format': signal.format,
        'data_word': signal.data_word.name if signal.data_word else None,
        'packet': signal.data_word.packet.name if signal.data_word else None,
        'bus': signal.data_word.packet.bus.name if signal.data_word and signal.data_word.packet else None
    })

@app.route('/related/<model_name>')
def related_models(model_name):
    models_map = {
        'buses': Bus,
        'packets': Packet,
        'datawords': DataWord
    }
    
    if model_name not in models_map:
        abort(404)
        
    Model = models_map[model_name]
    items = Model.query.order_by(Model.name).all()
    
    return render_template(f'related/{model_name}.html',
                         items=items,
                         model_name=model_name)
from flask import render_template_string

@app.context_processor
def utility_processor():
    def highlight_algorithm(algorithm):
        if not algorithm:
            return ""
        
        import re
        params = re.findall(r'([A-Z]\d+\.\d+\.\d+)', algorithm)
        highlighted = algorithm
        
        for param in set(params):
            highlighted = highlighted.replace(
                param,
                f'<span class="algorithm-param" data-param="{param}">{param}</span>'
            )
        
        return highlighted
    
    return dict(highlight_algorithm=highlight_algorithm)

@app.template_filter('tojson')
def tojson_filter(obj):
    import json
    return json.dumps(obj)