import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = 'farming_secret_key_123'
DATABASE = 'database.db'

# ---------------------------------------------------------
# LANGUAGE DICTIONARY (5 LANGUAGES)
# ---------------------------------------------------------
TRANSLATIONS = {
    'en': {
        'title': 'Kisan Assistant',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'dashboard': 'Dashboard',
        'email': 'Email',
        'password': 'Password',
        'name': 'Full Name',
        'village': 'Village',
        'submit': 'Submit',
        'welcome': 'Welcome',
        'ai_problem': 'Crop Doctor (AI)',
        'ai_info': 'Crop Wiki (AI)',
        'ai_chat': 'Voice Assistant',
        'community': 'Farmer Community',
        'market': 'Market Prices',
        'products': 'Buy/Sell Organic',
        'schemes': 'Govt Schemes',
        'profile': 'My Profile',
        'enter_crop': 'Enter Crop Name',
        'describe_prob': 'Describe Problem',
        'analyze': 'Analyze',
        'result': 'Result',
        'post': 'Post',
        'contact': 'Contact',
        'price': 'Price',
        'disclaimer': 'Note: This is computer-generated guidance, not an expert diagnosis.'
    },
    'hi': {
        'title': 'किसान सहायक',
        'login': 'लॉग इन',
        'register': 'पंजीकरण',
        'logout': 'लॉग आउट',
        'dashboard': 'डैशबोर्ड',
        'email': 'ईमेल',
        'password': 'पासवर्ड',
        'name': 'पूरा नाम',
        'village': 'गाँव',
        'submit': 'जमा करें',
        'welcome': 'स्वागत है',
        'ai_problem': 'फसल डॉक्टर (AI)',
        'ai_info': 'फसल जानकारी',
        'ai_chat': 'सहायक से पूछें',
        'community': 'किसान समुदाय',
        'market': 'बाजार भाव',
        'products': 'जैविक उत्पाद',
        'schemes': 'सरकारी योजनाएं',
        'profile': 'मेरी प्रोफाइल',
        'enter_crop': 'फसल का नाम लिखें',
        'describe_prob': 'समस्या का वर्णन करें',
        'analyze': 'जांच करें',
        'result': 'परिणाम',
        'post': 'पोस्ट करें',
        'contact': 'संपर्क',
        'price': 'कीमत',
        'disclaimer': 'नोट: यह कंप्यूटर जनित सलाह है, विशेषज्ञ निदान नहीं।'
    },
    'mr': {
        'title': 'किसान मित्र',
        'login': 'लॉगिन',
        'register': 'नोंदणी',
        'logout': 'बाहेर पडा',
        'dashboard': 'डॅशबोर्ड',
        'email': 'ईमेल',
        'password': 'पासवर्ड',
        'name': 'पूर्ण नाव',
        'village': 'गाव',
        'submit': 'सादर करा',
        'welcome': 'स्वागत आहे',
        'ai_problem': 'पीक डॉक्टर (AI)',
        'ai_info': 'पीक माहिती',
        'ai_chat': 'कृषी सहाय्यक',
        'community': 'शेतकरी समूह',
        'market': 'बाजार भाव',
        'products': 'सेंद्रिय उत्पादने',
        'schemes': 'शासकीय योजना',
        'profile': 'माझी प्रोफाइल',
        'enter_crop': 'पिकाचे नाव',
        'describe_prob': 'समस्येचे वर्णन करा',
        'analyze': 'तपासा',
        'result': 'निकाल',
        'post': 'पोस्ट करा',
        'contact': 'संपर्क',
        'price': 'किंमत',
        'disclaimer': 'टीप: हे मार्गदर्शन आहे, तज्ञांचे निदान नाही.'
    },
    # Simplified placeholders for Kannada (kn) and Telugu (te) for brevity
    # In a full production app, these would be fully translated script
    'kn': {
        'title': 'ಕिसಾನ್ ಅಸಿಸ್ಟೆಂಟ್', 'login': 'ಲಾಗಿನ್', 'register': 'ನೋಂದಣಿ', 'logout': 'ಲಾಗ್ ಔಟ್',
        'dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್', 'email': 'ಇಮೇಲ್', 'password': 'ಪಾಸ್‌ವರ್ಡ್', 'name': 'ಹೆಸರು',
        'village': 'ಗ್ರಾಮ', 'submit': 'ಸಲ್ಲಿಸಿ', 'welcome': 'ಸ್ವಾಗತ', 'ai_problem': 'ಬೆಳೆ ವೈದ್ಯ',
        'ai_info': 'ಬೆಳೆ ಮಾಹಿತಿ', 'ai_chat': 'ಸಹಾಯಕ', 'community': 'ಸಮುದಾಯ', 'market': 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆ',
        'products': 'ಸಾವಯವ ಉತ್ಪನ್ನ', 'schemes': 'ಸರ್ಕಾರಿ ಯೋಜನೆ', 'profile': 'ಪ್ರೊಫೈಲ್',
        'enter_crop': 'ಬೆಳೆ ಹೆಸರು', 'describe_prob': 'ಸಮಸ್ಯೆ ವಿವರಿಸಿ', 'analyze': 'ವಿಶ್ಲೇಷಿಸಿ',
        'result': 'ಫಲಿತಾಂಶ', 'post': 'ಪೋಸ್ಟ್', 'contact': 'ಸಂಪರ್ಕ', 'price': 'ಬೆಲೆ', 'disclaimer': 'ಸೂಚನೆ: ಇದು ಮಾರ್ಗದರ್ಶನ ಮಾತ್ರ.'
    },
    'te': {
        'title': 'కిసాన్ అసిస్టెంట్', 'login': 'లాగిన్', 'register': 'నమోదు', 'logout': 'లాగ్ అవుట్',
        'dashboard': 'డ్యాష్‌ బోర్డ్', 'email': 'ఇమెయిల్', 'password': 'పాస్‌వర్డ్', 'name': 'పేరు',
        'village': 'గ్రామం', 'submit': 'సమర్పించు', 'welcome': 'స్వాగతం', 'ai_problem': 'పంట డాక్టర్',
        'ai_info': 'పంట సమాచారం', 'ai_chat': 'సహాయకుడు', 'community': 'రైతు సంఘం', 'market': 'మార్కెట్ ధరలు',
        'products': 'సేంద్రీయ ఉత్పత్తులు', 'schemes': 'ప్రభుత్వ పథకాలు', 'profile': 'ప్రొఫైల్',
        'enter_crop': 'పంట పేరు', 'describe_prob': 'సమస్యను వివరించండి', 'analyze': 'విశ్లేషించు',
        'result': 'ఫలితం', 'post': 'పోస్ట్', 'contact': 'సంప్రదించండి', 'price': 'ధర', 'disclaimer': 'గమనిక: ఇది మార్గదర్శకత్వం మాత్రమే.'
    }
}

