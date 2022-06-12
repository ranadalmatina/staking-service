from invoke import task

@task
def security(c):
    c.run('safety check -r requirements/requirements_prod.txt')


@task
def isort(c):
    c.run('isort ss/')
    c.run('isort tasks/')


@task
def flake8(c):
    c.run('flake8 ss/')
    c.run('flake8 tasks/')


@task(default=True)
def all(c):
    isort(c)
    security(c)
    flake8(c)
