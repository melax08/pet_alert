# Pet Alert - веб-приложение для поиска пропавших животных

![petalert workflow](https://github.com/melax08/pet_alert/actions/workflows/petalert-workflow.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[//]: # (Посмотреть по баджу с coverage)

## Описание проекта

Проект создан с целью помощи людям в нахождении потерянных питомцев.
Хозяин потерянной зверюшки может создать объявление на сайте, предоставив всю необходимую информацию о случившейся ситуации.
Человек, который нашел на улице чужого питомца, может также сообщить об этом.

### Преимущества проекта

- **Удобство**: пользователю достаточно заполнить простую форму на сайте, чтобы сообщить о найденной или потерянной зверюшке.
- **Функциональность**: благодаря интеграции в проект `Яндекс карт`, пользователь может выбрать место, где был найден или потерян питомец.
- **Простота**: пользователю не нужно заранее регистрироваться на сайте, он будет зарегистрирован в момент создания своего первого объявления.
- **Возможности для коммуникации**: в проекте создана система диалогов, которая позволяет пользователям переписываться в рамках объявлений.
- **Приватность**: пользователи могут настраивать видимость своих контактных данных (email, мобильный телефон), если они не хотят делиться телефоном или почтой - то останется возможность коммуникации прямо на сайте, через диалоги.


### Используемый стек

[![Python][Python-badge]][Python-url]
[![Django][Django-badge]][Django-url]
[![DRF][DRF-badge]][DRF-url]
[![Postgres][Postgres-badge]][Postgres-url]
[![Nginx][Nginx-badge]][Nginx-url]
[![Poetry][Poetry-badge]][Poetry-url]
[![Docker][Docker-badge]][Docker-url]

### Системные требования

- Python 3.11+;
- Docker (19.03.0+) c docker compose;
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).

### Архитектура проекта

| Директория            | Описание                                              |
|-----------------------|-------------------------------------------------------|
| `infra`               | Docker-compose файл, конфиги Nginx                    |
| `src/pet_alert`       | Django приложение                                     |
| `src/pet_alert/ads`   | Основное приложение Django                            |
| `src/pet_alert/api`   | Django REST Framework API                             |
| `src/pet_alert/users` | Приложение для работы с пользователями                |
| `src/pet_alert/core`  | Контекст процессоры, фильтры шаблонов, общие сущности |


### Функциональные цели

<details>
  <summary>Нажмите, чтобы развернуть</summary>
  <br>

- [x] MVP проекта
- [x] Возможность создавать объявления
- [x] Просмотр объявлений списком и по карте
- [x] Фильтрация объявлений по видам питомцев
- [x] Система регистрации с подтверждением через почту
- [x] Система скрытой регистрации при создании объявления для гостя
- [x] Смена пароля, сброс пароля, авторизация, выход с аккаунта
- [x] Система управления своими объявлениями для пользователя
- [x] Настройка Docker, Docker-compose
- [x] Настройка CI/CD через github actions
- [x] Интеграция Yandex карт
- [x] Интегрировать на сайт ReCaptcha
- [x] Настройки пользователя через профиль (имя, приватность)
- [x] Система диалогов
- [ ] Оптимизация проекта
  - [x] Оптимизация SQL-запросов
  - [x] Индексы БД
  - [x] Оптимизация Nginx
  - [ ] Оптимизация PostgreSQL
  - [ ] Оптимизация взаимодействия с Yandex картами
  - [ ] Внедрение кэширования, Redis
- [x] Внедрение Poetry
- [x] Внедрение различных средств форматирования
  - [x] Black
  - [x] isort, flake8
  - [x] Pre-commit
- [ ] Система оповещения администраторов о новом объявлении через телеграм
- [ ] Скачивание объявления для распечатывания с QR-кодом
- [ ] API со всем функционалом из обычного сайта
  - [x] Создание объявлений
  - [x] Открытие/закрытие объявлений
- [ ] 100% покрытие тестами
  - [ ] Приложение с шаблонами
  - [ ] API

</details>

## Установка и эксплуатация

<details>
  <summary>Локальная установка, запуск, тестирование (без Docker)</summary>
  <br>

### Установка проекта локально (без Docker)

1. Устанавливаем инструмент для работы с виртуальным окружением и сборки пакетов `poetry`, [инструкция в официальной документации](https://python-poetry.org/docs/#installation).
2. Клонируем репозиторий с проектом и переходим в его директорию:
```shell
git clone https://github.com/melax08/pet_alert.git && cd pet_alert
```
3. Устанавливаем зависимости:
```shell
poetry install
```
4. Копируем файл `.env.example` с новыми названием `.env` и заполняем его необходимыми данными:
```shell
cp .env.example .env && nano .env
```
5. Подготавливаем бэкенд к работе:
```shell
poetry run python3 src/pet_alert/manage.py migrate
```

Опционально. Создаем суперпользователя:
```shell
poetry run python3 manage.py createsuperuser
```

### Запуск проекта локально (без Docker)

Переходим в каталог с проектом:
```shell
cd src/pet_alert
```

Запускаем проект:
```shell
poetry run python3 manage.py runserver
```

Локальный проект будет доступен по http://127.0.0.1:8000

### Запуск тестов

Чтобы запустить `unittest` тестирование работы функционала Django-приложений, выполним команду:

```shell
poetry run python3 manage.py test -v 2
```

</details>

<details><summary>Установка и запуск в Docker-контейнерах</summary>

<br>

Инструкция в разработке.

</details>


<!-- MARKDOWN LINKS & BADGES -->

[Python-url]: https://www.python.org/
[Python-badge]: https://img.shields.io/badge/Python-376f9f?style=for-the-badge&logo=python&logoColor=white
[Django-url]: https://github.com/django/django
[Django-badge]: https://img.shields.io/badge/Django-0c4b33?style=for-the-badge&logo=django&logoColor=white
[DRF-url]: https://github.com/encode/django-rest-framework
[DRF-badge]: https://img.shields.io/badge/DRF-a30000?style=for-the-badge
[Postgres-url]: https://www.postgresql.org/
[Postgres-badge]: https://img.shields.io/badge/postgres-306189?style=for-the-badge&logo=postgresql&logoColor=white
[Nginx-url]: https://nginx.org
[Nginx-badge]: https://img.shields.io/badge/nginx-009900?style=for-the-badge&logo=nginx&logoColor=white
[Poetry-url]: https://python-poetry.org
[Poetry-badge]: https://img.shields.io/badge/poetry-blue?style=for-the-badge&logo=Poetry&logoColor=white&link=https%3A%2F%2Fpython-poetry.org
[Docker-url]: https://www.docker.com
[Docker-badge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
