#!/usr/bin/python3
from flask import Flask, request, render_template, send_from_directory
from random import *
import os, requests
from database import getTabellen, getTabelleFürFlask

app = Flask(__name__)
app.config.update(
        TEMPLATES_AUTO_RELOAD = True
)

@app.route('/', methods=['GET'])
def index():
    return 'Flask von ralf_schneider'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
               'favicon.ico', mimetype='public/img/Streichholz.png')

@app.route('/hello/')
@app.route('/hello/<erwin>')
def hello(erwin=None):
    return render_template('hello.html', name=erwin)

@app.route('/parameter', methods=['GET', 'POST'])
def parameter():
    getwerte=request.args
    postwerte=request.form
    return render_template('parameter.html', g=getwerte, p=postwerte)

@app.route('/nim/')
@app.route('/nim')
def nimstart():
    zahl = randint(10, 20)
    return render_template('nimm/niminit.html', zahl=zahl)

@app.route('/nim/<int:noch>')
def nimfirst(noch):
    return render_template('nimm/nimfirst.html', noch=noch)

@app.route('/nimrun/<int:noch_beginn>')
def nimmain(noch_beginn):
    pcnimmt = noch_beginn % 4
    if pcnimmt == 0:
        pcnimmt = randint(1,3)
    noch = noch_beginn-pcnimmt
    return render_template('nimm/nimrun.html', noch_beginn=noch_beginn, noch=noch, pcnimmt=pcnimmt)


@app.route('/nimm2')
@app.route('/nimm2/')
def nimm2start():
    zahl = randint(10, 20)
    return render_template('nimm2/nimm2init.html', noch=zahl)

@app.route('/nimm2run', methods=['GET', 'POST'])
def nimm2run():
    get = request.args
    post = request.form
    args = {'beginn' : int(get['noch'])} #Noch wird als Integer gecastet
    if(len(post) == 0):
        return render_template('nimm2/nimm2first.html', noch=args['beginn'])
    else:
        args['genommen'] = int(post['genommen'])
        args['beginn'] -= args['genommen'] #Genommene Steine werden verrechnet
        pcnimmt = args['beginn'] % 4 #Pc nimmt Steine
        if pcnimmt == 0:
            pcnimmt = randint(1,3)
        args['pcnimmt'] = pcnimmt
        args['noch'] = args['beginn'] - pcnimmt
        return render_template('nimm2/nimm2run.html', args=args)


@app.route('/database')
@app.route('/database/')
def database():
    return render_template('database/database.html', tabellen=getTabellen())
    

@app.route('/database/<table>')
def showDatabase(table):
    return render_template('database/showdatabase.html', tablename=table, table=getTabelleFürFlask(table))

# Nur damit zu Hause flask auch alleine laufen kann.
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)