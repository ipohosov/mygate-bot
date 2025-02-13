# Mygate Node 

## Общая информация

Софт для запуска множества нод Mygate на одном сервере без браузера

## Основные особенности 

* **Поддержка прокси**
* **Детальное логирование**
* **Обработка ошибок**
* **Сохранение логов в файлы по дням**
* **Параллельный запуск аккаунтов**

## Требования к серверу
* **Ubuntu 22.04**
* **3.8.x <= python <= 3.11.x**
> Проверить версию питона можно командой **_python3 -V_**
* **tmux**
> Установка **_apt install tmux -y_**


## Подготовка к запуску

### 1. Регистрация аккаунтов Mygate Node

1. Регистрируем аккаунты Mygate Node
2. Заходим на дашборд и проверяем, что нода отобразилась

### 2. Покупаем прокси под каждый аккаунт

1. Сохраняем прокси в формате `http://user:password@host:port`

### 3. Клонирование репозитория

```bash
git clone https://github.com/ipohosov/mygate-bot.git
```
Для выполнения следующих команд перейдите в терминале в папку с проектом.

### 4. Добавление аккаунтов Mygate Node

1. Копируем файл _accounts.example.csv_ в файл _accounts.csv_
```bash
cp ./data/accounts.example.csv ./data/accounts.csv
```
2. Заполняем документ
   1. **Email** - приватный ключ, который использовался при регистрации
   2. **Token** - jwt токен любого реквеста с дашборда 
   3. **Proxy** - прокси для каждого аккаунта в формате `http://user:password@host:port`. 
3. Итого одна запись для аккаунта будет выглядить как строка
```bash
email,jwt_token,http://user:proxy_pwd@host:port
```

##  Установка и запуск проекта

> Устанавливая проект, вы принимаете риски использования софта(вас могут в любой день побрить даже если вы не спорите за цену Neon).

Для установки необходимых библиотек, пропишите в консоль

```bash
pip install -r requirements.txt
```

Запуск проекта

```bash
tmux new-session -s mygate_bot -d 'python3 main.py'
```

>Не удаляйте папку `accounts` в папке `data`. Это данные о каждом из ваших аккаунтов. Чтобы не собирать ее при каждом запуске, она хранится локально у вас на сервере. Никакой супер важной ифнормации там нет.

##  Полезные дополнительные штучки

### 1. Проверка логов

Логи можно проверить, как в папке logs, так и открыв сессию tmux. Чтобы отсоединиться от сессии и оставить ее работающей в фоне, просто нажмите Ctrl + b, затем d.
```bash
tmux attach-session -t mygate_bot
```
### 2. Вывести статистику по поинтам

```bash
bash stats.sh
```
> 
> Важно помнить что статистика по очкам обновляется раз в 2 часа, поэтому лучше проверять после того как скрипт отработает уже 2+ часов. Вероятность того, что в течении 2 часов будет собрана статистика 1 раз около 100%. Но рандомайзер не может гарантировать этого.