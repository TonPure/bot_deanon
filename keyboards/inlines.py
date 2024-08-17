from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from lexicon import lexicon_ru
from aiogram.filters.callback_data import CallbackData

class MyCallback(CallbackData, prefix="my"):
    foo: str
    bar: int | None = None

def create_inline_keyboards():
    stat_but = InlineKeyboardButton(
        text=lexicon_ru.LEXICON_RU['stat'],
        callback_data='/stat'
    )

    more_message_but = InlineKeyboardButton(
        text=lexicon_ru.LEXICON_RU['more_message'],
        callback_data='/more_message'
    )

    change_link_but = InlineKeyboardButton(
        text=lexicon_ru.LEXICON_RU['change_link'],
        callback_data='/change_link'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[stat_but],
                         [more_message_but],
                         [change_link_but]]
   )

    return keyboard
    
def create_inline_cancel():
    cancel_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['cancel_but'],
        callback_data='/start'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[cancel_but]]
    )
    
    return keyboard

def create_options_message(sender):
    answer_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['answer'],
        callback_data = MyCallback(foo='answer', bar=sender).pack()
    ) 

    get_name_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['get_name'],
        callback_data='get_name'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[answer_but],
                         [get_name_but]]
    )

    return keyboard

def create_more_message_inline():
    stat_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['stat'],
        callback_data = '/stat'
    )

    i_see_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['/i_see'],
        callback_data = '/start'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[stat_but],
                         [i_see_but]]
    )

    return keyboard

def create_change_options():
    change_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['change'],
        callback_data = '/change'
    )

    back_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['back'],
        callback_data = '/start'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[change_but],
                         [back_but]]
    )

    return keyboard

def create_inline_back():
    back_but = InlineKeyboardButton(
        text = lexicon_ru.LEXICON_RU['back'],
        callback_data = '/start'
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[back_but]]
    )

    return keyboard
