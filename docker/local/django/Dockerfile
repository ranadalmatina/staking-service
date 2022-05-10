ARG PYTHON_VERSION=3.10.4-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONUNBUFFERED 1

# Upgrade to latest pip
RUN pip install --upgrade pip

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

RUN pip install -r /requirements/requirements_dev.txt

COPY ./docker/prod/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
