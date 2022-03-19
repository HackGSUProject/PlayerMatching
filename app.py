import os
from flask import Flask, redirect, url_for, render_template, request, flash
from models import Users 
from database import db
from dotenv import find_dotenv, load_dotenv
from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user,
    LoginManager,
    UserMixin,
)
import os
import random
from dotenv import find_dotenv, load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

load_dotenv(find_dotenv())


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secretKey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
VERIFY_SERVICE_SID = os.getenv('VERIFY_SERVICE_SID')
client = Client(account_sid, auth_token)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

db.init_app(app)
with app.app_context():
    # db.drop_all()
    db.create_all()
    user = Users.query.all()

def sendVarificationCode(phone):
    verification = client.verify \
                     .services(VERIFY_SERVICE_SID) \
                     .verifications \
                     .create(to=phone, channel='sms')
    return verification.status

def check_verification_token(phone, token):
    verification_check = client.verify \
                           .services(VERIFY_SERVICE_SID) \
                           .verification_checks \
                           .create(to=phone, code=token)
    if verification_check.status == 'approved':
        return True
    elif verification_check.status == 'pending':
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        data = request.form
        username = data["username"]
        password = data["password"]
    if request.method == "POST":
        user = Users.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Incorrect Password")
        flash("Incorrect Username")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        firstName = data["Fname"]
        LastName = data["Lname"]
        username = data["username"]
        email = data["Email"]
        phone = data["phone"]
        password = data["password"]
        discord = data["discord"]
        status = random.randint(1,10)

        hashed_password = generate_password_hash(password, method='sha256')
        user = Users.query.filter_by(username=username).first()
        if user:
            flash("This user already exsists!")
        
        new_user = Users(
            Fname=firstName,
            Lname=LastName,
            username=username,
            Email=email,
            Pnumber=phone,
            discord=discord,
            status=status,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        phone = "+1"+phone
        sendVarificationCode(phone)
        return redirect(url_for('varification'))
    return render_template('register.html')

def randomUser():
    randomUser = random.choice(user) 
    return randomUser

@app.route('/varification' , methods=['GET', 'POST'])
def varification():
    if request.method == "POST":
        data = request.form
        phone = data["phone"]
        varification = data["varification"]
        phone = "+1"+phone
        status = check_verification_token(phone, varification)

        if status:
            return redirect(url_for('login'))
        else:
            flash("Wrong varification code")
    return render_template('varification.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    currentUser = current_user.Fname + " " +  current_user.Lname
    currentUserDiscord = current_user.discord
    match = ""
    matchDiscord=""
    current_user_start_status_start = current_user.status
    current_user_end_status_end = current_user.status+5
    for users in user:
        if users.status in range(current_user_start_status_start, (current_user_end_status_end)):
            match = users.Fname + " " + users.Lname
        else:
            matching = randomUser()
            if matching.id != current_user.id:
                match = matching.Fname + " " + matching.Lname
                matchDiscord = matching.discord
    return render_template(
        'home.html',
        currentUser=currentUser,
        currentUserDiscord=currentUserDiscord,
        match = match,
        matchDiscord=matchDiscord
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

app.run(
    host=os.getenv('IP', '0.0.0.0'),
    port=int(os.getenv('PORT', 8080)),
    debug=True
)



