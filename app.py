from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Veritabanını oluştur
with app.app_context():
    db.create_all()

def send_email(to_email):
    sender_email = "c5cf304984339d"
    password = "0bda298d2704d0"
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = "Kayıt Başarılı"

    body = "Kayıt işleminiz başarılı bir şekilde tamamlandı."
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.mailtrap.io", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())
        print("E-posta başarıyla gönderildi.")
    except smtplib.SMTPException as e:
        print("E-posta gönderilirken bir hata oluştu:", e)
    finally:
        server.quit()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Şifreleme metodunu güncelledik

        new_user = User(email=email, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            send_email(email)
            flash("Kayıt başarılı! Lütfen giriş yapın.", "success")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("Bu e-posta adresi zaten kayıtlı.", "danger")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Giriş başarılı!", "success")
            return redirect(url_for('hello'))
        else:
            flash("Geçersiz giriş bilgileri.", "danger")

    return render_template('login.html')

@app.route('/hello')
def hello():
    if 'user_id' not in session:
        flash("Bu sayfaya erişmek için lütfen giriş yapın.", "danger")
        return redirect(url_for('login'))
    return render_template('hello.html')
