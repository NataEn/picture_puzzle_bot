import logging
import bot_settings
import functionality
# from sys import stdout
# stdout.reconfigure(encoding="utf-16")
from PIL import Image
import emoji

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

NAME, GAME, PHOTO = range(3)


def start(update, context):
    update.message.reply_text(
        f'Hi! My name is Puzzle Bot. I am happy to meet you {emoji.emojize(":grinning_face_with_big_eyes:")}\n'
        'Send /cancel to stop talking to me.\n\n'
        'What is you name?')

    return NAME


def name(update, context):
    reply_keyboard = [['Sure!', 'Not today...']]
    user = update.message.from_user
    context.user_data["name"] = update.message.text
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    context.user_data['user_name'] = update.message.text
    update.message.reply_text(
        f'Nice to meet you {context.user_data["user_name"]}! \n Do you want to play a game with me?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return GAME


def skip_name(update, context):
    logger.info("Name of %s: %s didn't want to send name", context.user.first_name, update.message.text)
    context.user_data["name"] = 'Grumpy'
    update.message.reply_text(
        'OK, so I\'ll call you Grumpy!\n So, Grumpy, send me a photo of yourself, '
        'so I could sent it back as a puzzle '
        '\nSend /skip if you don\'t want to.')
    return GAME


def game(update, context):
    user = update.message.from_user
    logger.info("Name of %s: %s", user.first_name, update.message.text)
    # response=user_answer_check(update.message.text)
    if update.message.text == 'Sure!':
        update.message.reply_text(f'Lets play {context.user_data["user_name"]}!\n Please send me a photo of yourself, '
                                  'so I could sent it back as a puzzle.\nSend /skip if you don\'t want to.',
                                  reply_markup=ReplyKeyboardRemove())

        return PHOTO
    elif update.message.text == 'Not today...':
        return skip_game()
    return PHOTO


# def user_answer_check(response):
#     if response == 'Sure!':
#         update.message.reply_text(f'Lets play {context.user_data["user_name"]}!\n Please send me a photo of yourself, '
#                                   'so I could sent it back as a puzzle.\nSend /skip if you don\'t want to.',
#                                   reply_markup=ReplyKeyboardRemove())
#
#         return PHOTO
#     elif update.message.text == 'Not today...':
#         return skip_game()


def skip_game(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(f'Oh no....I am sad now {emoji.emojize(":slightly_frowning_face:")}.... \n')

    return ConversationHandler.END


def photo(update, context):
    user = update.message.from_user
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    photo_file = update.message.photo[-1].get_file()
    photo_path = photo_file['file_path']
    print(photo_path)
    chat_id = update.effective_chat.id
    print(photo_file)
    photo_file.download('user_photo.jpg')
    photo=Image.open('user_photo.jpg')
    print(photo)
    # making puzzle
    resized_photo = functionality.resize_img(photo, 300, 300)
    photo_parts = functionality.cut_img(resized_photo, 100)
    new_photo = functionality.assemble_img(photo_parts, 300, 300, 100)
    new_photo.save('new_user_photo.png')

    update.message.reply_text(text='Gorgeous! This is how I see you..')
    context.bot.send_photo(chat_id=chat_id, photo=open('new_user_photo.png', 'rb'))

    return ConversationHandler.END


def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(token=bot_settings.BOT_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states NAME and PHOTO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NAME: [MessageHandler(Filters.text, name)],
            GAME: [MessageHandler(Filters.text, game),
                   CommandHandler('skip', skip_game)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    logger.info('start pulling...."')
    updater.idle()


if __name__ == '__main__':
    main()
