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
- Python
- PostgreSQL
- Django
- Drango REST Framework
- Node Package Manager
- Docker
- Nginx/Gunicorn

## Запуск
Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения на Mac или Linux:

```bash
   python3 -m venv env
   source env/bin/activate
```

Команда для Windows:

```bash
   python -m venv venv
   source venv/Scripts/activate
```

- Перейти в директорию infra и выполнить команду для доступа к документации:

```bash
   docker-compose up 
```

Установить зависимости и выполнить миграции:

```bash
   pip install -r requirements.txt
```

```bash
   python manage.py migrate
```

Заполнить базу тестовыми данными об ингредиентах и тегами:

```bash
   python manage.py load_db
   python manage.py load_db_tags
```

Создать суперпользователя, если необходимо:

```bash
python manage.py createsuperuser
```

- Запустить локальный сервер:

```bash
   python manage.py runserver
```

#### Запуск на удалённом сервере

- Выполнить вход на удаленный сервер
- Установить docker:

```bash
   sudo apt install docker.io
   ```

- Установить docker-compose:

``` bash
    sudo apt install docker-compose     
```
- Скопировать содержимое файла `docker-compose.production.yml` на сервер.
- Настроить nginx

- Добавить в Secrets репозитория на GitHub переменные окружения:

Переменные PostgreSQL, ключ проекта Django и их значения по-умолчанию можно взять из файла .env.example, затем установить свои.

DOCKER_USERNAME=<имя пользователя DockerHub>
DOCKER_PASSWORD=<пароль DockerHub>

USER=<username для подключения к удаленному серверу>
HOST=<ip сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<id вашего Телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>


#### Для установки и запуска проекта, необходим [NodeJS](https://nodejs.org/) v8+.

## Автор
Рабченюк Валерия
