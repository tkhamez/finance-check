# finance-check

Reads tax information from corporation wallets.

## Requirements

- Python 3.8 (other versions may work, but are not tested)
- A MySQL or MariaDB database
- A Neucore installation - https://github.com/tkhamez/neucore

## Setup

Create an EVE app at https://developers.eveonline.com with callback: 
`https://your.domain.tld/auth/callback`.

Add a Neucore EVE Login:
- Scopes: `esi-wallet.read_corporation_wallets.v1 esi-characters.read_corporation_roles.v1`
- Roles: Accountant

Add a Neucore app:
- Roles: app-esi
- EVE Logins: The login from above

Create a database and add the tables from `schema.sql`.

Insert corporations those wallets should be read, e.g.:
```sql
INSERT INTO corporations (id, corporation_name, character_id) VALUES (98169165, 'BNI', 92888420);
```
The name does not matter, it's only used in the UI.  
The character must have an ESI token on Neucore for the EVE login configured with the environment variable 
API_EVE_LOGIN.

Environment variables:
- SECRET_KEY=a-secret-key # Used to encrypt the session cookie.
- API_BASE_URL=https://account.bravecollective.com/api
- API_KEY=123abc # base64 encoded id:secret
- API_EVE_LOGIN=finance # The Neucore EVE login name with the "wallet" scope.
- DB_HOST=127.0.0.1
- DB_PORT=3306 # optional
- DB_USER=finance_check
- DB_PASSWORD=123abc
- DB_DATABASE=finance_check
- EVE_APP_ID=
- EVE_APP_SECRET=
- EVE_APP_CALLBACK=https://your-domain.tld/auth/callback
- LOGIN_CHARACTERS=96061222,98169165 # EVE character IDs that are allowed to log in
- Optional for dev env if HTTPS is not available: OAUTHLIB_INSECURE_TRANSPORT=1

## Run

Install:
```
sudo apt-get install python3-venv python3-dev
python3 -m venv venv
. venv/bin/activate
pip install wheel
pip install -r requirements.txt
```

Dev:
```
. venv/bin/activate

export FLASK_ENV=development
export FLASK_APP=web/app:app

# export other env vars

flask run

python console/fetch-wallets.py
```

Prod:  
See files in `config/` for a setup with systemd and nginx on Ubuntu 20.04.  
The server can also be temporarily started with:
```
uwsgi --http 127.0.0.1:5000 --chdir web --module app:app
```

## Changes

2022-07-07

- Added index to wallet_journal.amount.
