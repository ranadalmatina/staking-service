# staking-service
Fireblocks backend service


Staking-service is a Django (Python) app with a Postgres database.
The service can be run from docker using docker compose.
An Asynchronous task queue is implemented using Celery.

## Development Setup

1. Create a .env file in the root dir to hold environment vars. An example is included in the project.

```
cd staking-service
cp example.env .env
```

2. Build the docker containers

`docker compose -f local.yml build`

3. Initialise the database by running the database migrations

`docker compose -f local.yml run django python manage.py migrate`

4. (Optional) Setup username/password access the Django admin backend.

`docker compose -f local.yml run django python manage.py createsuperuser`

5. (Optional) Spin up the development server on port 8000.

`docker compose -f local.yml up`

5. Run the tests

`docker compose -f local.yml run django python manage.py test`


## Docs

* Django has amazing [documentation](https://docs.djangoproject.com/en/4.0/) and this project sticks closely to Django conventions.
* Avalanche RPC API [docs](https://docs.avax.network/apis/avalanchego/apis/c-chain/#avaxgetutxos).
* Avalanche transaction format [docs](https://docs.avax.network/specs/coreth-atomic-transaction-serialization)
* Fireblocks API [docs](https://docs.fireblocks.com/api/#exchangeasset)
