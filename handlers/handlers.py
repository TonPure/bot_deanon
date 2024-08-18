import json

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload
from keyboards.inlines import *
from lexicon import lexicon_ru
from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from config_data.config import Config, load_config
from keyboards.inlines import MyCallback

storage = MemoryStorage() # хранилище для машины состояний

config: Config = load_config()

router = Router()


with open('user_dict.json', 'r') as f:      # считываем словарь с пользователями
    try:
        user_dict = json.load(f)
    except json.decoder.JSONDecodeError as err:
        print(f'                  {err}                                    ')


class FSM(StatesGroup):                      # Машина состояний
    fill_message = State()                   # Состояние ожидающее ввода сообщения
    fill_link = State()                      # Состояние ожидающее ввода ника


def check_dict(payload):                    # фун-я поиска id пользователя по нику 
    for k,v in user_dict.items():           # в словаре
        if v['payload'] == payload:
            return k

def get_payload(user):                      # фун-я проверки существующего ника 
    payload = user_dict[user]['payload']    # конкретного пользователя,
    if payload == '': return user           # в словаре пользователей
    else: return payload

@router.message(CommandStart(deep_link=True))    # переход по чьей-то ссылке
async def process_deep_command(message: Message, bot: Bot, state: FSMContext):
    args = message.text.split()
    recipient = check_dict(args[1]) # из аргументов(из deep_link) берем id получателя
    sender = str(message.from_user.id) # id отправителя
    if str(recipient) == sender:        # если пытаешся отправить сообщение себе
        deep_link = await create_start_link(bot,payload=get_payload(sender) # созд ссыль
        await message.answer(  # выдаем сообщение и ссыль
                text = f'{lexicon_ru.LEXICON_RU["/cancel_but_text"]} {str(deep_link)}'
        )
    else:
        await bot.send_message(        # приглашение написать сообщение
            sender,
            text=lexicon_ru.LEXICON_RU['/deep_start'],
            reply_markup=create_inline_cancel(), # добавим кнопку отмены 
            parse_mode='HTML'
        )
        await state.update_data(recipient=recipient, sender=sender) # сохраняем id
        await state.set_state(FSM.fill_message)    # устанавливаем состояние 
                                                   # ожидающее сообщение 

@router.message(StateFilter(FSM.fill_link))        # состояние сменить ссылку
async def process_get_link(message: Message, bot: Bot, state: FSMContext):
    user = message.from_user.id   # считаем id пользователя
    payload = message.text       # считываем ник 
    if check_dict(payload):      # проверяем не занято ли
        await bot.send_message(  # сообщаем что ник занят
            user
            text = lexicon_ru.LEXICON_RU['get_link_true']
        )
        await state.set_state(FSM.fill_link) # установим состояние смены ссылки
    else:
        old_link = await create_start_link(bot, user) # ссыль с id
        deep_link = await create_start_link(bot, payload) # ссыль с ником
        await bot.send_message(
            message.from_user.id,
            text = f'{lexicon_ru.LEXICON_RU["get_link_false"]}'.format(payload,deep_link, old_link)
        )
        await bot.send_message(   # и выводим стартовое сообщение
            user,
            text=lexicon_ru.LEXICON_RU['/start']+
                  str(deep_link) +"\n\n"+
                  lexicon_ru.LEXICON_RU['/start 1'],
            reply_markup=create_inline_keyboards()
        )

        user_dict[str(message.from_user.id)]['payload'] = payload # сохраним ник 
        with open('user_dict.json', 'w') as f:                    # в словарь
            json.dump(user_dict, f, indent=4, ensure_ascii=False) # и в файл


@router.message(StateFilter(FSM.fill_message)) # состояние написать сообщение
async def process_recipient(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()  # считываем state
    recipient, sender = data['recipient'], data['sender']
    if 'answer' in data:  # если это ответ на сообщение 
        message.answer(   # сообщаем что отправили
            text = f'{lexicon_ru.LEXICON_RU["answer_send"]}'
        )
        deep_link = await create_start_link(bot=bot, payload=get_payload(sender) # создаем ссыль
        await bot.send_message(  # выводим стартовое сообщение
            user,
            text=lexicon_ru.LEXICON_RU['/start']+
                  str(deep_link) +"\n\n"+
                  lexicon_ru.LEXICON_RU['/start 1'],
            reply_markup=create_inline_keyboards()
        )

    else:            # если не ответ, а сообщение по ссылке
        await bot.send_message( # отправляем сообщение
            recipient,
            text = f'{lexicon_ru.LEXICON_RU["get_message"]}\n\n'
                   f'{message.text}\n',
            reply_markup=create_options_message(sender) # прикрепляем кнопки для ответа
        )                                               # и платной опции
        if int(recipient) in config.tg_bot.admin_ids:  # если получатель в списке 
            await bot.send_message(                    # админов - отправляем ник 
                recipient,                             # отправителя
                text = f'👆 {message.from_user.first_name} --> <a href="tg://user?id={message.from_user.id}">@{message.from_user.username}</a>',
                parse_mode='HTML'
            )
    user_dict[recipient]['count_in']+=1        # итерируем счетчики сообщений 
    user_dict[sender]["count_out"]+=1          # для статистики
    with open('user_dict.json', 'w') as f:   # сохраняем словарь в файл
        json.dump(user_dict, f, indent=4, ensure_ascii=False) 
    await state.clear()            # очищаем состояние


@router.callback_query(F.data == '/start') # стартовое состояние по кнопке отмены
async def process_start_callback(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()          # откл анимацию ожидания на кнопке
    user = call.from_user.id     # берем id юзера
    deep_link = await create_start_link(bot=bot, payload=get_payload(user))
    await bot.send_message(   # стартовое сообщение
        user,
        text=lexicon_ru.LEXICON_RU['/start']+
              str(deep_link) +"\n\n"+
              lexicon_ru.LEXICON_RU['/start 1'],
        reply_markup=create_inline_keyboards()
    )


@router.message(CommandStart()) # старт бота из меню
async def process_start_command(call: CallbackQuery, bot: Bot, state: FSMContext):
    user = str(call.from_user.id) # id пользователя
    if str(user) in user_dict:   # если пользователь в словаре
        deep_link = await create_start_link(bot=bot, payload=get_payload(user))
    else:  # если не в словаре добавляем
        user_dict[user] = {"payload":"",
                           "count_in":0,
                           "count_out":0}
        deep_link = await create_start_link(bot=bot, payload=user) # создаем ссыль
    await bot.send_message(  # отправляем стартовое сообщение
        user,
        text=lexicon_ru.LEXICON_RU['/start']+
              str(deep_link) +"\n\n"+
              lexicon_ru.LEXICON_RU['/start 1'],
        reply_markup=create_inline_keyboards()
    )


@router.callback_query(F.data=='/stat') # нажатие на кнопку статистика
async def process_stat(call: CallbackQuery, bot: Bot, state: FSMContext):
    await call.answer()
    user = call.from_user.id # id пользователя
    input_msg = user_dict[user]["count_in"] # сообщений получено
    output_msg = user_dict[user]["count_out"] # сообщений отправлено
    c_worse_in = 0
    c_worse_out = 0

    for x in user_dict:  # считаем сколько пользователей с меньшим кол-вом сообщений
        if user_dict[x]["count_out"] < output_msg: 
            c_worse_out+=1
            print(f' y["count_out"] --> {y["count_out"]}')

        if user_dict[x]["count_in"] < input_msg: c_worse_in+=1
    
    persent_out = c_worse_out/len(user_dict)*100 # считаем в процентах насколько круче
    persent_in = c_worse_in/len(user_dict)*100
    try:
        persent = 2/(persent_out+persent_in)
    except Exception as e: print(f'-------{e}-------')
    await call.message.answer(  # сообщение со статистикой
        text=f'{lexicon_ru.LEXICON_RU["/stat"]}'.format(input_msg, output_msg,0,0, deep_link,),
        reply_markup=create_inline_back() # кнопка назад
    )

@router.callback_query(F.data=='/more_message') # нажатие кнопки " Больше сообщений "
async def process_more_message(call: CallbackQuery, bot: Bot):
    user = call.from_user.id
    deep_link = await create_start_link(bot=bot,payload=get_payload(user))
    await call.answer() # "отключение" анимации ожидания на кнопке
    await call.message.answer( # сообщение с просьбой оставилять ссылку везде
        text=lexicon_ru.LEXICON_RU['/more_message']+
              str(deep_link) +"\n\n"+
              lexicon_ru.LEXICON_RU['/more_message1'],
        reply_markup=create_more_message_inline(), # кнопки
        parse_mode='HTML'
    )


@router.callback_query(F.data=='/change_link') # нажатие кнопки смены ссылки (ник)
async def process_change_link(call: CallbackQuery, bot: Bot, state: FSMContext):
    recipient = call.from_user.id   # id пользователя
    deep_link = create_start_link(bot=bot, payload=get_payload(recipient)
    await call.answer() # "отключение" анимации ожидания на кнопке
    await bot.send_message( # предлагаем сменить ссылку и выводим кнопки
        recipient,
        text = f'{lexicon_ru.LEXICON_RU["/change_link_text"]}'.format(recipient,deep_link),
        reply_markup = create_change_options()
    )


@router.callback_query(F.data=='/change') # нажатие сменить ссылку
async def process_change_but(call: CallbackQuery, bot: Bot, state: FSMContext):
    recipient = call.from_user.id
    await call.answer() # "отключение" анимации ожидания на кнопке
    await bot.send_message( # просим ввести ник
        recipient,
        text = lexicon_ru.LEXICON_RU['/change'],
        reply_markup = create_inline_cancel()
    )
    await state.set_state(FSM.fill_link) # устанавливаем состояние ввода ника


@router.callback_query(F.data=='get_name') # нажатие на кнопку "получить имя"
async def process_get_name(call: CallbackQuery, bot: Bot, state: FSMContext):
    recipient = call.from_user.id         # получаем id
    await call.answer()  # отключаем анимацию кнопки
    await bot.send_message( # сообщаем что функция не реализована
        recipient,
        text = lexicon_ru.LEXICON_RU['get_name_text']
    )


@router.callback_query(MyCallback.filter(F.foo == 'answer')) # нажатие ответить под сообщ
async def process_answer_press(query: CallbackQuery, callback_data: MyCallback, bot: Bot, state: FSMContext):
    await query.answer()  # отключаем анимацию кнопки
    sender = query.from_user.id # id пользователя
    recipient = callback_data.bar # id того - кому отвечаем
    await state.update_data(recipient=recipient, sender=sender) # save id's in state
    await state.update_data(answer='answer') # flag 'answer' save to state
    await state.set_state(FSM.fill_message) # устанавливаем состояние отправки сообщения
    await bot.send_message( # просим написать ответ
        sender,
        text = lexicon_ru.LEXICON_RU['answer_text'],
        reply_markup = create_inline_cancel()
    )
