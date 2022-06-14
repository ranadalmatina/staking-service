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

## Contract Interaction

### Local

1. Deploy the [staking](https://github.com/ranaventures/staking) contracts using `scripts/deploy.sh`.

2. Update your `.env` with the deployed contract addresses:

```
DJANGO_SETTINGS_MODULE=ss.settings.local
CONTRACT_STAKING=0x...
CONTRACT_ORACLE=0x...
```

3. Run your command (e.g. `read_state`):
   `docker compose -f local.yml run django python manage.py read_state`

### Fuji

As above, but use `DJANGO_SETTINGS_MODULE=ss.settings.fuji` in your `.env`.

## Using Invoke tasks

There is a `tasks` directory that contains [Invoke](https://www.pyinvoke.org/) tasks which allow automation of various parts of the project.
Anything that can be written in Python or run in the shell can be automated with Invoke.

Reading through some of these tasks will also give examples of how to perform common actions in the project.

### Getting setup to use Invoke

Many of these tasks run externally to the project hence it is usually best to setup Invoke in a separate venv.

1. Create a new venv or use the default
2. `pip install -r requirements/tools.txt`
3. `pip install -r requirements/requirements_tools.txt`

This will install the `inv` command on your system. You can run `inv --list` to see all available invoke tasks.
Note you need to be in the top level directory of the project. Invoke looks for a folder called `tasks`.

### Linting + Security

Run the full suite of linting checks and security checks with `inv check` or run just one check
e.g. isort using `inv check.isort`

## Docs

- Django has amazing [documentation](https://docs.djangoproject.com/en/4.0/) and this project sticks closely to Django conventions.
- Avalanche RPC API [docs](https://docs.avax.network/apis/avalanchego/apis/c-chain/#avaxgetutxos).
- Avalanche transaction format [docs](https://docs.avax.network/specs/coreth-atomic-transaction-serialization).
- Fireblocks API [docs](https://docs.fireblocks.com/api/#exchangeasset).

## Using vscode

Because the project runs in docker, your local machine will not have the libraries installed for vscode to provide
errors / linting / autocomplete. To fix that, you can create an local virtual environment and install the requirements there.

To get VSCode to recognise it, you may have to do `ctrl + shift + p > Python: create terminal`. Then, in that terminal:

1. Ensure you're in the `staking-service` folder.
2. If you don't have it already: `python3 -m pip install --user virtualenv`
3. `python3 -m venv env`
4. `source env/bin/activate`
5. `pip install -r requirements/requirements.txt`

The language server should now be working. You can use `deactivate` to get out of the virtual env.

## Using PyCharm

You do not need to set up a separate venv, you can point PyCharm at your docker container
and it will find the correct versions of all libraries, Python etc 
