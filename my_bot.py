import telebot
from telebot import types
import logging.config
import sys

logging.config.fileConfig("logging_config.ini")
logger = logging.getLogger("my_bot")
bot = telebot.TeleBot('Token')


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot_token, chat_id):
        super().__init__()
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(self.chat_id, log_entry)


class FunctionBasedFilter(logging.Filter):
    def __init__(self, exclude_function_name):
        super().__init__()
        self.exclude_function_name = exclude_function_name

    def filter(self, record):
        return not record.funcName.startswith(self.exclude_function_name)

weight = 0
height = 0
imt = 0


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Давай узнаем твой ИМТ!')
        bot.send_message(message.from_user.id, "Напиши свой текущий вес (кг)")
        bot.register_next_step_handler(message, get_weight)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')


def get_weight(message):
    global weight
    while weight == 0:
        try:
            weight = float(message.text)
        except Exception:
            logger.error('Ошибка ввода веса')
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
    bot.send_message(message.from_user.id, 'Напиши свой текущий рост (см)')
    bot.register_next_step_handler(message, get_height)


def get_height(message):
    global height
    while height == 0:
        try:
            height = float(message.text)
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(message, get_height)
    bot.send_message(message.from_user.id, 'Вы готовы узнать твой ИМТ?')
    bot.register_next_step_handler(message, get_imt)

def get_imt(message):
    global imt
    imt = int(weight / (height / 100) ** 2)
    if imt < 20:
        bot.send_message(message.from_user.id, f'Твой ИМТ: {imt}. Это недостаточный вес.')
    elif 20 <= imt < 25:
        bot.send_message(message.from_user.id, f'Твой ИМТ: {imt}. Идеальный вес, риски для здоровья минимальны.')
    elif 25 <= imt < 30:
        bot.send_message(message.from_user.id, f'Твой ИМТ: {imt}. Наличие лишнего веса')
    elif 30 <= imt < 35:
        bot.send_message(message.from_user.id, f'Твой ИМТ: {imt}. Первая стадия ожирения')
    else:
        bot.send_message(message.from_user.id, f'Твой ИМТ: {imt}. Продвинутое ожирение')

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе понравился наш бот?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  
        bot.send_message(call.message.chat.id, 'Спасибо, мы рады : )')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Ну и ладно : )')


bot.polling(none_stop=True, interval=0)


logger.addHandler(TelegramLogHandler('YOUR_BOT_TOKEN', 'YOUR_CHAT_ID'))
logger.addFilter(FunctionBasedFilter('get_weight'))  
