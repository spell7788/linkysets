ARG PYTHON_IMAGE_TAG=3.8-alpine

FROM python:$PYTHON_IMAGE_TAG AS common

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR false

RUN pip install --upgrade pip && pip install pipenv

WORKDIR /app

COPY . .


# ---
FROM common AS dev

RUN pipenv install --deploy --system --dev

EXPOSE 8000

WORKDIR /app

# nostatic to enable whitenoise for serving files
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000", "--nostatic" ]


# ---
FROM common AS prod

RUN pipenv install --deploy --system

WORKDIR /app

CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
