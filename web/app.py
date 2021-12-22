import os
from typing import Union

from flask import Flask, Response

from pages.Auth import Auth
from pages.Index import Index


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index() -> Union[str, Response]:
    return Index().show()


@app.route('/auth/login')
def auth_login() -> str:
    return Auth.login()


@app.route('/auth/redirect')
def auth_redirect() -> Response:
    return Auth().redirect()


@app.route('/auth/callback')
def auth_callback() -> Response:
    return Auth().callback()


@app.route('/auth/logout')
def auth_logout() -> Response:
    return Auth.logout()
