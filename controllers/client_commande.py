#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                            template_folder='templates')

@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT p.*, c.nom_cle_usb, c.prix_cle_usb
             FROM panier p
             JOIN cle_usb c ON p.cle_usb_id = c.id_cle_usb
             WHERE p.utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()
    if len(articles_panier) >= 1:
        sql = '''SELECT SUM(p.quantite * c.prix_cle_usb) as prix_total
                 FROM panier p
                 JOIN cle_usb c ON p.cle_usb_id = c.id_cle_usb
                 WHERE p.utilisateur_id = %s'''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()['prix_total']
    else:
        prix_total = None
    return render_template('client/boutique/panier_validation_adresses.html',
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           validation=1)

@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT p.*, c.nom_cle_usb, c.prix_cle_usb
             FROM panier p
             JOIN cle_usb c ON p.cle_usb_id = c.id_cle_usb
             WHERE p.utilisateur_id = %s'''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()
    if items_ligne_panier is None or len(items_ligne_panier) < 1:
        flash(u'Pas d\'articles dans le panier', 'alert-warning')
        return redirect('/client/article/show')

    sql = '''INSERT INTO commande (date_achat, utilisateur_id, etat_commande) VALUES (NOW(), %s, 'en cours')'''
    mycursor.execute(sql, (id_client,))
    get_db().commit()

    sql = '''SELECT LAST_INSERT_ID() as last_insert_id'''
    mycursor.execute(sql)
    id_commande = mycursor.fetchone()['last_insert_id']

    for item in items_ligne_panier:
        sql = '''DELETE FROM panier WHERE utilisateur_id = %s AND cle_usb_id = %s'''
        mycursor.execute(sql, (id_client, item['cle_usb_id']))

        sql = '''INSERT INTO ligne_commande (commande_id, cle_usb_id, prix, quantite) VALUES (%s, %s, %s, %s)'''
        mycursor.execute(sql, (id_commande, item['cle_usb_id'], item['prix_cle_usb'], item['quantite']))

    get_db().commit()
    flash(u'Commande ajoutée','alert-success')
    return redirect('/client/article/show')

@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT c.*, SUM(lc.prix * lc.quantite) as prix_total
             FROM commande c
             JOIN ligne_commande lc ON c.id_commande = lc.commande_id
             WHERE c.utilisateur_id = %s
             GROUP BY c.id_commande
             ORDER BY c.etat_commande, c.date_achat DESC'''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        sql = '''SELECT c.nom_cle_usb, lc.quantite, lc.prix
                 FROM ligne_commande lc
                 JOIN cle_usb c ON lc.cle_usb_id = c.id_cle_usb
                 WHERE lc.commande_id = %s'''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses)