FROM python:3.9-alpine

COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install -r /usr/src/requirements.txt

RUN mkdir /usr/src/yatube_project/
WORKDIR /usr/src/yatube_project/
COPY . /usr/src/yatube_project/

EXPOSE 8000

WORKDIR /usr/src/yatube_project/yatube/
CMD python manage.py makemigrations ; python manage.py migrate ; python manage.py runserver 0.0.0.0:8000 --insecure
