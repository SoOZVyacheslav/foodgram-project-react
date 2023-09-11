# Проект «Продуктовый помощник» - Foodgram 
Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 
### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Workflow

### Скриншоты страниц:

- Можно посмотерть [здесь](../master/backend/data/screenshots)

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
git@github.com:SoOZVyacheslav/foodgram-project-react.git
```

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

- Скопировать на сервер файлы docker-compose.production.yml, nginx.conf или создайте на сервере docker-compose.yml:


- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение
```
- Создать файл .env на сервере:
```
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY=....
DEBUG=FALSE
ALLOWED_HOSTS=localhost,backend,127.0.0.1,вашь_ип,вашь_домен
```
- Создать и запустить контейнеры Docker, выполнить команду на сервере в зависимости от docker-compose.yml или docker-compose.production.yml:
```
sudo docker compose -f docker-compose.production.yml up -d

или

sudo docker compose up -d

# Далее будит указываться одна команда
```
- После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```

- Наполнить базу данных:
```
sudo docker compose exec backend python manage.py import_csv
```

- Для остановки контейнеров Docker:
```
sudo docker compose down     # с их удалением
sudo docker compose stop     # без удаления
```

### После каждого обновления репозитория будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Запуск проекта на локальной машине:

- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```
docker compose up -d # из папки infra
```


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)
# Сайт, пока доступен тут: 
``` 
https://foodgram2023.sytes.net/
``` 
### Автор
[Вячеслав Костырка](http://github.com/SoOZVyacheslav)
