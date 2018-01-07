import config
import constants
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
    bot.send_message(message.chat.id, constants.title_ru)
    log_messages(
        "/start",
        message.chat.first_name + " " + message.chat.last_name,
        constants.title_ru,
        type="command"
    )


@bot.message_handler(commands=["help"])
def handle_help(message):
    bot.send_message(message.chat.id, constants.help_ru)
    log_messages(
        "/help",
        message.chat.first_name + " " + message.chat.last_name,
        constants.title_ru,
        type="command"
    )


def translate_text(text, dest):
    if text == "":
        text = random.choice(constants.random_russian_words)
        response_text = constants.empty_translate_text_message.format(
            text,
            translator.translate(text, dest=dest).text
        )
    else:
        response_text = translator.translate(text, dest=dest).text
    return response_text


@bot.message_handler(commands=["translate"])
def handle_translate(message):
    command_len = len("/translate") + 1

    text = message.text[command_len:]
    dest_lang = kernel.getPredicate("translate_dest_lang", message.chat.id)
    dest_lang = dest_lang if dest_lang in constants.languages else "en"

    if text[:2] in constants.languages:
        dest_lang = text[:2]
        text = text[3:]
    response_text = translate_text(text, dest=dest_lang)

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
    if message.text.lower().startswith(constants.translate_key_ru):
        text = kernel.getPredicate("translate_text", message.chat.id)
        dest_lang = kernel.getPredicate("translate_dest_lang", message.chat.id)
        dest_lang = dest_lang if dest_lang in constants.languages else "en"
        response_text += " " + translate_text(text, dest=dest_lang)

    log_messages(
        message.text,
        message.chat.first_name + " " + message.chat.last_name,
        response_text
    )
    bot.send_message(message.chat.id, response_text)


if __name__ == '__main__':
    bot.polling(none_stop=True)
