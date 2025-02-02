from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from connexion_db import get_db

auth_security = Blueprint('auth_security', __name__, template_folder='templates')


@auth_security.route('/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    if request.method == 'POST':
        mycursor = get_db().cursor()
        login = request.form.get('login')
        password = request.form.get('password')
        sql = "SELECT * FROM utilisateur WHERE login = %s"
        mycursor.execute(sql, (login,))
        user = mycursor.fetchone()
        if user:
            if check_password_hash(user['password'], password):
                session['login'] = user['login']
                session['role'] = user['role']
                session['id_user'] = user['id_utilisateur']
                if user['role'] == 'ROLE_admin':
                    return render_template('/admin/commandes/show.html')
                else:
                    return render_template('/client/boutique/_filtre.html')
            else:
                flash(u'Vérifier votre mot de passe et essayer encore.', 'alert-warning')
                return redirect('/login')
        else:
            flash(u'Vérifier votre login et essayer encore.', 'alert-warning')
            return redirect('/login')


@auth_security.route('/signup', methods=['GET', 'POST'])
def auth_signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')

    if request.method == 'POST':
        mycursor = get_db().cursor()
        email = request.form.get('email')
        login = request.form.get('login')
        password = request.form.get('password')

        # Check if username or email already exists
        sql = "SELECT * FROM utilisateur WHERE login = %s OR email = %s"
        mycursor.execute(sql, (login, email))
        user = mycursor.fetchone()
        if user:
            flash(u'Votre adresse Email ou votre Login existe déjà', 'alert-warning')
            return redirect('/signup')

        # Insert new user
        hashed_password = generate_password_hash(password, method='sha256')
        sql = "INSERT INTO utilisateur (login, email, password, role) VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql, (login, email, hashed_password, 'ROLE_client'))
        get_db().commit()

        # Get the last inserted id
        sql = "SELECT LAST_INSERT_ID() as last_insert_id"
        mycursor.execute(sql)
        info_last_id = mycursor.fetchone()
        id_user = info_last_id['last_insert_id']

        # Set session
        session.clear()
        session['login'] = login
        session['role'] = 'ROLE_client'
        session['id_user'] = id_user

        return redirect('/client/article/show')


@auth_security.route('/logout')
def auth_logout():
    session.clear()
    return render_template('auth/login.html')