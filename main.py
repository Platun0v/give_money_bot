import telebot
import config

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message):
    bot.send_message(message.chat.id, message.from_user.id)


bot.polling()
