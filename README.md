# Pet Alert - веб-портал для поиска пропавших животных

![petalert workflow](https://github.com/melax08/pet_alert/actions/workflows/petalert-workflow.yml/badge.svg)

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

In progress


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