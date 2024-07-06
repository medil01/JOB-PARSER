### 1. Job Parser

```markdown
Проект предназначен для парсинга данных о вакансиях с сайтов hh.ru, avito.ru и career.habr.com, их загрузки в базу данных и предоставления телеграм-бота для поиска по этой базе данных.

Требования

- Docker
- Docker Compose
- Python 3.9+
```

### 2. Установка Python-зависимостей

Создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv venv
source venv/bin/activate   # для Linux/Mac
venv\Scripts\activate      # для Windows
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных

Docker Compose автоматически настроит и запустит MySQL базу данных.

### 4. Запуск через Docker Compose

Создайте файл `docker-compose.yml` со следующим содержимым:

```yaml
version: '3'

services:
  db:
    image: mysql:5.7
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: job_database
      MYSQL_USER: your_user
      MYSQL_PASSWORD: your_password
    ports:
      - "3306:3306"
  
  parser:
    build:
      context: .
      dockerfile: Dockerfile.parser
    depends_on:
      - db

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    depends_on:
      - db
```

Создайте файл `Dockerfile.parser` со следующим содержимым:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "parser.py"]
```

Создайте файл `Dockerfile.bot` со следующим содержимым:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### 5. Запуск системы

Запустите систему с помощью Docker Compose:

```bash
docker-compose up --build
```

### 6. Проверка состояния контейнеров

Чтобы убедиться, что все контейнеры запущены и работают корректно, выполните:

```bash
docker-compose ps
```

## Использование

### Парсинг вакансий

Запустите скрипт `parser.py`, который автоматически парсит вакансии с сайтов hh.ru, avito.ru и career.habr.com и сохраняет их в базу данных.

### Телеграм-бот

Запустите скрипт `bot.py`, который запустит телеграм-бота для поиска по базе данных вакансий.
