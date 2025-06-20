import requests
import logging
from telegram import Update, BotCommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import time
from dotenv import load_dotenv
import sys

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Вывод в консоль
        logging.FileHandler('bot.log')      # Запись в файл
    ]
)
logger = logging.getLogger(__name__)


class RussianAI:
    def __init__(self):
        self.provider = os.getenv("DEFAULT_PROVIDER", "yandexgpt")
        self.conversation_history = []
        self.set_provider(self.provider)

    def set_provider(self, provider: str):
        self.provider = provider.lower()
        self.conversation_history = []

        if self.provider == 'yandexgpt':
            self.api_key = os.getenv('YANDEX_API_KEY')
            self.folder_id = os.getenv('YANDEX_FOLDER_ID')
            self.model = os.getenv('YANDEX_MODEL', 'yandexgpt-lite')
            self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

            if not self.api_key or not self.folder_id:
                logger.error('Не заданы ключи от яндекс апи и каталога!')
                return False

        elif self.provider == "sberai":
            self.api_key = os.getenv("SBER_API_KEY")
            self.model = os.getenv("SBER_MODEL", "GigaChat:latest")
            self.base_url = "https://api.gigachat.dev/v1/chat/completions"

            if not self.api_key:
                logger.error("Не задан SBER_API_KEY")
                return False

        else:
            logger.error(f"Неизвестный провайдер: {provider}")
            return False

        logger.info(f"Используется провайдер: {self.provider.upper()} ({self.model})")
        return True

    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})

    def generate_response(self, user_input: str):
        self.add_message("user", user_input)

        try:
            if self.provider == "yandexgpt":
                return self._yandex_request()
            elif self.provider == "sberai":
                return self._sber_request()
        except Exception as e:
            return f"🚨 Ошибка API ({self.provider}): {str(e)}"

    def _yandex_request(self):
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
            "x-folder-id": self.folder_id
        }

        yandex_messages = [{"role": msg["role"], "text": msg["content"]} for msg in self.conversation_history]

        payload = {
            "modelUri": f"gpt://{self.folder_id}/{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 2000
            },
            "messages": yandex_messages
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)

            if response.status_code != 200:
                logger.error(f"Ошибка {response.status_code}: {response.text}")
                return f"Ошибка API: {response.text}"

            data = response.json()
            ai_reply = data["result"]["alternatives"][0]["message"]["text"]
            self.add_message("assistant", ai_reply)
            return ai_reply

        except Exception as e:
            return f"Ошибка соединения: {str(e)}"

    def _sber_request(self):
        auth_response = requests.post(
            "https://api.gigachat.dev/v1/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": self.api_key,
                "scope": "GIGACHAT_API_PERS"
            }
        )

        if auth_response.status_code != 200:
            logger.error(f"Ошибка аутентификации SberAI: {auth_response.text}")
            return "Ошибка аутентификации SberAI"

        auth_data = auth_response.json()
        access_token = auth_data["access_token"]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            logger.error(f"Ошибка SberAI: {response.status_code} - {response.text}")
            return f"Ошибка SberAI: {response.text}"

        data = response.json()
        ai_reply = data["choices"][0]["message"]["content"]
        self.add_message("assistant", ai_reply)
        return ai_reply

    def clear_history(self):
        self.conversation_history = []
        logger.info("История диалога очищена")
        return True


ai_assistant = RussianAI()


def start(update: Update, context: CallbackContext) -> None:
    help_text = (
        'Привет! Я ИИ-ассистент. Могу ответить на вопросы с помощью:\n'
        f'YandexGPT ({ai_assistant.model if ai_assistant.provider == "yandexgpt" else "доступен через /yandex"})\n'
        f'SberAI ({ai_assistant.model if ai_assistant.provider == "sberai" else "доступен через /sber"})\n\n'
        'Доступные команды:\n'
        '/yandex - использовать YandexGPT\n'
        '/sber - использовать SberAI (GigaChat)\n'
        '/clear - очистить историю диалога\n'
        'Просто отправьте мне сообщение с вашим вопросом!'
    )
    update.message.reply_text(help_text)


def switch_to_yandex(update: Update, context: CallbackContext) -> None:
    if ai_assistant.set_provider('yandexgpt'):
        update.message.reply_text(f'✅ Переключено на YandexGPT ({ai_assistant.model})')
    else:
        update.message.reply_text('❌ Не удалось переключиться на YandexGPT')


def switch_to_sber(update: Update, context: CallbackContext) -> None:
    if ai_assistant.set_provider('sberai'):
        update.message.reply_text(f'✅ Переключено на SberAI ({ai_assistant.model})')
    else:
        update.message.reply_text('❌ Не удалось переключиться на SberAI')


def clear_history(update: Update, context: CallbackContext) -> None:
    if ai_assistant.clear_history():
        update.message.reply_text('🗑️ История диалога очищена!')
    else:
        update.message.reply_text('❌ Не удалось очистить историю')


def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    if user_input.startswith('/'):
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    start_time = time.time()

    try:
        response = ai_assistant.generate_response(user_input)
        elapsed_time = time.time() - start_time

        formatted_response = (
            f"🤖 {ai_assistant.provider.upper()} отвечает:\n"
            f"{response}\n"
            f"⏱ Время генерации: {elapsed_time:.2f} сек"
        )
        update.message.reply_text(formatted_response)

    except Exception as e:
        logger.error(f"Ошибка генерации ответа: {str(e)}")
        update.message.reply_text("🚨 Произошла ошибка при генерации ответа. Попробуйте позже.")


def set_bot_commands(bot):
    """Устанавливает список команд, отображаемых в меню бота"""
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("yandex", "Переключиться на YandexGPT"),
        BotCommand("sber", "Переключиться на SberAI (GigaChat)"),
        BotCommand("clear", "Очистить историю диалога"),
    ]
    bot.set_my_commands(commands)
    # print("Команды бота установлены") # для отладки


def main():
    if not os.getenv("YANDEX_API_KEY") and not os.getenv("SBER_API_KEY"):
        logger.error("Не найдены API-ключи! Проверьте .env файл")
        print("❌ ОШИБКА: Не найден ни один API ключ в .env файле!")
        print("Добавьте ключи для Yandex или SberAI")
        print("Пример .env файла:")
        print("YANDEX_API_KEY=ваш_ключ_яндекс")
        print("YANDEX_FOLDER_ID=ваш_folder_id")
        print("SBER_API_KEY=ваш_ключ_сбер")
        return

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("Не задан TELEGRAM_BOT_TOKEN в .env файле!")
        print("❌ ОШИБКА: Не задан TELEGRAM_BOT_TOKEN в .env файле!")
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("yandex", switch_to_yandex))
    dispatcher.add_handler(CommandHandler("sber", switch_to_sber))
    dispatcher.add_handler(CommandHandler("clear", clear_history))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Установка команд бота
    set_bot_commands(updater.bot)

    # Запуск бота
    updater.start_polling(
        poll_interval=1,  # Оптимально для сервера
        timeout=15,
        drop_pending_updates=True
    )
    logger.info("🤖 Российский AI-ассистент запущен и готов к работе!")
    print("Бот успешно запущен. Используйте /start в Telegram для начала работы.")
    updater.idle()


if __name__ == '__main__':
    main()