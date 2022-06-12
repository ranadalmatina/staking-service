from invoke import task


@task
def down(c):
    c.run('docker compose -f local.yml down')


@task(default=True)
def up(c):
    c.run('docker compose -f local.yml up', pty=True)


@task
def drop_db(c):
    down(c)
    result = c.run('docker volume ls | grep staking-service_postgres_data_local', warn=True)
    if result.ok:
        c.run('docker volume rm staking-service_postgres_data_local')


@task
def build(c, clean=False, no_cache=False):
    down(c)
    cmd = 'docker compose -f local.yml build'
    if clean or no_cache:
        cmd += ' --no-cache'
    c.run(cmd)


@task
def migrate(c):
    """
    Migrate local Docker database.
    """
    c.run('docker compose -f local.yml run django python manage.py migrate', pty=True)


@task
def test(c):
    """
    Run all tests.
    """
    c.run('docker compose -f local.yml run django python manage.py test', pty=True)


@task
def psql(c):
    # We need to supply user and password here too to connect to local postgres instance
    c.run('docker compose -f local.yml run postgres psql -h postgres', pty=True)
