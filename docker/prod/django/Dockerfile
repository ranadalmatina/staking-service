ARG PYTHON_VERSION=3.10.4-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements

# Upgrade to latest pip and install production requirements
RUN pip install --upgrade pip
RUN pip install -r /requirements/requirements_prod.txt

# Copy all Django code to the /app dir
COPY ./ss /app

COPY ./docker/prod/django/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh

COPY ./docker/prod/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/gunicorn.sh"]
