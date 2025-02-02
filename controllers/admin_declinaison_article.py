#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                                      template_folder='templates')

@admin_declinaison_article.route('/admin/declinaison_article/add')
def add_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''SELECT * FROM cle_usb WHERE id_cle_usb = %s'''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    sql = '''SELECT * FROM capacite'''
    mycursor.execute(sql)
    capacites = mycursor.fetchall()
    sql = '''SELECT * FROM type_cle_usb'''
    mycursor.execute(sql)
    types = mycursor.fetchall()
    return render_template('admin/article/add_declinaison_article.html',
                           article=article,
                           capacites=capacites,
                           types=types)

@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    capacite_id = request.form.get('capacite_id')
    type_cle_usb_id = request.form.get('type_cle_usb_id')
    sql = '''INSERT INTO cle_usb (nom_cle_usb, capacite_id, type_cle_usb_id, prix_cle_usb)
             SELECT CONCAT(nom_cle_usb, ' ', (SELECT libelle_capacite FROM capacite WHERE id_capacite = %s)),
                    %s, %s, prix_cle_usb
             FROM cle_usb WHERE id_cle_usb = %s'''
    mycursor.execute(sql, (capacite_id, capacite_id, type_cle_usb_id, id_article))
    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + id_article)

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article')
    mycursor = get_db().cursor()
    sql = '''SELECT * FROM cle_usb WHERE id_cle_usb = %s'''
    mycursor.execute(sql, (id_declinaison_article,))
    declinaison_article = mycursor.fetchone()
    sql = '''SELECT * FROM capacite'''
    mycursor.execute(sql)
    capacites = mycursor.fetchall()
    sql = '''SELECT * FROM type_cle_usb'''
    mycursor.execute(sql)
    types = mycursor.fetchall()
    return render_template('admin/article/edit_declinaison_article.html',
                           declinaison_article=declinaison_article,
                           capacites=capacites,
                           types=types)

@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    id_declinaison_article = request.form.get('id_declinaison_article','')
    id_article = request.form.get('id_article','')
    capacite_id = request.form.get('capacite_id','')
    type_cle_usb_id = request.form.get('type_cle_usb_id','')
    prix = request.form.get('prix','')
    mycursor = get_db().cursor()
    sql = '''UPDATE cle_usb SET capacite_id = %s, type_cle_usb_id = %s, prix_cle_usb = %s WHERE id_cle_usb = %s'''
    mycursor.execute(sql, (capacite_id, type_cle_usb_id, prix, id_declinaison_article))
    get_db().commit()
    message = u'declinaison_article modifié , id:' + str(id_declinaison_article) + '- capacite :' + str(capacite_id) + ' - type:' + str(type_cle_usb_id) + ' - prix:' + str(prix)
    flash(message, 'alert-success')
    return redirect('/admin/article/edit?id_article=' + str(id_article))

@admin_declinaison_article.route('/admin/declinaison_article/delete', methods=['GET'])
def admin_delete_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article','')
    id_article = request.args.get('id_article','')
    mycursor = get_db().cursor()
    sql = '''DELETE FROM cle_usb WHERE id_cle_usb = %s'''
    mycursor.execute(sql, (id_declinaison_article,))
    get_db().commit()
    flash(u'declinaison supprimée, id_declinaison_article : ' + str(id_declinaison_article),  'alert-success')
    return redirect('/admin/article/edit?id_article=' + str(id_article))