#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from flask import Blueprint

from controllers.auth_security import *
from controllers.fixtures_load import *

from controllers.client_article import *
from controllers.client_panier import *
from controllers.client_commande import *
from controllers.client_commentaire import *
from controllers.client_coordonnee import *

from controllers.admin_article import admin_article
from controllers.admin_declinaison_article import *
from controllers.admin_commande import *
from controllers.admin_type_article import *
from controllers.admin_dataviz import *
from controllers.admin_commentaire import *
from controllers.client_liste_envies import *

app = Flask(__name__)
app.secret_key = 'une cle() : grain de sel(any random string)'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def show_accueil():
    if 'role' in session:
        if session['role'] == 'ROLE_admin':
            return render_template('/admin/commandes/show.html')
        else:
            return render_template('/client/boutique/_filtre.html')
    return render_template('auth/login.html')


@app.before_request
def before_request():
    if request.path.startswith('/admin') or request.path.startswith('/client'):
        if 'role' not in session:
            return redirect('/login')
        else:
            if (request.path.startswith('/client') and session['role'] != 'ROLE_client') or (request.path.startswith('/admin') and session['role'] != 'ROLE_admin'):
                print('pb de route : ', session['role'], request.path.title(), ' => deconnexion')
                session.pop('login', None)
                session.pop('role', None)
                flash("PB route / rôle / autorisation", "alert-warning")
                return redirect('/logout')




@app.route('/client/panier/filtre', methods=['GET', 'POST'])
def filter_usb():
    if request.method == 'POST':
        session['filter_word'] = request.form.get('filter_word')
        session['filter_types'] = request.form.getlist('filter_types')
        session['filter_prix_min'] = request.form.get('filter_prix_min')
        session['filter_prix_max'] = request.form.get('filter_prix_max')
        session['filter_capacity'] = request.form.get('filter_capacity')
        session['filter_speed'] = request.form.get('filter_speed')
        session['filter_brand'] = request.form.get('filter_brand')
        # Appliquez votre logique de filtrage ici

    items_filtre = [
        {'id_type_article': '1', 'libelle': 'USB 2.0'},
        {'id_type_article': '2', 'libelle': 'USB 3.0'},
        {'id_type_article': '3', 'libelle': 'USB-C'},
    ]  # Remplacez par vos données réelles

    return render_template('/client/boutique/_filtre.html', items_filtre=items_filtre)

@app.route('/client/panier/filtre/suppr', methods=['POST'])
def remove_filter():
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_capacity', None)
    session.pop('filter_speed', None)
    session.pop('filter_brand', None)
    return redirect(url_for('filter_usb'))

app.register_blueprint(auth_security)
app.register_blueprint(fixtures_load)

app.register_blueprint(client_article)
app.register_blueprint(client_commande)
app.register_blueprint(client_commentaire)
app.register_blueprint(client_panier)
app.register_blueprint(client_coordonnee)
app.register_blueprint(client_liste_envies)

app.register_blueprint(admin_article)
app.register_blueprint(admin_declinaison_article)
app.register_blueprint(admin_commande)
app.register_blueprint(admin_type_article)
app.register_blueprint(admin_dataviz)
app.register_blueprint(admin_commentaire)

if __name__ == '__main__':
    app.run()
