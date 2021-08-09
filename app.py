#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 12:17:54 2021

@author: ying
"""

from flask import Flask, render_template, request,flash, redirect, url_for
from werkzeug.utils import secure_filename
import os 
import json
from main_functions import make_prediction

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'stl','STL'}
#app.config['UPLOAD_EXTENSIONS'] = ['.stl', '.STL']
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template('main.html')

@app.route('/' , methods=['POST'])
def get_data():
    if request.method == 'POST':
        results =request.form
        file = request.files['stl_file']
        json_filename = file.filename.rsplit('.', 1)[0] + '.json'
        with open(json_filename,'w') as f:
            json.dump(results, f)
            
         # if user does not select file, browser also
         # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(filename)
            return redirect(url_for('prediction', filename=filename))     
        
    return render_template('main.html')

@app.route('/prediction/<filename>')
def prediction(filename):
    process_filename = filename.rsplit('.', 1)[0] + '.json'
    predictions = make_prediction(filename,process_filename)
    if predictions ==1:
        result = 'congratulations! You part is ready to print'
    else:
        result = 'You part need some modifications before you print it'
    
    return render_template('predict.html',result = result,filename=filename)


if __name__ == '__main__':

   app.run(debug=True)