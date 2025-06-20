# 🤖 Telegram-бот, который предоставляет доступ к двум российским языковым моделям: YandexGPT и SberAI (GigaChat) . 
Позволяет переключаться между провайдерами, сохраняет историю диалога и отвечает на вопросы пользователей


### 🔧 Требования
##### Для запуска проекта необходимы:

* Python 3.10+
* Библиотеки: python-telegram-bot, requests, python-dotenv
* API-ключи:
1. Yandex Cloud — YandexGPT
2. SberAI GigaChat Dev — GigaChat
3. Telegram Bot Token (получается через @BotFather )

##### 📦 Установка зависимостей
```bash
pip install -r requirements.txt
```
### 🔐 Настройка окружения
* Создайте файл .env в корне проекта
* добавьте в него следующие параметры:
```
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=ваш_токен_от_botfather

# YandexGPT
YANDEX_API_KEY=ваш_yandex_api_key
YANDEX_FOLDER_ID=ваш_folder_id
YANDEX_MODEL=yandexgpt-lite  # или yandexgpt

# SberAI GigaChat
SBER_API_KEY=ваш_sber_api_key
SBER_MODEL=GigaChat:latest    # или другая версия модели

# Провайдер по умолчанию (yandexgpt или sberai)
DEFAULT_PROVIDER=yandexgpt
```
##### ⚠️ Никогда не публикуйте содержимое .env файла в открытых репозиториях! 

### 🚀 Запуск бота
```
python main.py
```

##### После успешного запуска бот начнёт ожидать сообщений в Telegram. Напишите ему /start, чтобы начать общение.

### 📝 Команды бота
```
/start     Приветственное сообщение
/yandex    Переключиться на YandexGPT
/sber      Переключиться на SberAI (GigaChat)
/clear     Очистить историю диалога
```

### 💬 Общение с ботом
* Просто отправьте текстовое сообщение с вашим вопросом — бот ответит, используя выбранную модель ИИ.

### 📊 Логирование
Логи записываются в консоль в формате:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```
### 📌 Возможности
* Поддержка нескольких ИИ-провайдеров
* Сохранение истории диалога
* Отображение времени генерации ответа
* Работа через Telegram интерфейс