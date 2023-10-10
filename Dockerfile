FROM python:3.9-slim

RUN apt-get update \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install --upgrade pip --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

COPY ./yatube ./yatube/

EXPOSE 8000

WORKDIR ./yatube/
CMD python manage.py migrate ; python manage.py runserver 0.0.0.0:8000 --insecure
