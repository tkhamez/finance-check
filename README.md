# Finance Check

An application for EVE Online to read tax related information from corporation wallets.

## Requirements

- Python 3.12 (other versions may work, but are not tested)
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

Install (Ubuntu 24.04):
```
python3.12 -m venv .venv
. .venv/bin/activate
pip install pipenv
pipenv install
```

Environment variables for the web application:
- DB_HOST=127.0.0.1
- DB_PORT=3306 # optional
- DB_USER=finance_check
- DB_PASSWORD=123abc
- DB_DATABASE=finance_check
- EVE_APP_ID=
- EVE_APP_SECRET=
- EVE_APP_CALLBACK=https://your-domain.tld/auth/callback
- SECRET_KEY=a-secret-key # Used to encrypt the session cookie.
- API_BASE_URL=https://account.bravecollective.com/api
- API_KEY=123abc # base64 encoded id:secret
- API_EVE_LOGIN=finance # The Neucore EVE login name with the "wallet" scope.
- CHECK_ALLIANCES=99003214,99010079
- CHECK_CORPORATIONS=98614261
- LOGIN_CHARACTERS=96061222,98169165 # EVE character IDs that are allowed to log in
- Optional for dev env if HTTPS is not available: OAUTHLIB_INSECURE_TRANSPORT=1

Environment variables for the console application:
- All DB_*
- All API_*
- ALL_TYPES_CORPORATIONS= # Optionally, a comma separated list of corporation IDs.

## Run

### Dev

```
. .venv/bin/activate

export FLASK_ENV=development
export FLASK_APP=web/app:app

# export other env vars

flask run

python console/fetch-wallets.py
```

### Prod

See files in `config/` for a setup with systemd and nginx on Ubuntu 24.04.  
The server can also be temporarily started with:
```
# export env vars

.venv/bin/uwsgi --http 127.0.0.1:5000 --chdir web --module app:app
```

Set up a cronjob to run `python console/fetch-wallets.py` to fetch the data.

## Changes

2024-08-09
- Compatibility with Python 3.12.
- Player donations are now always stored and were added as a filter.
- Updated dependencies.

2023-08-10
- Fixed missing year_month value in table wallet_journal. Run the last SQL in [schema.sql](schema.sql) from
  2023-06-23 to add missing values.

2023-06-23
- Added wallet_journal.journal_year_month column, see [schema.sql](schema.sql).
- "Sum per month" now displays a maximum of 12 months, starting with the selected month.

2022-11-01
- Added ALL_TYPES_CORPORATIONS environment variable.

2022-10-07
- Added CHECK_ALLIANCES and CHECK_CORPORATIONS environment variables.

2022-07-07
- Added index to wallet_journal.amount.
