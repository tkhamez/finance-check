import os

import requests
from flask import render_template, session, redirect, url_for, Response, request
# noinspection PyPackageRequirements
from jose import jwt
# noinspection PyPackageRequirements
from jose.exceptions import JWTClaimsError
from requests_oauthlib import OAuth2Session


class Auth:
    def __init__(self):
        self.__client_id = os.getenv('EVE_APP_ID')
        self.__client_secret = os.getenv('EVE_APP_SECRET')
        self.__redirect_uri = os.getenv('EVE_APP_CALLBACK')
        self.__allowed_characters = os.getenv('LOGIN_CHARACTERS').split(',')
        self.__authorization_base_url = 'https://login.eveonline.com/v2/oauth/authorize'
        self.__token_url = 'https://login.eveonline.com/v2/oauth/token'
        self.__jwk_set_url = 'https://login.eveonline.com/oauth/jwks'

    @staticmethod
    def login() -> str:
        return render_template('auth_login.html')

    def redirect(self) -> Response:
        oauth = OAuth2Session(self.__client_id, redirect_uri=self.__redirect_uri)
        authorization_url, state = oauth.authorization_url(self.__authorization_base_url)
        session['oauth_state'] = state
        return redirect(authorization_url)

    def callback(self) -> Response:
        if 'oauth_state' not in session:
            return redirect(url_for('index'))

        oauth = OAuth2Session(self.__client_id, state=session['oauth_state'])
        token = oauth.fetch_token(self.__token_url, client_secret=self.__client_secret,
                                  authorization_response=request.url)

        character_id = self.__validate_eve_jwt(token['access_token'])
        if character_id in self.__allowed_characters:
            session['character_id'] = int(character_id)

        return redirect(url_for('index'))

    @staticmethod
    def logout() -> Response:
        session.pop('character_id', None)
        return redirect(url_for('index'))

    def __validate_eve_jwt(self, access_token: str) -> str:
        res = requests.get(self.__jwk_set_url)
        data = res.json()
        jwk_sets = data["keys"]
        jwk_set = next((item for item in jwk_sets if item["alg"] == "RS256"))

        # https://github.com/ccpgames/sso-issues/issues/41
        # try login.eveonline.com and https://login.eveonline.com
        try:
            data = jwt.decode(
                access_token,
                jwk_set,
                algorithms=jwk_set["alg"],
                issuer="login.eveonline.com",
                options={"verify_aud": False}
            )
        except JWTClaimsError:
            data = jwt.decode(
                access_token,
                jwk_set,
                algorithms=jwk_set["alg"],
                issuer="https://login.eveonline.com",
                options={"verify_aud": False}
            )

        return data['sub'].replace('CHARACTER:EVE:', '')
