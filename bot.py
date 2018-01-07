import config
import random

import aiml
import telebot
from googletrans import Translator

kernel = aiml.Kernel()
kernel.bootstrap(learnFiles=config.startup_file, commands="LOAD AIML BOT")

bot = telebot.TeleBot(config.token)
translator = Translator()


def log_messages(text, from_user, bot_response, type="message"):
    print("receive {}: \"{}\", from {}. response: \"{}\"".format(
        type,
        text,
        from_user,
        bot_response)
    )


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, config.title_ru)
    log_messages(
        "/start",
        message.chat.first_name + " " + message.chat.last_name,
        config.title_ru,
        type="command"
    )


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, config.help_ru)
    log_messages(
        "/help",
        message.chat.first_name + " " + message.chat.last_name,
        config.title_ru,
        type="command"
    )


def translate_empty(dest):
    text = random.choice(config.random_russian_words)
    response_text = config.empty_translate_text_message.format(
        text,
        translator.translate(text, dest=dest).text
    )
    return response_text


@bot.message_handler(commands=["translate"])
def handle_translate(message):
    command_len = len("/translate") + 1

    text = message.text[command_len:]
    stored_dest_lang = kernel.getPredicate("translate_dest_lang", message.chat.id)
    stored_dest_lang = stored_dest_lang if stored_dest_lang in config.languages else "en"
    if text == "":
        response_text = translate_empty(stored_dest_lang)
    elif text[:2] in config.languages:
        dest = text[:2]
        text = text[3:]
        if text == "":
            response_text = translate_empty(dest)
        else:
            response_text = translator.translate(text, dest=dest).text
    else:
        response_text = translator.translate(text, dest=stored_dest_lang).text

    log_messages(
        message.text,
        message.chat.first_name + " " + message.chat.last_name,
        response_text,
        type="command"
    )

    bot.send_message(message.chat.id, response_text)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def response(message):
    kernel.setPredicate("name", message.chat.first_name + " " + message.chat.last_name, message.chat.id)
    response_text = kernel.respond(message.text, message.chat.id)
    log_messages(
        message.text,
        message.chat.first_name + " " + message.chat.last_name,
        response_text
    )
    bot.send_message(message.chat.id, response_text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
