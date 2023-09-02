from environs import Env
from aiogram import Bot
from handlers.handlers import dp

env = Env()
env.read_env('../env/.env')

BOT_TOKEN = env('BOT_TOKEN')


# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)

# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)
