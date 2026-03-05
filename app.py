import os
from flask import Flask, redirect, render_template, request, session, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp
from authlib.integrations.flask_client import OAuth
from api_key import CLIENT_ID, CLIENT_SECRET


app = Flask(__name__)

# Security: Use environment variable for secret key, with fallback for development
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    # Generate a random key for development only - sessions will be invalidated on restart
    import secrets
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    print("WARNING: Using randomly generated SECRET_KEY. Set SECRET_KEY environment variable for production.")

# CSRF Protection configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.environ.get('WTF_CSRF_SECRET_KEY', app.config['SECRET_KEY'])

# Session security
# Only enable secure cookies in production (when HTTPS is used)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Configure SQLAlchemy database with absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "users.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

auth = OAuth(app)

google = auth.register(
    name='google',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url='https://accounts.google/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# Initialize Flask-WTF
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)


# WTForms for authentication with password validation
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=25, message='Username must be between 3 and 25 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
        Regexp(r'^(?=.*[a-zA-Z])(?=.*\d)', message='Password must contain both letters and numbers')
    ])
    submit = SubmitField('Register')


def validate_password_strength(password):
    """Validate password meets strength requirements"""
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not any(c.isalpha() for c in password):
        return "Password must contain at least one letter"
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number"
    return None


# Database Model
class User(db.Model):
    # Class Variables
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Routes

@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register')
def register_page():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

# Login Route

@app.route('/login', methods=['POST'])
def login():
    # Collect info from the form
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('index.html', error='Please provide both username and password')
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error='Invalid username or password')

# Register Route

@app.route('/create-account', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return render_template('index.html', error='Please provide both username and password')
    
    # Validate password strength
    error = validate_password_strength(password)
    if error:
        return render_template('index.html', error=error)
    
    user = User.query.filter_by(username=username).first()
    if user:
        return render_template('index.html', error='Username already exists')
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        return redirect(url_for('dashboard'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

# login google

@app.route('/login/google')
def login_google():
    try:
        redirect_uri = url_for('authorize', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        app.logger.error(f"Error during Google login: {e}")
        return "Error during Google login. Please try again later.", 500
    
@app.route('/authorize/google')
def authorize():
    token = google.authorize_access_token()
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    username = user_info['email']

    user = User.query.filter_by(username=username).first()
    if not user:
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
    session['username'] = username
    session['oauth_token'] = token
    return redirect(url_for('dashboard'))

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template('dashboard.html', username=session.get('username'))
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

