from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Transaction
from . import db

views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        type = request.form.get("type")
        amount = request.form.get("amount")
        amount = float(amount)

        if len(type) < 1:
            flash('Note is too short!', category='error')
        elif amount <= 0:
            flash('Please enter a positive value!', category='error')
        else:
            new_transaction = Transaction(type=type, amount=amount, user_id=current_user.id)  # providing the schema for the note
            db.session.add(new_transaction)  # adding the note to the database
            db.session.commit()
            flash('Transaction added successfully!', category='success')

    return render_template("home.html", user=current_user)


@views.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect password, try again!", category="error")
        else:
            flash("Invalid email", category="error")

    return render_template("login.html", user=current_user)

@views.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already registered.",category="error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category="error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character.", category="error")
        elif password1 != password2:
            flash("The passwords must be equals to each other.", category="error")
        elif len(password1) < 7:
            flash("Your password must be at least 7 characters long. ", category="error")
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("User has been added successfully", category="success")

            return redirect(url_for("views.home"))

    return render_template("sign-up.html", user=current_user)

@views.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.login"))