[![CI](https://github.com/CrowMEV/gsd-games-back/actions/workflows/actions.yaml/badge.svg)](https://github.com/CrowMEV/gsd-games-back/actions/workflows/actions.yaml)
# GSD-games

## Настройка проекта

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -r requirements.txt
poetry install
```

### Установка pre-commit hooks

Установка хуков

```bash
pre-commit install
```

Для того чтобы прогнать `pre-commit` до выполнения коммита

```bash
pre-commit run --all-files
```

### Запуск БД проекта

Для запуска docker compose базой данных нужно создать файл .env с переменными:

```
COMPOSE_FILE=""
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
```

### Запуск проекта

Для запуска docker compose пректа нужно создать файл .env с переменными:

```
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DOCS_URL=""
REDOC_URL=""
DEBUG=true/false
PYTHONPATH=./example
SECRET_KEY=""
ALGORITHM=""
ACCESS_TOKEN_EXPIRE_MINUTES=0
```

### Команды для docker compose

```bash
docker compose up --build -d
docker compose down -v
docker compose exec имя_контейнера psql -U имя_пользователя имя_бд

```

### Запуск тестов

```bash
pytest
```

### Документация:

- [Swagger](http://127.0.0.1:8000/docs)
- [Redoc](http://127.0.0.1:8000/redoc)