# ---------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Users
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT,
            village TEXT, state TEXT, district TEXT, lang TEXT, crop TEXT
        )''')
        # Community Posts
        db.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, video_link TEXT, likes INTEGER DEFAULT 0
        )''')
        # Comments
        db.execute('''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, content TEXT
        )''')
        # Organic Products
        db.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, category TEXT, quantity TEXT, price TEXT, location TEXT, contact TEXT
        )''')
        # Govt Schemes (Static data loader)
        db.execute('''CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY, name TEXT, description TEXT, eligibility TEXT, link TEXT
        )''')
        # Market Prices
        db.execute('''CREATE TABLE IF NOT EXISTS market (
            id INTEGER PRIMARY KEY, crop TEXT, market_loc TEXT, price INTEGER, date TEXT
        )''')
        
        # Seed Data - Schemes
        cursor = db.execute("SELECT count(*) FROM schemes")
        if cursor.fetchone()[0] == 0:
            db.execute("INSERT INTO schemes (name, description, eligibility, link) VALUES (?, ?, ?, ?)",
                       ('PM Kisan Samman Nidhi', 'Financial benefit of Rs 6000/year', 'Small/Marginal Farmers', 'https://pmkisan.gov.in'))
            db.execute("INSERT INTO schemes (name, description, eligibility, link) VALUES (?, ?, ?, ?)",
                       ('Fasal Bima Yojana', 'Crop Insurance Scheme', 'All Farmers', 'https://pmfby.gov.in'))

        # Seed Data - Market Prices (Mock)
        cursor = db.execute("SELECT count(*) FROM market")
        if cursor.fetchone()[0] == 0:
            db.execute("INSERT INTO market (crop, market_loc, price, date) VALUES (?, ?, ?, ?)", ('Onion', 'Pune', 25, '2023-10-25'))
            db.execute("INSERT INTO market (crop, market_loc, price, date) VALUES (?, ?, ?, ?)", ('Onion', 'Mumbai', 28, '2023-10-25'))
            db.execute("INSERT INTO market (crop, market_loc, price, date) VALUES (?, ?, ?, ?)", ('Tomato', 'Pune', 15, '2023-10-25'))
            db.execute("INSERT INTO market (crop, market_loc, price, date) VALUES (?, ?, ?, ?)", ('Wheat', 'Mumbai', 32, '2023-10-25'))
        
        db.commit()

# ---------------------------------------------------------
# MOCK AI LOGIC
# ---------------------------------------------------------
def get_mock_problem_solution(lang, crop, problem):
    # Very basic keyword matching
    p_lower = problem.lower()
    
    # Base Responses (English keys mapped to specific lang return)
    responses = {
        'yellow': {
            'issue': 'Nitrogen Deficiency or Yellow Mosaic Virus',
            'reason': 'Lack of nutrients in soil or whitefly attack.',
            'steps': 'Apply Neem oil spray. Add organic compost or urea.',
        },
        'holes': {
            'issue': 'Caterpillar / Stem Borer',
            'reason': 'Larvae eating leaves.',
            'steps': 'Use Pheromone traps. Spray chilli-garlic solution.',
        },
        'default': {
            'issue': 'General Stress / Unknown',
            'reason': 'Could be water stress or fungal infection.',
            'steps': 'Ensure proper drainage. Remove infected parts.',
        }
    }
    
    key = 'default'
    if 'yellow' in p_lower or 'pil' in p_lower: key = 'yellow' # 'pil' for pila (hindi/mr)
    if 'hole' in p_lower or 'eat' in p_lower: key = 'holes'

    # Translation wrapper (Mocking translation by returning Eng for now, real app needs dict)
    # Ideally, we would have a huge dictionary here for every condition in 5 languages.
    # For this Phase 1 demo, we return English text but the wrapper structure is there.
    return responses[key]

def get_mock_crop_info(crop_name):
    # Static Data
    return {
        'Soil': 'Well-drained loamy soil',
        'Water': 'Regular irrigation, do not waterlog',
        'Weather': 'Warm and humid',
        'Stages': 'Sowing -> Vegetative -> Flowering -> Maturity',
        'Tips': 'Use organic manure before sowing.'
    }

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.context_processor
def inject_lang():
    lang = session.get('lang', 'en')
    return dict(t=TRANSLATIONS.get(lang, TRANSLATIONS['en']), lang_code=lang)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, email, password, village, state, district, lang, crop) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (request.form['name'], request.form['email'], request.form['password'],
                        request.form['village'], request.form['state'], request.form['district'],
                        request.form['lang'], request.form['crop']))
            db.commit()
            return redirect(url_for('login'))
        except:
            flash("Email already exists")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                          (request.form['email'], request.form['password'])).fetchone()
        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['lang'] = user['lang']
            session['location'] = user['district'] # For market prices
            return redirect(url_for('dashboard'))
        flash("Invalid Credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'])

# --- AI MODULES ---
@app.route('/ai_problem', methods=['GET', 'POST'])
def ai_problem():
    if 'user_id' not in session: return redirect(url_for('login'))
    result = None
    if request.method == 'POST':
        crop = request.form['crop']
        problem = request.form['problem']
        result = get_mock_problem_solution(session['lang'], crop, problem)
    return render_template('ai_problem.html', result=result)

@app.route('/ai_info', methods=['GET', 'POST'])
def ai_info():
    if 'user_id' not in session: return redirect(url_for('login'))
    result = None
    if request.method == 'POST':
        result = get_mock_crop_info(request.form['crop'])
    return render_template('ai_info.html', result=result)

@app.route('/ai_chat', methods=['GET', 'POST'])
def ai_chat():
    if 'user_id' not in session: return redirect(url_for('login'))
    response = None
    if request.method == 'POST':
        # Mock Friendly Chat
        q = request.form['query']
        lang = session['lang']
        if lang == 'hi':
            response = "नमस्ते! मैं आपका कृषि मित्र हूँ। आपकी फसल अच्छी दिख रही है। पानी का ध्यान रखें।"
        elif lang == 'mr':
            response = "नमस्कार! काळजी करू नका, मी इथे आहे. हवामान शेतीसाठी चांगले आहे."
        else:
            response = "Hello! I am your farming friend. Don't worry, keep the soil moisture balanced."
    return render_template('ai_chat.html', response=response)

# --- COMMUNITY ---
@app.route('/community', methods=['GET', 'POST'])
def community():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        if 'content' in request.form: # New Post
            db.execute("INSERT INTO posts (user_id, content, video_link) VALUES (?, ?, ?)",
                       (session['user_id'], request.form['content'], request.form['video']))
        elif 'like_post' in request.form: # Like
            db.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (request.form['like_post'],))
        db.commit()
        return redirect(url_for('community'))
    
    posts = db.execute("SELECT p.*, u.name, u.village FROM posts p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC").fetchall()
    return render_template('community.html', posts=posts)

# --- PRODUCTS ---
@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO products (user_id, name, category, quantity, price, location, contact) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (session['user_id'], request.form['name'], request.form['category'], 
                    request.form['quantity'], request.form['price'], session['location'], request.form['contact']))
        db.commit()
    
    items = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template('products.html', items=items)

# --- SCHEMES & MARKET ---
@app.route('/schemes')
def schemes():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    schemes_data = db.execute("SELECT * FROM schemes").fetchall()
    return render_template('schemes.html', schemes=schemes_data)

@app.route('/market')
def market():
    if 'user_id' not in session: return redirect(url_for('login'))
    # Logic: Show prices for Mumbai or Pune based on user location approx, defaults to showing all for demo
    db = get_db()
    prices = db.execute("SELECT * FROM market").fetchall()
    return render_template('market.html', prices=prices)

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
