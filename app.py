import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from models import db, Trade
from datetime import datetime
from PIL import Image  # For image processing
import os
from pathlib import Path 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trade_journal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Image upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

# Create upload folder if it doesn't exist
upload_dir = Path(app.config['UPLOAD_FOLDER'])
upload_dir.mkdir(parents=True, exist_ok=True)


db.init_app(app)

# Helper function to check file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to generate thumbnail
def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    try:
        img = Image.open(image_path)
        img.thumbnail(size)
        img.save(thumbnail_path)
        return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init-db')
def init_db():
    with app.app_context():
        db.create_all()  # Creates all database tables
    return "Database tables created successfully!"

@app.route('/trades')
def trades():
    all_trades = Trade.query.order_by(Trade.entry_date.desc()).all()
    return render_template('trades.html', trades=all_trades)

@app.route('/add_trade', methods=['GET', 'POST'])
def add_trade():
    if request.method == 'POST':
        # Get form data
        symbol = request.form['symbol']
        entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%dT%H:%M')
        entry_price = float(request.form['entry_price'])
        quantity = float(request.form['quantity'])
        position = request.form['position']
        
        # Optional fields
        exit_date_str = request.form.get('exit_date')
        exit_date = datetime.strptime(exit_date_str, '%Y-%m-%dT%H:%M') if exit_date_str else None
        exit_price = float(request.form['exit_price']) if request.form.get('exit_price') else None
        strategy = request.form.get('strategy')
        notes = request.form.get('notes')
        fees = float(request.form['fees']) if request.form.get('fees') else 0.0
        
        # Calculate PnL if exit price is provided
        pnl = None
        if exit_price is not None and entry_price != 0:  # Ensure valid values
           try:
               if position == 'long' and symbol == "XAUUSD":
                  pnl_o = (exit_price - entry_price) * (quantity * 100) - fees
                  pnl="{:.2f}".format(pnl_o)
               else:
                  pnl_o = (entry_price - exit_price) * (quantity * 100) - fees
                  pnl="{:.2f}".format(pnl_o)
           except Exception as e:
                print(f"Error calculating PnL: {e}")
                pnl = None

        pnl = None
        if exit_price is not None and entry_price != 0:  # Ensure valid values
           try:
               if position == 'long':
                  pnl_o = (exit_price - entry_price) * (quantity * 100000) - fees
                  pnl="{:.2f}".format(pnl_o)
               else:
                  pnl_o = (entry_price - exit_price) * (quantity * 100000) - fees
                  pnl="{:.2f}".format(pnl_o)
           except Exception as e:
                print(f"Error calculating PnL: {e}")
                pnl = None
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to make filename unique
                unique_filename = f"{datetime.now().timestamp()}_{filename}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)
                image_path = unique_filename
                
                # Create thumbnail
                thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], f"thumb_{unique_filename}")
                create_thumbnail(save_path, thumbnail_path)
        
        # Create new trade
        new_trade = Trade(
            symbol=symbol,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            position=position,
            strategy=strategy,
            notes=notes,
            pnl=pnl,
            fees=fees,
            image_path=image_path
        )
        
        db.session.add(new_trade)
        db.session.commit()
        
        return redirect(url_for('trades'))
    
    return render_template('add_trade.html')

@app.route('/trade/<int:trade_id>')
def trade_detail(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    return render_template('trade_detail.html', trade=trade)


# Edit Trade Route
@app.route('/edit_trade/<int:trade_id>', methods=['GET', 'POST'])
def edit_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    
    if request.method == 'POST':
        # Update trade with form data
        trade.symbol = request.form['symbol']
        trade.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%dT%H:%M')
        trade.entry_price = float(request.form['entry_price'])
        trade.quantity = float(request.form['quantity'])
        trade.position = request.form['position']
        
        # Handle optional fields
        exit_date_str = request.form.get('exit_date')
        trade.exit_date = datetime.strptime(exit_date_str, '%Y-%m-%dT%H:%M') if exit_date_str else None
        trade.exit_price = float(request.form['exit_price']) if request.form.get('exit_price') else None
        trade.strategy = request.form.get('strategy')
        trade.notes = request.form.get('notes')
        trade.fees = float(request.form['fees']) if request.form.get('fees') else 0.0
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # Delete old image if exists
                if trade.image_path:
                    old_image = os.path.join(app.config['UPLOAD_FOLDER'], trade.image_path)
                    if os.path.exists(old_image):
                        os.remove(old_image)
                
                # Save new image
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().timestamp()}_{filename}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(save_path)
                trade.image_path = unique_filename
        
        # Recalculate PnL
        if trade.exit_price:
            if trade.position == 'long':
                trade.pnl = (trade.exit_price - trade.entry_price) * trade.quantity - trade.fees
            else:
                trade.pnl = (trade.entry_price - trade.exit_price) * trade.quantity - trade.fees
        else:
            trade.pnl = None
        
        db.session.commit()
        return redirect(url_for('trade_detail', trade_id=trade.id))
    
    # Convert datetime to HTML5 datetime-local format
    entry_date = trade.entry_date.strftime('%Y-%m-%dT%H:%M')
    exit_date = trade.exit_date.strftime('%Y-%m-%dT%H:%M') if trade.exit_date else ''
    
    return render_template('edit_trade.html', trade=trade, entry_date=entry_date, exit_date=exit_date)

# Delete Trade Route
@app.route('/delete_trade/<int:trade_id>', methods=['POST'])
def delete_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    
    # Delete associated image if exists
    if trade.image_path:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], trade.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(trade)
    db.session.commit()
    return redirect(url_for('trades'))


@app.route('/test_pnl')
def test_pnl():
    test_cases = [
        {'position': 'long', 'entry': 100, 'exit': 110, 'qty': 10, 'fees': 5, 'expected': 5},  # ((110-100)/100)*1000 -5 = 5
        {'position': 'short', 'entry': 100, 'exit': 90, 'qty': 10, 'fees': 5, 'expected': 5},
        {'position': 'long', 'entry': 100, 'exit': 90, 'qty': 10, 'fees': 5, 'expected': -15},
    ]
    
    results = []
    for case in test_cases:
        if case['position'] == 'long':
            calc = ((case['exit'] - case['entry']) / case['entry']) * (case['qty'] * 100) - case['fees']
        else:
            calc = ((case['entry'] - case['exit']) / case['entry']) * (case['qty'] * 100) - case['fees']
        
        results.append({
            'case': case,
            'calculated': calc,
            'passed': abs(calc - case['expected']) < 0.0001
        })
    
    return render_template('test_pnl.html', results=results)




if __name__ == '__main__':
    app.run(debug=True)