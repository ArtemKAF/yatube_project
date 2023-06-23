[![Actions status](https://github.com/ArtemKAF/yatube_project/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/ArtemKAF/yatube_project/actions/workflows/python-app.yml)
# yatube
### Описание
Социальная сеть для публикации личных дневников
### Технологии
- Python 3.9.16
- Django 2.2.6
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
source ./venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- В папке с файлом manage.py проведите миграции:
```
python manage.py makemigrations
python manage.py migrate
```
- Cоздайте суперпользователя:
```
python manage.py createsuperuser
```
- Запустите Django-сервер командой:
```
python manage.py runserver --insecure
```
### License
MIT
### Авторы
Козин Артем