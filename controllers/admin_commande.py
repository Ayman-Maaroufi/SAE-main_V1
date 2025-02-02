#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')

@admin_commande.route('/admin/commande/show', methods=['GET'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']
    sql = '''
    SELECT c.id_commande, c.date_achat, c.etat_commande, u.login, SUM(lc.prix * lc.quantite) as total_commande
    FROM commande c
    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
    JOIN ligne_commande lc ON c.id_commande = lc.commande_id
    GROUP BY c.id_commande, c.date_achat, c.etat_commande, u.login
    ORDER BY c.date_achat DESC
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        sql = '''
        SELECT a.nom_cle_usb, lc.quantite, lc.prix
        FROM ligne_commande lc
        JOIN cle_usb a ON lc.cle_usb_id = a.id_cle_usb
        WHERE lc.commande_id = %s
        '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql = '''
        SELECT a.libelle_adresse, a.nom_adresse, a.rue, a.code_postal, a.ville
        FROM adresse a
        JOIN commande c ON (a.id_adresse = c.adresse_livraison_id OR a.id_adresse = c.adresse_facturation_id)
        WHERE c.id_commande = %s
        '''
        mycursor.execute(sql, (id_commande,))
        commande_adresses = mycursor.fetchall()

    return render_template('admin/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses
                           )

@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        sql = '''
        UPDATE commande
        SET etat_commande = 'expediee'
        WHERE id_commande = %s
        '''
        mycursor.execute(sql, (commande_id,))
        get_db().commit()
    return redirect('/admin/commande/show')