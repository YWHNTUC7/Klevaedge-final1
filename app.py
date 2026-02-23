from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import os
from functools import wraps
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'klevaedge-k3y-2025-xZ9qP2mN8rL4wT7v')

# Upload configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/klevaedge_uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database setup
def init_db_tables():
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/crypto_broker.db'))
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  balance REAL DEFAULT 0,
                  profit REAL DEFAULT 0,
                  total_deposit REAL DEFAULT 0,
                  total_withdrawal REAL DEFAULT 0,
                  is_verified INTEGER DEFAULT 0,
                  verification_code TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  type TEXT NOT NULL,
                  amount REAL NOT NULL,
                  crypto TEXT,
                  status TEXT DEFAULT 'Pending',
                  wallet_address TEXT,
                  proof_file TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    # Add proof_file column if it doesn't exist (for existing DBs)
    try:
        c.execute('ALTER TABLE transactions ADD COLUMN proof_file TEXT')
    except:
        pass
    
    # Copy Trading table
    c.execute('''CREATE TABLE IF NOT EXISTS copy_trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  trader_name TEXT NOT NULL,
                  amount REAL NOT NULL,
                  profit_share REAL DEFAULT 10,
                  status TEXT DEFAULT 'Active',
                  total_profit REAL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Trading Activity Log
    c.execute('''CREATE TABLE IF NOT EXISTS trading_activity
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  activity_type TEXT,
                  description TEXT,
                  amount REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Trades table (buy/sell)
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  symbol TEXT NOT NULL,
                  trade_type TEXT NOT NULL,
                  amount REAL NOT NULL,
                  duration TEXT,
                  stop_loss REAL,
                  take_profit REAL,
                  status TEXT DEFAULT 'Open',
                  profit_loss REAL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Stakes table
    c.execute('''CREATE TABLE IF NOT EXISTS stakes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  asset TEXT NOT NULL,
                  amount REAL NOT NULL,
                  daily_rate REAL DEFAULT 0.5,
                  status TEXT DEFAULT 'Active',
                  earnings REAL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Subscriptions table
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  plan TEXT NOT NULL,
                  amount REAL NOT NULL,
                  roi_percent REAL DEFAULT 0,
                  duration_days INTEGER DEFAULT 14,
                  status TEXT DEFAULT 'Active',
                  earnings REAL DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Copy Traders table (admin managed)
    c.execute('''CREATE TABLE IF NOT EXISTS traders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  country TEXT,
                  photo TEXT,
                  roi REAL DEFAULT 0,
                  win_rate REAL DEFAULT 0,
                  wins INTEGER DEFAULT 0,
                  losses INTEGER DEFAULT 0,
                  copiers INTEGER DEFAULT 0,
                  profit_share REAL DEFAULT 10,
                  is_active INTEGER DEFAULT 1,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Signals table
    c.execute('''CREATE TABLE IF NOT EXISTS signal_purchases
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  signal_name TEXT NOT NULL,
                  amount REAL NOT NULL,
                  status TEXT DEFAULT 'Active',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')

    conn.commit()
    conn.close()

def init_db():
    init_db_tables()

def seed_traders():
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM traders').fetchone()[0]
    if count == 0:
        traders = [
            ('Vivek Sharma', 'India', 'https://randomuser.me/api/portraits/men/32.jpg', 287.5, 74.2, 312, 109, 1200, 10),
            ('Edo Martinez', 'Spain', 'https://randomuser.me/api/portraits/men/44.jpg', 145.8, 68.4, 198, 91, 387, 10),
            ('W D Gann', 'USA', 'https://randomuser.me/api/portraits/men/77.jpg', 199.8, 71.0, 89, 36, 50, 25),
            ('Echo X', 'Singapore', 'https://randomuser.me/api/portraits/men/22.jpg', 212.4, 65.8, 445, 231, 920, 10),
            ('Coach JV', 'UK', 'https://randomuser.me/api/portraits/men/55.jpg', 176.1, 72.5, 261, 99, 620, 10),
            ('Sarah Chen', 'China', 'https://randomuser.me/api/portraits/women/44.jpg', 134.2, 66.1, 187, 96, 510, 10),
            ('Marcus Webb', 'Australia', 'https://randomuser.me/api/portraits/men/68.jpg', 98.7, 59.3, 142, 97, 230, 15),
            ('Yuki Tanaka', 'Japan', 'https://randomuser.me/api/portraits/men/9.jpg', 221.0, 73.4, 389, 141, 870, 20),
            ('Aisha Okafor', 'Nigeria', 'https://randomuser.me/api/portraits/women/68.jpg', 163.5, 67.8, 203, 96, 480, 10),
            ('Viktor Petrov', 'Russia', 'https://randomuser.me/api/portraits/men/15.jpg', 157.9, 69.2, 278, 124, 740, 10),
            ('Liam OBrien', 'Ireland', 'https://randomuser.me/api/portraits/men/38.jpg', 129.3, 61.8, 156, 97, 310, 12),
            ('Priya Nair', 'India', 'https://randomuser.me/api/portraits/women/25.jpg', 189.6, 70.4, 298, 125, 590, 10),
            ('Carlos Reyes', 'Mexico', 'https://randomuser.me/api/portraits/men/82.jpg', 111.4, 63.7, 221, 126, 430, 10),
            ('Nadia Blanc', 'France', 'https://randomuser.me/api/portraits/women/12.jpg', 147.8, 66.9, 189, 93, 360, 15),
            ('James Osei', 'Ghana', 'https://randomuser.me/api/portraits/men/91.jpg', 178.2, 71.6, 302, 120, 680, 10),
        ]
        for t in traders:
            db.execute('INSERT INTO traders (name, country, photo, roi, win_rate, wins, losses, copiers, profit_share) VALUES (?,?,?,?,?,?,?,?,?)', t)
        db.commit()
    db.close()

def migrate_db():
    """Add any missing tables to existing database - safe to run every startup."""
    # Use direct connection to avoid dependency on get_db() which may not be defined yet
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/crypto_broker.db'))
    conn.row_factory = sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS wallet_addresses (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  coin_id TEXT UNIQUE NOT NULL,
                  coin_name TEXT NOT NULL,
                  symbol TEXT NOT NULL,
                  icon TEXT NOT NULL,
                  address TEXT NOT NULL,
                  is_active INTEGER DEFAULT 1
                )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS contact_info (
                  id INTEGER PRIMARY KEY,
                  email TEXT DEFAULT 'support@klevaedge.com',
                  whatsapp TEXT DEFAULT '+1234567890',
                  whatsapp_link TEXT DEFAULT 'https://wa.me/1234567890',
                  telegram TEXT DEFAULT '@klevaedgesupport',
                  telegram_link TEXT DEFAULT 'https://t.me/klevaedgesupport'
                )''')
    if not conn.execute('SELECT COUNT(*) FROM contact_info').fetchone()[0]:
        conn.execute("INSERT INTO contact_info (id,email,whatsapp,whatsapp_link,telegram,telegram_link) VALUES (1,'support@klevaedge.com','+1 (234) 567-890','https://wa.me/1234567890','@klevaedgesupport','https://t.me/klevaedgesupport')")
    if not conn.execute('SELECT COUNT(*) FROM wallet_addresses').fetchone()[0]:
        wallets = [
            ('bitcoin','Bitcoin','BTC','₿','bc1qwvam7n34ca68l0ukgm2za63pxprhw7gx2jh477',1),
            ('ethereum','Ethereum','ETH','Ξ','0x7Bc2EbbEbeB692091c201ed6f9E75720B4Dd965d',1),
            ('usdt','USDT TRC20','USDT','₮','THtq4hFQbdBCD6zZTMu2aj8WnWMaUDjYfR',1),
            ('litecoin','Litecoin','LTC','Ł','ltc1qs3glhf2ymryfpce8sxk32lj7u9xu7zuv0dayxv',1),
        ]
        conn.executemany('INSERT OR IGNORE INTO wallet_addresses (coin_id,coin_name,symbol,icon,address,is_active) VALUES (?,?,?,?,?,?)', wallets)
    conn.commit()
    conn.close()

migrate_db()  # run after definition

def get_wallets():
    try:
        db = get_db()
        rows = db.execute('SELECT * FROM wallet_addresses WHERE is_active=1 ORDER BY id').fetchall()
        db.close()
        return [dict(r) for r in rows]
    except:
        migrate_db()
        db = get_db()
        rows = db.execute('SELECT * FROM wallet_addresses WHERE is_active=1 ORDER BY id').fetchall()
        db.close()
        return [dict(r) for r in rows]

def get_contact():
    try:
        db = get_db()
        row = db.execute('SELECT * FROM contact_info WHERE id=1').fetchone()
        db.close()
        return dict(row) if row else {}
    except:
        migrate_db()
        db = get_db()
        row = db.execute('SELECT * FROM contact_info WHERE id=1').fetchone()
        db.close()
        return dict(row) if row else {}

# Admin credentials (change these!)
ADMIN_EMAIL = 'admin@cryptobroker.com'
ADMIN_PASSWORD = hashlib.sha256('admin123'.encode()).hexdigest()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/crypto_broker.db'))
    conn.row_factory = sqlite3.Row
    return conn

init_db()
seed_traders()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Crypto price API
@app.route('/api/crypto-prices')
def get_crypto_prices():
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={
                'ids': 'bitcoin,ethereum,tether,litecoin,solana,ripple,dogecoin,cardano',
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'bitcoin': {
                    'price': data['bitcoin']['usd'],
                    'change': data['bitcoin']['usd_24h_change']
                },
                'ethereum': {
                    'price': data['ethereum']['usd'],
                    'change': data['ethereum']['usd_24h_change']
                },
                'tether': {
                    'price': data['tether']['usd'],
                    'change': data['tether']['usd_24h_change']
                },
                'litecoin': {
                    'price': data['litecoin']['usd'],
                    'change': data['litecoin']['usd_24h_change']
                },
                'solana': {
                    'price': data['solana']['usd'],
                    'change': data['solana']['usd_24h_change']
                },
                'ripple': {
                    'price': data['ripple']['usd'],
                    'change': data['ripple']['usd_24h_change']
                },
                'dogecoin': {
                    'price': data['dogecoin']['usd'],
                    'change': data['dogecoin']['usd_24h_change']
                },
                'cardano': {
                    'price': data['cardano']['usd'],
                    'change': data['cardano']['usd_24h_change']
                }
            })
        else:
            return jsonify({'error': 'Failed to fetch prices'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Notifications API
@app.route('/api/notifications')
@login_required
def get_notifications():
    db = get_db()
    activities = db.execute(
        'SELECT * FROM trading_activity WHERE user_id = ? ORDER BY created_at DESC LIMIT 20',
        (session['user_id'],)
    ).fetchall()
    db.close()
    notifs = []
    icons = {
        'Trade Opened': 'fa-chart-bar',
        'Trade Closed': 'fa-check-circle',
        'Copy Trade Started': 'fa-copy',
        'Copy Trade Stopped': 'fa-stop-circle',
        'Staking Started': 'fa-coins',
        'Plan Subscribed': 'fa-server',
        'Signal Purchased': 'fa-broadcast-tower',
        'Deposit': 'fa-arrow-down',
        'Withdrawal': 'fa-arrow-up',
    }
    colors = {
        'Trade Opened': 'blue',
        'Trade Closed': 'green',
        'Copy Trade Started': 'purple',
        'Copy Trade Stopped': 'gray',
        'Staking Started': 'yellow',
        'Plan Subscribed': 'indigo',
        'Signal Purchased': 'cyan',
        'Deposit': 'green',
        'Withdrawal': 'orange',
    }
    for a in activities:
        notifs.append({
            'id': a['id'],
            'type': a['activity_type'],
            'description': a['description'],
            'amount': a['amount'],
            'created_at': a['created_at'][:16],
            'icon': icons.get(a['activity_type'], 'fa-bell'),
            'color': colors.get(a['activity_type'], 'blue')
        })
    return jsonify(notifs)

# Admin notifications API
@app.route('/api/admin/notifications')
@admin_required
def get_admin_notifications():
    db = get_db()
    notifs = []

    # Pending deposits
    pending_deposits = db.execute(
        "SELECT t.*, u.name FROM transactions t JOIN users u ON t.user_id = u.id "
        "WHERE t.type = 'Deposit' AND t.status = 'Pending' ORDER BY t.created_at DESC LIMIT 10"
    ).fetchall()
    for d in pending_deposits:
        notifs.append({
            'id': f"dep_{d['id']}",
            'type': 'Pending Deposit',
            'description': f"{d['name']} deposited ${d['amount']:.2f} via {(d['crypto'] or '').upper()} — awaiting approval",
            'amount': d['amount'],
            'created_at': (d['created_at'] or '')[:16],
            'icon': 'fa-arrow-down',
            'color': 'yellow',
        })

    # Pending withdrawals
    pending_withdrawals = db.execute(
        "SELECT t.*, u.name FROM transactions t JOIN users u ON t.user_id = u.id "
        "WHERE t.type = 'Withdrawal' AND t.status = 'Pending' ORDER BY t.created_at DESC LIMIT 10"
    ).fetchall()
    for w in pending_withdrawals:
        notifs.append({
            'id': f"wd_{w['id']}",
            'type': 'Withdrawal Request',
            'description': f"{w['name']} requested a withdrawal of ${w['amount']:.2f}",
            'amount': w['amount'],
            'created_at': (w['created_at'] or '')[:16],
            'icon': 'fa-arrow-up',
            'color': 'orange',
        })

    # New users (last 7 days)
    new_users = db.execute(
        "SELECT * FROM users WHERE created_at >= datetime('now', '-7 days') "
        "ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    for u in new_users:
        notifs.append({
            'id': f"usr_{u['id']}",
            'type': 'New User',
            'description': f"{u['name']} just created an account",
            'amount': 0,
            'created_at': (u['created_at'] or '')[:16],
            'icon': 'fa-user-plus',
            'color': 'green',
        })

    db.close()
    notifs.sort(key=lambda x: x['created_at'], reverse=True)
    return jsonify(notifs[:20])

# Admin Wallet Management
@app.route('/admin/wallets')
@admin_required
def admin_wallets():
    migrate_db()  # ensure tables exist on every call
    db = get_db()
    wallets = db.execute('SELECT * FROM wallet_addresses ORDER BY id').fetchall()
    contact = db.execute('SELECT * FROM contact_info WHERE id=1').fetchone()
    db.close()
    return render_template('admin/wallets.html', wallets=wallets, contact=contact)

@app.route('/admin/wallets/add', methods=['POST'])
@admin_required
def admin_add_wallet():
    coin_id = request.form.get('coin_id','').strip().lower().replace(' ','_')
    coin_name = request.form.get('coin_name','').strip()
    symbol = request.form.get('symbol','').strip().upper()
    icon = request.form.get('icon','₿').strip()
    address = request.form.get('address','').strip()
    if coin_id and coin_name and address:
        db = get_db()
        try:
            db.execute('INSERT INTO wallet_addresses (coin_id,coin_name,symbol,icon,address) VALUES (?,?,?,?,?)',
                      (coin_id, coin_name, symbol, icon, address))
            db.commit()
            flash(f'{coin_name} wallet added!', 'success')
        except:
            flash('Coin ID already exists. Use a unique ID.', 'error')
        db.close()
    return redirect(url_for('admin_wallets'))

@app.route('/admin/wallets/edit/<int:wallet_id>', methods=['POST'])
@admin_required
def admin_edit_wallet(wallet_id):
    db = get_db()
    db.execute('UPDATE wallet_addresses SET coin_name=?, symbol=?, icon=?, address=?, is_active=? WHERE id=?',
              (request.form.get('coin_name'), request.form.get('symbol','').upper(),
               request.form.get('icon','₿'), request.form.get('address'),
               int(request.form.get('is_active', 1)), wallet_id))
    db.commit()
    db.close()
    flash('Wallet updated!', 'success')
    return redirect(url_for('admin_wallets'))

@app.route('/admin/wallets/delete/<int:wallet_id>', methods=['POST'])
@admin_required
def admin_delete_wallet(wallet_id):
    db = get_db()
    db.execute('DELETE FROM wallet_addresses WHERE id=?', (wallet_id,))
    db.commit()
    db.close()
    flash('Wallet removed.', 'success')
    return redirect(url_for('admin_wallets'))

@app.route('/admin/contact/update', methods=['POST'])
@admin_required
def admin_update_contact():
    email = request.form.get('email','').strip()
    whatsapp = request.form.get('whatsapp','').strip()
    whatsapp_link = request.form.get('whatsapp_link','').strip()
    telegram = request.form.get('telegram','').strip()
    telegram_link = request.form.get('telegram_link','').strip()
    db = get_db()
    db.execute('UPDATE contact_info SET email=?, whatsapp=?, whatsapp_link=?, telegram=?, telegram_link=? WHERE id=1',
              (email, whatsapp, whatsapp_link, telegram, telegram_link))
    db.commit()
    db.close()
    flash('Contact info updated!', 'success')
    return redirect(url_for('admin_wallets'))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/support')
def support():
    contact = get_contact()
    return render_template('support.html', contact=contact)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    contact = get_contact()
    return render_template('contact.html', contact=contact)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if admin
        if email == ADMIN_EMAIL and hash_password(password) == ADMIN_PASSWORD:
            session['is_admin'] = True
            session['user_email'] = email
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # Check regular user
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        # Generate verification code
        verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        db = get_db()
        try:
            # Auto-verify users (skip email verification for now)
            db.execute('INSERT INTO users (name, email, password, is_verified, verification_code) VALUES (?, ?, ?, ?, ?)',
                      (name, email, hash_password(password), 1, verification_code))
            db.commit()
            
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    # Skip email verification for now
    flash('Email verification is temporarily disabled. You can login directly.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    # Get recent transactions
    transactions = db.execute(
        'SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (session['user_id'],)
    ).fetchall()
    
    # Get copy trades
    copy_trades = db.execute(
        'SELECT * FROM copy_trades WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    
    # Get recent activity
    activities = db.execute(
        'SELECT * FROM trading_activity WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
        (session['user_id'],)
    ).fetchall()
    
    db.close()
    return render_template('dashboard.html', user=user, transactions=transactions, 
                         copy_trades=copy_trades, activities=activities)

@app.route('/copy-trading')
@login_required
def copy_trading():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    copy_trades = db.execute(
        'SELECT * FROM copy_trades WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    db.close()
    
    # Top traders (sample data)
    top_traders = [
        {'name': 'Vivek Sharma', 'roi': 287.5, 'copiers': 1200, 'win_rate': 97.0, 'wins': 18003, 'losses': 556, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/32.jpg', 'country': 'India'},
        {'name': 'Edo Martinez', 'roi': 245.8, 'copiers': 987, 'win_rate': 94.7, 'wins': 1892, 'losses': 120, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/44.jpg', 'country': 'Spain'},
        {'name': 'W D Gann', 'roi': 399.8, 'copiers': 50, 'win_rate': 99.8, 'wins': 103, 'losses': 1, 'profit_share': 25, 'photo': 'https://randomuser.me/api/portraits/men/77.jpg', 'country': 'USA'},
        {'name': 'Echo X', 'roi': 312.4, 'copiers': 2500, 'win_rate': 95.6, 'wins': 50218, 'losses': 180, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/22.jpg', 'country': 'Singapore'},
        {'name': 'Coach JV', 'roi': 276.1, 'copiers': 820, 'win_rate': 98.3, 'wins': 8201, 'losses': 46, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/55.jpg', 'country': 'UK'},
        {'name': 'Sarah Chen', 'roi': 334.2, 'copiers': 1650, 'win_rate': 96.2, 'wins': 22450, 'losses': 890, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/women/44.jpg', 'country': 'China'},
        {'name': 'Marcus Webb', 'roi': 198.7, 'copiers': 430, 'win_rate': 92.1, 'wins': 4320, 'losses': 370, 'profit_share': 15, 'photo': 'https://randomuser.me/api/portraits/men/68.jpg', 'country': 'Australia'},
        {'name': 'Yuki Tanaka', 'roi': 421.0, 'copiers': 3100, 'win_rate': 97.8, 'wins': 61003, 'losses': 210, 'profit_share': 20, 'photo': 'https://randomuser.me/api/portraits/men/9.jpg', 'country': 'Japan'},
        {'name': 'Aisha Okafor', 'roi': 263.5, 'copiers': 780, 'win_rate': 93.4, 'wins': 7812, 'losses': 556, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/women/68.jpg', 'country': 'Nigeria'},
        {'name': 'Viktor Petrov', 'roi': 357.9, 'copiers': 2200, 'win_rate': 96.9, 'wins': 38901, 'losses': 124, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/15.jpg', 'country': 'Russia'},
        {'name': 'Liam O\'Brien', 'roi': 229.3, 'copiers': 560, 'win_rate': 91.8, 'wins': 5640, 'losses': 503, 'profit_share': 12, 'photo': 'https://randomuser.me/api/portraits/men/38.jpg', 'country': 'Ireland'},
        {'name': 'Priya Nair', 'roi': 289.6, 'copiers': 1400, 'win_rate': 95.1, 'wins': 19230, 'losses': 990, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/women/25.jpg', 'country': 'India'},
        {'name': 'Carlos Reyes', 'roi': 311.4, 'copiers': 1900, 'win_rate': 94.3, 'wins': 28400, 'losses': 1710, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/82.jpg', 'country': 'Mexico'},
        {'name': 'Nadia Blanc', 'roi': 247.8, 'copiers': 670, 'win_rate': 93.7, 'wins': 8930, 'losses': 600, 'profit_share': 15, 'photo': 'https://randomuser.me/api/portraits/women/12.jpg', 'country': 'France'},
        {'name': 'James Osei', 'roi': 378.2, 'copiers': 2800, 'win_rate': 98.1, 'wins': 44300, 'losses': 105, 'profit_share': 10, 'photo': 'https://randomuser.me/api/portraits/men/91.jpg', 'country': 'Ghana'},
    ]
    
    return render_template('copy_trading.html', user=user, top_traders=top_traders, 
                         copy_trades=copy_trades)

@app.route('/start-copy-trade', methods=['POST'])
@login_required
def start_copy_trade():
    trader_name = request.form.get('trader_name')
    amount = float(request.form.get('amount'))
    
    db = get_db()
    user = db.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if amount > user['balance']:
        flash('Insufficient balance!', 'error')
    else:
        db.execute(
            'INSERT INTO copy_trades (user_id, trader_name, amount) VALUES (?, ?, ?)',
            (session['user_id'], trader_name, amount)
        )
        db.execute(
            'UPDATE users SET balance = balance - ? WHERE id = ?',
            (amount, session['user_id'])
        )
        db.execute(
            'INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?, ?, ?, ?)',
            (session['user_id'], 'Copy Trade Started', f'Started copying {trader_name}', amount)
        )
        db.commit()
        flash(f'Successfully started copying {trader_name} with ${amount}!', 'success')
    
    db.close()
    return redirect(url_for('copy_trading'))

@app.route('/stop-copy-trade/<int:trade_id>', methods=['POST'])
@login_required
def stop_copy_trade(trade_id):
    db = get_db()
    trade = db.execute('SELECT * FROM copy_trades WHERE id = ? AND user_id = ?', 
                      (trade_id, session['user_id'])).fetchone()
    
    if trade:
        # Return investment plus profit
        total_return = trade['amount'] + trade['total_profit']
        db.execute('UPDATE users SET balance = balance + ? WHERE id = ?', 
                  (total_return, session['user_id']))
        db.execute('UPDATE copy_trades SET status = ? WHERE id = ?', ('Stopped', trade_id))
        db.execute(
            'INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?, ?, ?, ?)',
            (session['user_id'], 'Copy Trade Stopped', f'Stopped copying {trade["trader_name"]}', total_return)
        )
        db.commit()
        flash(f'Copy trade stopped. ${total_return:.2f} returned to your balance.', 'success')
    
    db.close()
    return redirect(url_for('copy_trading'))

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = request.form.get('amount')
        crypto = request.form.get('crypto')
        proof_filename = None

        # Handle file upload
        if 'payment_proof' in request.files:
            file = request.files['payment_proof']
            if file and file.filename and allowed_file(file.filename):
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower()
                proof_filename = f"proof_{session['user_id']}_{uuid.uuid4().hex[:8]}.{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], proof_filename))

        db = get_db()
        db.execute('INSERT INTO transactions (user_id, type, amount, crypto, status, proof_file) VALUES (?, ?, ?, ?, ?, ?)',
            (session['user_id'], 'Deposit', float(amount) if amount else 0, crypto, 'Pending', proof_filename))
        db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
            (session['user_id'], 'Deposit', f'Deposit of ${amount} via {crypto.upper() if crypto else ""} submitted — awaiting confirmation.', float(amount) if amount else 0))
        db.commit()
        db.close()
        flash(f'Deposit of ${amount} submitted! Our team will confirm your payment shortly.', 'success')
    db = get_db()
    deposits = db.execute("SELECT * FROM transactions WHERE user_id = ? AND type = 'Deposit' ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    db.close()
    wallets = get_wallets()
    wallets_dict = {w['coin_id']: w['address'] for w in wallets}
    return render_template('deposit.html', wallets=wallets_dict, wallet_list=wallets, deposits=deposits)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not session.get('user_id') and not session.get('is_admin'):
        return redirect(url_for('login'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        crypto = request.form.get('crypto')
        wallet_address = request.form.get('wallet_address')
        
        if amount > user['balance']:
            flash('Insufficient balance!', 'error')
        else:
            db.execute('INSERT INTO transactions (user_id, type, amount, crypto, wallet_address, status) VALUES (?, ?, ?, ?, ?, ?)',
                (session['user_id'], 'Withdrawal', amount, crypto, wallet_address, 'Pending'))
            db.commit()
            flash(f'Withdrawal request for ${amount} submitted!', 'success')
    withdrawals = db.execute("SELECT * FROM transactions WHERE user_id = ? AND type = 'Withdrawal' ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    db.close()
    wallets = get_wallets()
    wallets_dict = {w['coin_id']: w['address'] for w in wallets}
    return render_template('withdraw.html', user=user, wallets=wallets_dict, wallet_list=wallets, withdrawals=withdrawals)

@app.route('/transactions')
@login_required
def transactions():
    db = get_db()
    transactions = db.execute(
        'SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    ).fetchall()
    db.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Admin routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    db = get_db()
    
    if request.method == 'POST':
        balance = request.form.get('balance')
        profit = request.form.get('profit')
        total_deposit = request.form.get('total_deposit')
        total_withdrawal = request.form.get('total_withdrawal')
        
        db.execute(
            'UPDATE users SET balance = ?, profit = ?, total_deposit = ?, total_withdrawal = ? WHERE id = ?',
            (balance, profit, total_deposit, total_withdrawal, user_id)
        )
        db.commit()
        flash('User data updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    transactions = db.execute(
        'SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    db.close()
    
    return render_template('admin/edit_user.html', user=user, transactions=transactions)

@app.route('/admin/transaction/<int:transaction_id>/approve', methods=['POST'])
@admin_required
def admin_approve_transaction(transaction_id):
    db = get_db()
    transaction = db.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,)).fetchone()

    if transaction:
        db.execute('UPDATE transactions SET status = ? WHERE id = ?', ('Completed', transaction_id))

        # Update user balance for deposits + send notification
        if transaction['type'] == 'Deposit':
            db.execute(
                'UPDATE users SET balance = balance + ?, total_deposit = total_deposit + ? WHERE id = ?',
                (transaction['amount'], transaction['amount'], transaction['user_id'])
            )
            db.execute(
                'INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (transaction['user_id'], 'Deposit',
                 f'Your deposit of ${transaction["amount"]:.2f} via {(transaction["crypto"] or "").upper()} has been confirmed and credited to your account! 🎉',
                 transaction['amount'])
            )

        # Update user balance for withdrawals + send notification
        elif transaction['type'] == 'Withdrawal':
            db.execute(
                'UPDATE users SET balance = balance - ?, total_withdrawal = total_withdrawal + ? WHERE id = ?',
                (transaction['amount'], transaction['amount'], transaction['user_id'])
            )
            db.execute(
                'INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (transaction['user_id'], 'Withdrawal',
                 f'Your withdrawal of ${transaction["amount"]:.2f} has been approved and is being processed.',
                 transaction['amount'])
            )

        db.commit()
        flash(f'Transaction approved! User balance updated and notification sent.', 'success')

    db.close()
    return redirect(url_for('admin_edit_user', user_id=transaction['user_id']))


# ============================================================
# NEW ROUTES - Added from reference app screenshots
# ============================================================

@app.route('/assets')
@login_required
def assets():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    transactions = db.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5', (session['user_id'],)).fetchall()
    db.close()
    return render_template('assets.html', user=user, transactions=transactions)

@app.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        symbol = request.form.get('symbol', 'BTC')
        trade_type = request.form.get('trade_type', 'Buy')
        amount = float(request.form.get('amount', 0))
        duration = request.form.get('duration', '1h')
        stop_loss = request.form.get('stop_loss') or None
        take_profit = request.form.get('take_profit') or None
        if amount <= 0:
            flash('Please enter a valid amount.', 'error')
        elif amount > user['balance']:
            flash('Insufficient balance!', 'error')
        else:
            db.execute('INSERT INTO trades (user_id, symbol, trade_type, amount, duration, stop_loss, take_profit) VALUES (?,?,?,?,?,?,?)',
                (session['user_id'], symbol, trade_type, amount, duration, stop_loss, take_profit))
            db.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, session['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (session['user_id'], 'Trade Opened', f'{trade_type} {symbol} for ${amount:.2f}', amount))
            db.commit()
            flash(f'{trade_type} order placed for {symbol} — ${amount:.2f}!', 'success')
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    open_trades = db.execute("SELECT * FROM trades WHERE user_id = ? AND status = 'Open' ORDER BY created_at DESC", (session['user_id'],)).fetchall()
    closed_trades = db.execute("SELECT * FROM trades WHERE user_id = ? AND status != 'Open' ORDER BY created_at DESC LIMIT 20", (session['user_id'],)).fetchall()
    db.close()
    return render_template('trade.html', user=user, open_trades=open_trades, closed_trades=closed_trades)

@app.route('/trade/close/<int:trade_id>', methods=['POST'])
@login_required
def close_trade(trade_id):
    db = get_db()
    trade = db.execute('SELECT * FROM trades WHERE id = ? AND user_id = ?', (trade_id, session['user_id'])).fetchone()
    if trade:
        import random
        pnl = round(trade['amount'] * random.uniform(-0.08, 0.18), 2)
        returned = trade['amount'] + pnl
        db.execute('UPDATE trades SET status = ?, profit_loss = ? WHERE id = ?', ('Closed', pnl, trade_id))
        db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (returned, max(pnl,0), session['user_id']))
        db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
            (session['user_id'], 'Trade Closed', f'Closed {trade["trade_type"]} {trade["symbol"]} P&L: ${pnl:.2f}', returned))
        db.commit()
        flash(f'Trade closed. P&L: ${pnl:+.2f} returned to balance.', 'success')
    db.close()
    return redirect(url_for('trade'))

@app.route('/markets')
@login_required
def markets():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('markets.html', user=user)

@app.route('/stake', methods=['GET', 'POST'])
@login_required
def stake():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        asset = request.form.get('asset')
        amount = float(request.form.get('amount', 0))
        daily_rate = float(request.form.get('daily_rate', 0.5))
        if amount <= 0:
            flash('Invalid amount.', 'error')
        elif amount > user['balance']:
            flash('Insufficient balance!', 'error')
        else:
            db.execute('INSERT INTO stakes (user_id, asset, amount, daily_rate) VALUES (?,?,?,?)',
                (session['user_id'], asset, amount, daily_rate))
            db.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, session['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (session['user_id'], 'Staking Started', f'Staked {amount} {asset}', amount))
            db.commit()
            flash(f'Successfully staked ${amount:.2f} in {asset}!', 'success')
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    stakings = db.execute('SELECT * FROM stakes WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    db.close()
    return render_template('stake.html', user=user, stakings=stakings)

@app.route('/stake/unstake/<int:stake_id>', methods=['POST'])
@login_required
def unstake(stake_id):
    db = get_db()
    stake = db.execute('SELECT * FROM stakes WHERE id = ? AND user_id = ?', (stake_id, session['user_id'])).fetchone()
    if stake and stake['status'] == 'Active':
        total = stake['amount'] + stake['earnings']
        db.execute('UPDATE stakes SET status = ? WHERE id = ?', ('Unstaked', stake_id))
        db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (total, stake['earnings'], session['user_id']))
        db.commit()
        flash(f'Unstaked successfully. ${total:.2f} returned to balance.', 'success')
    db.close()
    return redirect(url_for('stake'))

@app.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        plan = request.form.get('plan')
        amount = float(request.form.get('amount', 0))
        roi = float(request.form.get('roi', 150))
        days = int(request.form.get('days', 14))
        if amount <= 0:
            flash('Invalid amount.', 'error')
        elif amount > user['balance']:
            flash('Insufficient balance!', 'error')
        else:
            db.execute('INSERT INTO subscriptions (user_id, plan, amount, roi_percent, duration_days) VALUES (?,?,?,?,?)',
                (session['user_id'], plan, amount, roi, days))
            db.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, session['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (session['user_id'], 'Plan Subscribed', f'Subscribed to {plan} plan for ${amount:.2f}', amount))
            db.commit()
            flash(f'Successfully subscribed to {plan} plan!', 'success')
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    subscriptions = db.execute('SELECT * FROM subscriptions WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    db.close()
    return render_template('subscribe.html', user=user, subscriptions=subscriptions)

@app.route('/signals', methods=['GET', 'POST'])
@login_required
def signals():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        signal_name = request.form.get('signal_name')
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Invalid amount.', 'error')
        elif amount > user['balance']:
            flash('Insufficient balance!', 'error')
        else:
            db.execute('INSERT INTO signal_purchases (user_id, signal_name, amount) VALUES (?,?,?)',
                (session['user_id'], signal_name, amount))
            db.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, session['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (session['user_id'], 'Signal Purchased', f'Purchased {signal_name} signal for ${amount:.2f}', amount))
            db.commit()
            flash(f'Signal "{signal_name}" purchased successfully!', 'success')
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    purchases = db.execute('SELECT * FROM signal_purchases WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    db.close()
    return render_template('signals.html', user=user, purchases=purchases)

@app.route('/settings')
@login_required
def settings():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('settings.html', user=user)

@app.route('/settings/update', methods=['POST'])
@login_required
def settings_update():
    first_name = request.form.get('first_name', '')
    last_name = request.form.get('last_name', '')
    name = f"{first_name} {last_name}".strip()
    if name:
        db = get_db()
        db.execute('UPDATE users SET name = ? WHERE id = ?', (name, session['user_id']))
        db.commit()
        db.close()
        session['user_name'] = name
        flash('Profile updated successfully!', 'success')
    return redirect(url_for('settings'))

@app.route('/settings/change-password', methods=['POST'])
@login_required
def change_password():
    current = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm = request.form.get('confirm_password')
    if new_pw != confirm:
        flash('New passwords do not match!', 'error')
        return redirect(url_for('settings'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if user['password'] != hash_password(current):
        flash('Current password is incorrect!', 'error')
    else:
        db.execute('UPDATE users SET password = ? WHERE id = ?', (hash_password(new_pw), session['user_id']))
        db.commit()
        flash('Password changed successfully!', 'success')
    db.close()
    return redirect(url_for('settings'))

# Admin: view all trades
@app.route('/admin/trades')
@admin_required
def admin_trades():
    db = get_db()
    trades = db.execute('''SELECT t.*, u.name, u.email FROM trades t
                           JOIN users u ON t.user_id = u.id
                           ORDER BY t.created_at DESC''').fetchall()
    db.close()
    return render_template('admin/trades.html', trades=trades)

@app.route('/admin/trade/<int:trade_id>/close', methods=['POST'])
@admin_required
def admin_close_trade(trade_id):
    pnl = float(request.form.get('pnl', 0))
    db = get_db()
    trade = db.execute('SELECT * FROM trades WHERE id = ?', (trade_id,)).fetchone()
    if trade:
        returned = trade['amount'] + pnl
        db.execute('UPDATE trades SET status = ?, profit_loss = ? WHERE id = ?', ('Closed', pnl, trade_id))
        db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (returned, max(pnl,0), trade['user_id']))
        db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
            (trade['user_id'], 'Trade Closed', f'Your {trade["trade_type"]} trade on {trade["symbol"]} was closed. P&L: ${pnl:+.2f}', returned))
        db.commit()
        flash(f'Trade #{trade_id} closed. P&L: ${pnl:+.2f} — balance updated.', 'success')
    db.close()
    return redirect(url_for('admin_trades'))

# Admin: view all stakes
@app.route('/admin/stakes')
@admin_required
def admin_stakes():
    db = get_db()
    stakes = db.execute('''SELECT s.*, u.name, u.email FROM stakes s
                           JOIN users u ON s.user_id = u.id
                           ORDER BY s.created_at DESC''').fetchall()
    db.close()
    return render_template('admin/stakes.html', stakes=stakes)

@app.route('/admin/stake/<int:stake_id>/update', methods=['POST'])
@admin_required
def admin_update_stake(stake_id):
    earnings = float(request.form.get('earnings', 0))
    status = request.form.get('status', 'Active')
    db = get_db()
    stake = db.execute('SELECT * FROM stakes WHERE id = ?', (stake_id,)).fetchone()
    if stake:
        prev_earnings = stake['earnings']
        db.execute('UPDATE stakes SET earnings = ?, status = ? WHERE id = ?', (earnings, status, stake_id))
        if status == 'Unstaked':
            total = stake['amount'] + earnings
            db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (total, earnings, stake['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (stake['user_id'], 'Staking Started', f'Your {stake["asset"]} stake was unstaked. Earnings: ${earnings:.2f} returned to balance.', total))
        elif earnings != prev_earnings:
            # Profit updated while still active - credit difference to balance
            diff = earnings - prev_earnings
            if diff > 0:
                db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (diff, diff, stake['user_id']))
                db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                    (stake['user_id'], 'Staking Started', f'Staking profit of ${diff:.2f} credited to your account from {stake["asset"]} stake.', diff))
        db.commit()
        flash(f'Stake #{stake_id} updated. Balance credited.', 'success')
    db.close()
    return redirect(url_for('admin_stakes'))

# Admin: view all subscriptions
@app.route('/admin/subscriptions')
@admin_required
def admin_subscriptions():
    db = get_db()
    subs = db.execute('''SELECT s.*, u.name, u.email FROM subscriptions s
                         JOIN users u ON s.user_id = u.id
                         ORDER BY s.created_at DESC''').fetchall()
    db.close()
    return render_template('admin/subscriptions.html', subs=subs)

@app.route('/admin/subscription/<int:sub_id>/update', methods=['POST'])
@admin_required
def admin_update_subscription(sub_id):
    earnings = float(request.form.get('earnings', 0))
    status = request.form.get('status', 'Active')
    db = get_db()
    sub = db.execute('SELECT * FROM subscriptions WHERE id = ?', (sub_id,)).fetchone()
    if sub:
        prev_earnings = sub['earnings']
        db.execute('UPDATE subscriptions SET earnings = ?, status = ? WHERE id = ?', (earnings, status, sub_id))
        if status == 'Completed':
            total = sub['amount'] + earnings
            db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (total, earnings, sub['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (sub['user_id'], 'Plan Subscribed', f'Your {sub["plan"]} plan completed. Earnings: ${earnings:.2f} credited to balance.', total))
        elif earnings != prev_earnings:
            diff = earnings - prev_earnings
            if diff > 0:
                db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (diff, diff, sub['user_id']))
                db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                    (sub['user_id'], 'Plan Subscribed', f'Subscription profit of ${diff:.2f} credited from {sub["plan"]} plan.', diff))
        db.commit()
        flash(f'Subscription #{sub_id} updated. Balance credited.', 'success')
    db.close()
    return redirect(url_for('admin_subscriptions'))

# Admin: view all signals
@app.route('/admin/signals')
@admin_required
def admin_signals():
    db = get_db()
    sigs = db.execute('''SELECT sp.*, u.name, u.email FROM signal_purchases sp
                         JOIN users u ON sp.user_id = u.id
                         ORDER BY sp.created_at DESC''').fetchall()
    db.close()
    return render_template('admin/signals.html', sigs=sigs)

@app.route('/admin/signal/<int:sig_id>/update', methods=['POST'])
@admin_required
def admin_update_signal(sig_id):
    status = request.form.get('status', 'Active')
    db = get_db()
    db.execute('UPDATE signal_purchases SET status = ? WHERE id = ?', (status, sig_id))
    db.commit()
    flash(f'Signal #{sig_id} updated to {status}.', 'success')
    db.close()
    return redirect(url_for('admin_signals'))

# Admin: view copy trades
@app.route('/admin/copy-trades')
@admin_required
def admin_copy_trades():
    db = get_db()
    trades = db.execute('''SELECT ct.*, u.name, u.email FROM copy_trades ct
                           JOIN users u ON ct.user_id = u.id
                           ORDER BY ct.created_at DESC''').fetchall()
    db.close()
    return render_template('admin/copy_trades.html', trades=trades)

@app.route('/admin/copy-trade/<int:trade_id>/update', methods=['POST'])
@admin_required
def admin_update_copy_trade(trade_id):
    profit = float(request.form.get('total_profit', 0))
    status = request.form.get('status', 'Active')
    db = get_db()
    ct = db.execute('SELECT * FROM copy_trades WHERE id = ?', (trade_id,)).fetchone()
    if ct:
        prev_profit = ct['total_profit']
        db.execute('UPDATE copy_trades SET total_profit = ?, status = ? WHERE id = ?', (profit, status, trade_id))
        if status == 'Stopped':
            total = ct['amount'] + profit
            db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (total, max(profit,0), ct['user_id']))
            db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                (ct['user_id'], 'Copy Trade Stopped', f'Copy trading with {ct["trader_name"]} stopped. Profit: ${profit:.2f} + investment returned.', total))
        elif profit != prev_profit:
            diff = profit - prev_profit
            if diff > 0:
                db.execute('UPDATE users SET balance = balance + ?, profit = profit + ? WHERE id = ?', (diff, diff, ct['user_id']))
                db.execute('INSERT INTO trading_activity (user_id, activity_type, description, amount) VALUES (?,?,?,?)',
                    (ct['user_id'], 'Copy Trade Started', f'Copy trading profit of ${diff:.2f} credited from {ct["trader_name"]}.', diff))
        db.commit()
        flash(f'Copy trade #{trade_id} updated. Profit credited to user.', 'success')
    db.close()
    return redirect(url_for('admin_copy_trades'))

# Admin: manage copy traders
@app.route('/admin/traders')
@admin_required
def admin_traders():
    db = get_db()
    traders = db.execute('SELECT * FROM traders ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin/traders.html', traders=traders)

@app.route('/admin/traders/add', methods=['POST'])
@admin_required
def admin_add_trader():
    db = get_db()
    db.execute('''INSERT INTO traders (name, country, photo, roi, win_rate, wins, losses, copiers, profit_share)
                  VALUES (?,?,?,?,?,?,?,?,?)''', (
        request.form.get('name'),
        request.form.get('country'),
        request.form.get('photo', 'https://randomuser.me/api/portraits/men/1.jpg'),
        float(request.form.get('roi', 0)),
        float(request.form.get('win_rate', 0)),
        int(request.form.get('wins', 0)),
        int(request.form.get('losses', 0)),
        int(request.form.get('copiers', 0)),
        float(request.form.get('profit_share', 10)),
    ))
    db.commit()
    db.close()
    flash('Trader added successfully!', 'success')
    return redirect(url_for('admin_traders'))

@app.route('/admin/traders/edit/<int:trader_id>', methods=['POST'])
@admin_required
def admin_edit_trader(trader_id):
    db = get_db()
    db.execute('''UPDATE traders SET name=?, country=?, photo=?, roi=?, win_rate=?,
                  wins=?, losses=?, copiers=?, profit_share=?, is_active=? WHERE id=?''', (
        request.form.get('name'),
        request.form.get('country'),
        request.form.get('photo'),
        float(request.form.get('roi', 0)),
        float(request.form.get('win_rate', 0)),
        int(request.form.get('wins', 0)),
        int(request.form.get('losses', 0)),
        int(request.form.get('copiers', 0)),
        float(request.form.get('profit_share', 10)),
        int(request.form.get('is_active', 1)),
        trader_id
    ))
    db.commit()
    db.close()
    flash('Trader updated!', 'success')
    return redirect(url_for('admin_traders'))

@app.route('/admin/traders/delete/<int:trader_id>', methods=['POST'])
@admin_required
def admin_delete_trader(trader_id):
    db = get_db()
    db.execute('DELETE FROM traders WHERE id = ?', (trader_id,))
    db.commit()
    db.close()
    flash('Trader removed.', 'success')
    return redirect(url_for('admin_traders'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
