from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import mysql.connector

# Конфигурация базы данных
db_config = {
    'user': 'your_user',
    'password': 'your_password',
    'host': 'db',  # Docker-compose использует имя сервиса в качестве хоста
    'database': 'job_database',
}

# Подключение к базе данных
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Функция для поиска вакансий
def search_jobs(query):
    search_query = "SELECT * FROM vacancies WHERE job_title LIKE %s OR skills LIKE %s"
    cursor.execute(search_query, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    return results

# Функция для обработки команды /search
def search(update: Update, context: CallbackContext) -> None:
    query = ' '.join(context.args)
    results = search_jobs(query)
    response = "\n".join([f"{r[1]}: {r[2]} ({r[3]})" for r in results])
    update.message.reply_text(response)

# Основной код для запуска бота
def main() -> None:
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("search", search))

    updater.start_polling()
    updater.idle()

# Закрытие соединения с базой данных
cursor.close()
conn.close()

if __name__ == '__main__':
    main()
