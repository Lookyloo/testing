#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap  # type: ignore

from .helpers import get_homedir
from .proxied import ReverseProxied


app: Flask = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)  # type: ignore

secret_file_path: Path = get_homedir() / 'secret_key'
if not secret_file_path.exists() or secret_file_path.stat().st_size < 64:
    with secret_file_path.open('wb') as f:
        f.write(os.urandom(64))

with secret_file_path.open('rb') as f:
    app.config['SECRET_KEY'] = f.read()

Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SESSION_COOKIE_NAME'] = 'lookyloo-testing'

app.debug = False


@app.route('/', methods=['GET'])
def index():
    if request.method == 'HEAD':
        # Just returns ack if the webserver is running
        return 'Ack'
    return render_template('index.html')


@app.route('/redirect_http')
def redirect_http():
    return render_template('01.1.redirect.html')


@app.route('/redirect_http_partial')
def redirect_http_partial():
    return render_template('01.2.redirect.html')


@app.route('/subdir/redirect_http_path')
def redirect_http_path():
    return render_template('01.3.redirect.html')


@app.route('/redirect_js_loc')
def redirect_js_loc():
    return render_template('02.1.redirect.html')


@app.route('/redirect_js_loc_replace')
def redirect_js_loc_replace():
    return render_template('02.2.redirect.html')


@app.route('/redirect_js_loc_assign')
def redirect_js_loc_assign():
    return render_template('02.3.redirect.html')


@app.route('/redirect_js_obfs')
def redirect_js_obfs():
    return render_template('02.4.redirect.html')
