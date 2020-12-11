#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import ipaddress
import uuid

from ip2geotools.databases.noncommercial import DbIpCity

from flask import Flask, render_template, request, url_for, redirect, make_response, Response
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


@app.route('/url_parameter')
def url_parameter():
    '''Redirect based on url parameters'''
    args = request.args
    if 'blah' in args:
        # Redirect to self, parameters only
        resp = Response("Location header partial")
        resp.headers['Location'] = '?foo=bar'
        return make_response(resp, 302)
    elif 'foo' in args:
        # final redirect if blah was in the parameters
        return render_template('01.1.redirect.html')
    elif 'query_dest' in args:
        # called with meta http-equiv if there is a query parameter in the URL
        return render_template('01.1.redirect.html')
    return render_template('special.html', args=args)


@app.route('/frame')
def http_frame():
    '''Load a URL in a frame, no actual redirect'''
    return render_template('03.1.frame.html')


# JS redirects

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


@app.route('/redirect_js_partial')
def redirect_js_partial():
    '''Redirect with JS to partial URL'''
    return render_template('02.5.redirect.html')


@app.route('/subdir/redirect_js_partial_subdir')
def redirect_js_partial_subdir():
    '''Redirect with JS to partial URL, from subdit'''
    return render_template('02.6.redirect.html')


@app.route('/history_pushstate')
def history_pushstate():
    '''Use History.pushstate to block backing out, submit hidden form'''
    args = request.args
    if 'try_go_back' in args:
        return render_template('i_see_you.html')
    if 'refer' in args:
        return render_template('02.5.redirect.html')
    return render_template('04.1.hell.html')


@app.route('/stats')
def stats():
    return str(uuid.uuid4())


@app.route('/history_pushstate_landing')
def history_pushstate_landing():
    '''Use History.pushstate to trigger a redirect from hell'''
    return render_template('04.1.hell.html')


# server side stuff

@app.route('/server_side_redirect')
def server_side_redirect():
    '''Server side redirect'''
    return redirect(url_for('redirect_http'), 303)


@app.route('/missing')
def raise_404():
    '''Trigger a 404, but still redirect'''
    return make_response(render_template('01.1.redirect.html'), 404)


@app.route('/refresh_header')
def refresh_header():
    resp = Response("Refresh header")
    resp.headers['Refresh'] = '0; /redirect_http'
    return resp


@app.route('/location_header')
def location_header():
    resp = Response("Location header")
    resp.headers['Location'] = '/redirect_http'
    return make_response(resp, 302)


@app.route('/location_header_partial')
def location_header_partial():
    resp = Response("Location header partial")
    resp.headers['Location'] = 'url_parameter?blah=foo'
    return make_response(resp, 302)


@app.route('/user_agent')
def ua():
    ua = request.user_agent
    if ua.platform == 'android':
        return redirect('https://www.youtube.com/watch?v=z1APG3HjO4Q')
    elif ua.platform == 'linux':
        return redirect('https://www.youtube.com/watch?v=FDgEdcFTquM')
    elif ua.platform == 'windows':
        return redirect('https://www.youtube.com/watch?v=EHCRimwRGLs')
    elif ua.platform == 'iphone':
        return redirect('https://www.youtube.com/watch?v=M_Ccpl1Opew')
    elif ua.platform == 'macos':
        return redirect('https://www.youtube.com/watch?v=0NwkczSuwL8')
    else:
        return redirect('https://www.youtube.com/watch?v=I4bNg5MeCek')


@app.route('/ip')
def ip():
    '''Redirects to different places depending on the CC of the IP doing the request'''
    ip = ipaddress.ip_address(request.remote_addr)
    try:
        response = DbIpCity.get(ip, api_key='free')
        cc = response.country
    except Exception:
        cc = 'No Clue.'
    return render_template('ip.html', ip=ip, cc=cc)


@app.route('/cookie')
def cookie():
    '''Redirecting properly only if the cookie is right'''
    name = request.cookies.get('UserID')
    if name and name == 'Eduard' or name == 'Khil':
        return render_template('01.1.redirect.html')

    resp = Response("Nay")
    resp.headers['Location'] = 'https://en.wikipedia.org/wiki/Eduard_Khil'
    resp.headers['X-Cookie'] = 'UserID=???'
    return make_response(resp, 302)


@app.route('/referer')
def referer():
    '''Redirecting properly only if the referer is right'''
    referer = request.headers.get("Referer")
    if referer and referer == 'http://circl.lu':
        return render_template('01.1.redirect.html')
    resp = Response("Nay")
    resp.headers['Location'] = '//google.dk'
    resp.headers['X-Referer'] = 'Not circl.lu'
    return make_response(resp, 302)
