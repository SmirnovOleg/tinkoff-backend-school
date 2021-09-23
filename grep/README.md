# Homework 2. MyGrep utility

Аналог утилиты `grep`, которая выполняет поиск указанной подстроки во всеx файлах указанной директории и всех её
поддиректорий.

### Установка

- `python setup.py install`

### Использование

```
usage: mygrep [-h] path substring

positional arguments:
  path        path to target directory
  substring   substring to search for

optional arguments:
  -h, --help  show this help message and exit
```

### Запуск тестов

- `make venv`
- `make test`