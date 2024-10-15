# pages/db_home.py
from flask import render_template, request, redirect, url_for, session

class DbHome:
    route = '/'
    methods = ['GET', 'POST']
    endpoint_name = 'db_home'

    # def __init__(self, web_app):
    #     self.web_app = web_app

    def view_func(self):
        if request.method == 'POST':
            server_type = request.form.get('server_type')
            action=request.form.get('action')
            session['server_type']=server_type
            session['action']=action
            if server_type == 'gdrive': 
                return redirect(url_for('google_drive')) 
            if server_type == 'lab':
                return redirect(url_for('lab_connect'))
            #add more servers here

        return render_template('db_home.html')

