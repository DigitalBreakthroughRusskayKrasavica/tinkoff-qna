# Tinkoff QnA

## 🛠 Установка

### Локально

   1. Склонируйте проект и войдите в него
      ```
      git clone https://github.com/DigitalBreakthroughRusskayKrasavica/tinkoff-qna
      cd tinkoff-qna/backend
      ```
   
   2. Создайте и активируйте виртуальное окружение
       ```
       python -m venv venv
       source venv/bin/activate
       ```
   
   3. Установите зависимости в интерактивном режиме
      ```
      pip install -e .
      ```
      
   4. Переименуйте и заполните конфиги (app.example.toml -> app.toml)
   
   5. Примените миграции
      ```
      python -m alembic upgrade head
      ```
      
   6. Заполните базу данных данными из датасета
      ```
      python parse_to_db.py
      ```
      
   7. Запустите бота
      ```
      python -m tinkoff_qna.main.bot
      ```

   8. Запустите веб апи (в другом процессе)
      ```
      python -m tinkoff_qna.main.web
      ```

### via Docker

   1. Склонируйте проект и войдите в директорию с ним
      ```
      git clone https://github.com/DigitalBreakthroughRusskayKrasavica/tinkoff-qna
      cd tinkoff-qna/backend
      ```
   2. Переименуйте и заполните конфиги (app.docker.example.toml -> app.docker.toml, db.example.env -> db.env)
   
   3. Создайте докер образ
       ```
       docker build -f Dockerfile -t tinkoff-qna .
       ```
       
   4. Запустите компоус
       ```
       docker-compose up -d
       ```
      
   5. Создайте и активируйте виртуальное окружение
      ```
      python -m venv venv
      source venv/bin/activate
      ```
   
   6. Заполните базу данных данными из датасета
      ```
      pip install SQLAlchemy==2.0.23 && python parse_to_db.py
      ```

## 🧰 Tech Stack


### Web API

- [FastAPI](https://fastapi.tiangolo.com/) - Modern and fast python web-framework for building APIs;
- [Uvicorn](https://www.uvicorn.org/) - ASGI web server implemetation for python. 

### Telegram Bot

- [aiogram](https://aiogram.dev/) - Modern and fully asynchronous framework for Telegram Bot API;

### Backend/low-level part

- [Toml](https://pypi.org/project/toml/) - A library for parsing and serialising configs from toml files into python structures;
- [Pydantic](https://docs.pydantic.dev/latest/) - A most popular library for building validation rules;
- [SQLAlchemy](https://www.sqlalchemy.org/) - An ORM and SQL toolkit that provides easy database interaction from python;
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database migration tool for SQLAlchemy.

### Testing
- [Pytest](https://docs.pytest.org) - A python testing framework;
- [Unittest](https://docs.python.org/3/library/unittest.html) - A python builtin library for building unit tests

### Docs
- [SwaggerUI](https://github.com/swagger-api/swagger-ui) -  A tool for describing, visualizing and interaction with the API’s resources

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/DigitalBreakthroughRusskayKrasavica/tinkoff-qna/tags).

## Authors

> See the list of [contributors](https://github.com/DigitalBreakthroughRusskayKrasavica/tinkoff-qna/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details

