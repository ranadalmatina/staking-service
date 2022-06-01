# staking-service

Fireblocks backend service.

Staking-service is a Django (Python) app with a Postgres database.
The service can be run from docker using docker compose.
An Asynchronous task queue is implemented using Celery.

## Development Setup

1. Create a .env file in the root dir to hold environment vars. An example is included in the project:

```
cd staking-service
cp example.env .env
```

2. Install [Docker](https://docs.docker.com/desktop/), if needed, and launch it to install the command line tools.

3. Build the docker containers:
   `docker compose -f local.yml build`

4. Initialize the database by running the database migrations:
   `docker compose -f local.yml run django python manage.py migrate`

5. (Optional) Setup username/password access the Django admin backend:
   `docker compose -f local.yml run django python manage.py createsuperuser`

6. (Optional) Spin up the development server on port 8000:
   `docker compose -f local.yml up`

7. Run the tests:
   `docker compose -f local.yml run django python manage.py test`

## Docs

-   Django has amazing [documentation](https://docs.djangoproject.com/en/4.0/) and this project sticks closely to Django conventions.
-   Avalanche RPC API [docs](https://docs.avax.network/apis/avalanchego/apis/c-chain/#avaxgetutxos).
-   Avalanche transaction format [docs](https://docs.avax.network/specs/coreth-atomic-transaction-serialization).
-   Fireblocks API [docs](https://docs.fireblocks.com/api/#exchangeasset).

## Using vscode

Because the project runs in docker, your local machine will not have the libraries installed for vscode to provide
errors / linting / autocomplete. To fix that, you can create an local virtual environment and install the requirements there.

To get VSCode to recognise it, you may have to do `ctrl + shift + p > Python: create terminal`. Then, in that terminal:

1. Ensure you're in the `staking-service` folder.
1. If you don't have it already: `python3 -m pip install --user virtualenv`
1. `python3 -m venv env`
1. `source env/bin/activate`
1. `pip install -r requirements/requirements.txt`

The language server should now be working. You can use `deactivate` to get out of the virtual env.
