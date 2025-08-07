# FOODGRAM

https://yafoodgram.hopto.org/recipes

Сервис для обмена рецептами. Пользователи могут публиковать свои рецепты, добавлять чужие  в избранное и подписываться на публикации других авторов. Рецепты можно скачать, а продукты для понравившегося блюда добавить в список покупок.

Основные возможности:
- Создание и публикация рецептов с описанием ингредиентов, этапов приготовления и фотографиями.
- Редактирование рецептов.
- Добавление рецептов в Избранное
- Добавление ингредиентов в Список покупок.
- Скачивание списка покупок.
- Подписка на других пользователей.
- Регистрация и аутентификация.

## Содержание
- [Технологии](#технологии)
- [Запуск](#запуск)
- [Автор](#автор)

## Технологии
- Язык программирования: Python 3.9
- Веб-фреймворк: Django
- REST API: Django REST Framework
- Аутентификация: Djoser
- База данных: PostgreSQL
- Обработка изображений: Pillow
- Тестирование: flake8
- Развертывание: Gunicorn, Nginx, Docker
- Конфигурация: PyYAML

## Запуск
1. **Клонируйте репозиторий**:

```bash
git clone git@github.com:ValeryRabchenyuk/foodgram.git
cd foodgram
```

2. **Добавьте обязательные переменные окружения**

Подставьте свои значения переменных.

```bash
echo 'POSTGRES_DB=django' >> .env
echo 'POSTGRES_USER=django_user' >> .env
echo 'POSTGRES_PASSWORD=mysecretpassword' >> .env
echo 'DB_HOST=db' >> .env
echo 'DB_PORT=5432' >> .env
echo 'SECRET_KEY=secret_key' >> .env
echo 'DEBUG=False' >> .env
echo 'ALLOWED_HOSTS=127.0.0.1,localhost' >> .env
echo 'SQLITE=False' >> .env
```

3. **Создайте и активируйте виртуальное окружение**

```bash
cd backend/
py -3.9 -m venv venv
source venv/Scripts/activate
```

4. **Установите зависимости и выполните миграции:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
```

5. **Заполните базу тестовыми данными об ингредиентах и тегами:**

```bash
   python manage.py load_db
   python manage.py load_db_tags
```

6. **Создайте супер пользователя и запустите локальный сервер:**

```bash
python manage.py createsuperuser
python manage.py runserver
```

7. **Доступ к документации:**
```bash
cd ../infra
docker compose up -d
```

9. **Сервис готов** 

[Бэкэнд](http://localhost:8080)
[Фронтэнд](http://localhost:80)
[Redoc](http://localhost/api/docs/)

#### Запуск приложения на удалённом сервере

1. **Выполните вход на удаленный сервер**
2. **Установите Docker и docker-compose:**

```bash
   sudo apt install docker.io
   sudo apt install docker-compose     
```
3. **Скопируйте содержимое файла `docker-compose.production.yml` на сервер**
4. **Настройте nginx**
5. **Добавьте переменные окружения**
```bash
DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_PASSWORD=<пароль DockerHub>

USER=<username для подключения к удаленному серверу>
HOST=<ip сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<id вашего Телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```

#### Для установки и запуска проекта, необходим [NodeJS](https://nodejs.org/) v8+.

## Автор
Рабченюк Валерия
