#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                                template_folder='templates')

@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''INSERT INTO liste_envies (utilisateur_id, cle_usb_id) VALUES (%s, %s)'''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''DELETE FROM liste_envies WHERE utilisateur_id = %s AND cle_usb_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/envies/show')

@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT c.* FROM cle_usb c
             JOIN liste_envies le ON c.id_cle_usb = le.cle_usb_id
             WHERE le.utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()
    sql = '''SELECT c.* FROM cle_usb c
             JOIN historique h ON c.id_cle_usb = h.cle_usb_id
             WHERE h.utilisateur_id = %s
             ORDER BY h.date_consultation DESC
             LIMIT 5'''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()
    nb_liste_envies = len(articles_liste_envies)
    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nb_liste_envies)

def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    sql = '''SELECT * FROM historique WHERE cle_usb_id = %s AND utilisateur_id = %s'''
    mycursor.execute(sql, (article_id, client_id))
    historique_produit = mycursor.fetchone()
    if historique_produit:
        sql = '''UPDATE historique SET date_consultation = NOW() WHERE cle_usb_id = %s AND utilisateur_id = %s'''
        mycursor.execute(sql, (article_id, client_id))
    else:
        sql = '''INSERT INTO historique (cle_usb_id, utilisateur_id, date_consultation) VALUES (%s, %s, NOW())'''
        mycursor.execute(sql, (article_id, client_id))
    sql = '''SELECT COUNT(*) as count FROM historique WHERE utilisateur_id = %s'''
    mycursor.execute(sql, (client_id,))
    historiques = mycursor.fetchone()
    if historiques['count'] > 5:
        sql = '''DELETE FROM historique WHERE utilisateur_id = %s ORDER BY date_consultation ASC LIMIT 1'''
        mycursor.execute(sql, (client_id,))
    get_db().commit()

@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
def client_liste_envies_article_move():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    action = request.path.split('/')[-1]

    sql = '''SELECT ordre FROM liste_envies WHERE utilisateur_id = %s AND cle_usb_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    current_order = mycursor.fetchone()['ordre']

    if action == 'up' and current_order > 1:
        sql = '''UPDATE liste_envies SET ordre = ordre + 1 WHERE utilisateur_id = %s AND ordre = %s'''
        mycursor.execute(sql, (id_client, current_order - 1))
        sql = '''UPDATE liste_envies SET ordre = ordre - 1 WHERE utilisateur_id = %s AND cle_usb_id = %s'''
        mycursor.execute(sql, (id_client, id_article))
    elif action == 'down':
        sql = '''UPDATE liste_envies SET ordre = ordre - 1 WHERE utilisateur_id = %s AND ordre = %s'''
        mycursor.execute(sql, (id_client, current_order + 1))
        sql = '''UPDATE liste_envies SET ordre = ordre + 1 WHERE utilisateur_id = %s AND cle_usb_id = %s'''
        mycursor.execute(sql, (id_client, id_article))
    elif action == 'first':
        sql = '''UPDATE liste_envies SET ordre = ordre + 1 WHERE utilisateur_id = %s AND ordre < %s'''
        mycursor.execute(sql, (id_client, current_order))
        sql = '''UPDATE liste_envies SET ordre = 1 WHERE utilisateur_id = %s AND cle_usb_id = %s'''
        mycursor.execute(sql, (id_client, id_article))
    elif action == 'last':
        sql = '''SELECT MAX(ordre) as max_ordre FROM liste_envies WHERE utilisateur_id = %s'''
        mycursor.execute(sql, (id_client,))
        max_order = mycursor.fetchone()['max_ordre']
        sql = '''UPDATE liste_envies SET ordre = ordre - 1 WHERE utilisateur_id = %s AND ordre > %s'''
        mycursor.execute(sql, (id_client, current_order))
        sql = '''UPDATE liste_envies SET ordre = %s WHERE utilisateur_id = %s AND cle_usb_id = %s'''
        mycursor.execute(sql, (max_order, id_client, id_article))

    get_db().commit()
    return redirect('/client/envies/show')