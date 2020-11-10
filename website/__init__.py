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
    '''Simple redirect to a complete URL'''
    return render_template('01.1.redirect.html')


@app.route('/redirect_http_partial')
def redirect_http_partial():
    '''Redirect to redirect_http (path only, no slash)'''
    return render_template('01.2.redirect.html')


@app.route('/redirect_http_partial_no_scheme')
def redirect_http_partial_no_scheme():
    '''Redirect to full URL, but without the schema  (will use the same schema as the originator)'''
    return render_template('01.4.redirect.html')


@app.route('/subdir/redirect_http_partial_no_slash')
def redirect_http_partial_no_slash():
    '''Redirect to redirect_http_partial_no_slash_dest (partial path)'''
    return render_template('01.5.redirect.html')


@app.route('/subdir/redirect_http_partial_no_slash_dest')
def redirect_http_partial_no_slash_dest():
    '''Renders the same page as redirect_http, redirect to full URL'''
    return render_template('01.1.redirect.html')


@app.route('/subdir/redirect_http_path')
def redirect_http_path():
    '''Redirect to ../redirect_http (full path)'''
    return render_template('01.3.redirect.html')


@app.route('/redirect_js_loc')
def redirect_js_loc():
    '''Change window.location.href, full URL'''
    return render_template('02.1.redirect.html')


@app.route('/redirect_js_loc_replace')
def redirect_js_loc_replace():
    '''Use window.location.replace, with timer and full URL'''
    return render_template('02.2.redirect.html')


@app.route('/redirect_js_loc_assign')
def redirect_js_loc_assign():
    '''Use window.location.assign, with timer and full URL'''
    return render_template('02.3.redirect.html')


@app.route('/redirect_js_obfs')
def redirect_js_obfs():
    '''Obfuscated JS call, full URL'''
    return render_template('02.4.redirect.html')
