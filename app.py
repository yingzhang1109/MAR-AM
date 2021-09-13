#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 12:17:54 2021

@author: ying
"""

from flask import Flask, render_template, request,flash, redirect, url_for
from werkzeug.utils import secure_filename
import json
from main_functions import make_prediction
from recommender import recommender
import os

app = Flask(__name__)
print(os.path.join(app.root_path, 'static/saved/'))
path = app.root_path+'/static/saved/'
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
            file.save(os.path.join(app.root_path, 'static/saved/'+filename))
            return redirect(url_for('prediction', filename=filename))     
        
    return render_template('main.html')

@app.route('/prediction/<filename>')
def prediction(filename):
    process_filename = filename.rsplit('.', 1)[0] + '.json'
    predictions = make_prediction(path+filename,process_filename)
    if predictions ==1:
        result = 'Congratulations! Your part is ready to print'
        suggestion = ''
        new_filename = filename
    else:
        result = 'Your part needs some modifications before you print it'
        #suggestion = 'Recommendations: Try different build orientation as the viewer shows'
        #suggestion = 'Recommendations: Try PLA'
        suggestion,new_filename = recommender(path+filename,process_filename)
        #new_filename = filename
    return render_template('predict.html',result = result,filename=new_filename, suggestion = suggestion)


if __name__ == '__main__':

   app.run(debug=True)
