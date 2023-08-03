from flask import render_template, session, flash, redirect, request, Flask, url_for
from app import db, app
from app.forms import LoginForm, RegistrationForm, StatsForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import pymysql
import sys
import warnings
import csi3335 as cfig
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from werkzeug.utils import secure_filename
import os



# need to add this packege.
# from flask_moment import Moment

#con = pymysql.connect(host=cfig.con['host'], user=cfig.con['user'], password=cfig.con['password'],
                      #database=cfig.con['database'])
#cur = con.cursor()


@app.route('/')
def root():
    return redirect(url_for('tool'))

@app.route('/index')
def index():
    return render_template("index.html", title='Home Page')
@app.route('/tool')
def tool():
    message = request.args.get('message', None)
    return render_template("tool.html", title='tool', message=message)

app.config['SESSION_TYPE'] = 'filesystem'
@app.route('/chose_the_organ', methods=['GET', 'POST'])
def chose_the_organ():
    if request.method == 'POST':
        organ = request.form.get('selectedOrgan')
        session['selectedOrgan'] = organ
        if request.form.get('action') == 'updateData':
            return redirect(url_for('file'))
        else:
            return redirect(url_for('form'))
    return render_template("chose.html", title='organ select')

@app.route('/form')
def form():
    uploaded_files = session.get('uploaded_files')
  
    # prossisng the file will go over here it is now not there as we delete it so that we can 
    # solve the runtime problem that we are facing, as it is taking more than 2 mints to run the
    # file and we are trying diffrent way to make it run faster.

    if uploaded_files:
        return render_template('form.html', uploaded_files=uploaded_files, title='Data Results')
    else:
        return 'No files uploaded.'

@app.route('/file', methods=['GET', 'POST'])
def file():
    if request.method == 'POST':
        file1 = request.files['fileUpload1']
        file2 = request.files['fileUpload2']
        file3 = request.files['fileUpload3']

        if file1 and file2 and file3:
            filename1 = secure_filename(file1.filename)
            filename2 = secure_filename(file2.filename)
            filename3 = secure_filename(file3.filename)

            file_path1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
            file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
            file_path3 = os.path.join(app.config['UPLOAD_FOLDER'], filename3)

            file1.save(file_path1)
            file2.save(file_path2)
            file3.save(file_path3)

            session['uploaded_files'] = [filename1, filename2, filename3]

            return redirect(url_for('form'))

    return render_template("file.html", title='File Select')


