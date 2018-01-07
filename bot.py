import config
import aiml
import telebot

kernel = aiml.Kernel()
kernel.bootstrap(learnFiles=config.startup_file, commands="LOAD AIML BOT")

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, config.title_ru)


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, config.help_ru)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def response(message):
    kernel.setPredicate("name", message.chat.first_name + " " + message.chat.last_name)
    kernel_response = kernel.respond(message.text)
    print("receive message: \"{}\", from {}. response: \"{}\"".format(
        message.text,
        message.chat.first_name + " " + message.chat.last_name,
        kernel_response)
    )
    bot.send_message(message.chat.id, kernel_response)


if __name__ == '__main__':
    bot.polling(none_stop=True)
