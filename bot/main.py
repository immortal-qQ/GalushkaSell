# thx to https://mastergroosha.github.io/telegram-tutorial-2/
# his repo: https://github.com/MasterGroosha/telegram-tutorial-2/tree/master/code
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text

# справка: https://docs-python.ru/packages/modul-requests-python/obekt-otvet-servera-response/
import requests

import json
# import app
from .app.handlers.sell_form import register_handlers_post
from .app.handlers.post_edit import register_handlers_edit
from .app.handlers.common import register_handlers_common
from .app.config_reader import load_config

from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt

from telegram_bot_pagination import InlineKeyboardPaginator
from telegram_bot_pagination import InlineKeyboardButton

import os

# # Объект бота
# bot = Bot(token="2079878449:AAFVO8sV6N2A7EJGIfrGmlijX8AwBEime0A")
# # Диспетчер для бота
# dp = Dispatcher(bot, storage=MemoryStorage())

# локаль
# http://127.0.0.1:8000/

# admin local
# http://127.0.0.1:8000/admin/
# admin | admin

# Парсинг файла конфигурации
# https://habr.com/ru/post/485236/
config = load_config("bot/config/bot.ini")

# Объявление и инициализация объектов бота и диспетчера
# https://docs.aiogram.dev/en/latest/dispatcher/index.html
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/start", description="Главное меню.")
        # types.BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


# словарь для расшифровки системных обозначений категорий
categories = {
    2: "Алкоголь 🍷",
    13: "Аптека 💊",
    5: "Напитки 🥤",
    4: "Молочная продукция 🥛",
    6: "Другие съедобные товары ❔",
    8: "Табачка 🚬",
    3: "Аптека 🥡",
    9: "Другие несъедобные товары ❔",
    11: "Другие услуги ❔",
    # 13: None# аптека съедобные
}
reversed_categories = {
    "Алкоголь 🍷": 2,
    "Аптека 💊": 13,
    "Напитки 🥤": 5,
    "Молочная продукция 🥛": 4,
    "Другие съедобные товары ❔": 6,
    "Табачка 🚬": 8,
    "Аптека 🥡": 3,
    "Другие несъедобные товары ❔": 9,
    "Другие услуги ❔": 11
}

statuses = {
    'A': 'Активно',
    'S': 'Приостановлено'
}


# декоратор для каждого хэндлера
@dp.message_handler(commands="start")
@dp.message_handler(Text(equals=["Назад в главное меню"]))
async def start(message: types.Message):
    # message - справка: https://docs.aiogram.dev/en/latest/telegram/types/message.html

    uid = message.from_user.id  # unique id
    tag = message.from_user.username  # tag
    fname = message.from_user.first_name
    lname = message.from_user.last_name
    if fname is None:
        fname = ' '
    if lname is None:
        lname = ' '
    if tag is None:
        tag = f'empty_tag_{uid}'

    # print(f"[{uid}] [{tag}] [{fname}] [{lname}]")
    buttons = [
        types.InlineKeyboardButton(text="Мои объявления", callback_data=f"own_{uid}"),
        types.InlineKeyboardButton(text="Избранное❤️", callback_data=f"favourite_{uid}")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    # user registration
    url = "http://127.0.0.1:8000/bot_users/"

    payload = json.dumps({
        "tg_id": uid,
        "nickname": tag,
        "first_name": fname,  # message.from_user.first_name if message.from_user.first_name non None else ' '
        "last_name": lname,
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, auth=('admin', 'admin'), headers=headers, data=payload)
    # print(response.text)
    # достаём ссылку на vk
    url = f"http://127.0.0.1:8000/bot_users/{uid}"
    response = requests.request("GET", url, headers=headers)
    # print(response.json())
    if response.json()["state"] == 'A':
        out = f"Добро пожаловать, {tag if not 'empty_tag' in tag else fname}! \n\n" \
              f"Ваш уникальный номер - {uid}.\n\n" \
              f"Ваш профиль на vk.com для связи с покупателем/продавцом - {response.json()['vk_link']}\n\n" \
              f"❗Не забывайте указывать ссылку на Ваш профиль ВК, чтобы обеспечить возможность общения.\n\n----\n" \
              f"Note: Именно Ваш уникальный номер учётной записи обеспечивает возможность публикации, " \
              f"изменения и удаления Ваших объявлений только Вами."
        await message.answer(out, reply_markup=keyboard, disable_web_page_preview=True)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Начать работу!", "Настройки⚙️"]
        keyboard.add(*buttons)
        await message.answer("Воспользуйтесь клавиатурой в самом низу экрана 🙃", reply_markup=keyboard)
    else:
        out = f"Доброго времени суток, {tag if not 'empty_tag' in tag else fname}.\n\n" \
              f"Ваш профиль в боте был заблокирован за нарушение правил ❌.\n\n" \
              f"Вы можете только просматривать объявления других пользователей. " \
              f"Для разблокировки обращайтесь в поддержку @GSellSupport"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Начать работу!"]
        keyboard.add(*buttons)
        await message.answer(out, reply_markup=keyboard)


@dp.message_handler(Text(equals=["Назад в меню", "Начать работу!"]))
async def case(message: types.Message):
    headers = {
        'Content-Type': 'application/json'
    }
    url = f"http://127.0.0.1:8000/bot_users/{message.from_user.id}"
    response = requests.request("GET", url, headers=headers)
    if response.json()["state"] == 'A':
        buttons = ["Купить", "Продать", "Назад в главное меню"]
    else:
        buttons = ["Купить", "Назад в главное меню"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*buttons)
    await message.answer("Что пожелаете?", reply_markup=keyboard)


# buy beginning
@dp.message_handler(Text(equals=["Купить", "Назад в меню выбора"]))
async def buy(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Съедобные товары", "Несъедобные товары", "Услуги", "Назад в меню"]
    keyboard.add(*buttons)
    await message.answer("Выберите подходящую категорию:", reply_markup=keyboard)


@dp.message_handler(Text(equals="Съедобные товары"))
async def edible(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Алкоголь 🍷", "Аптека 💊", "Напитки 🥤", "Молочная продукция 🥛", "Другие съедобные товары ❔", "Назад в меню выбора"]
    keyboard.add(*buttons)
    await message.answer("Выберите подходящую категорию:", reply_markup=keyboard)


@dp.message_handler(Text(equals="Несъедобные товары"))
async def inedible(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Табачка 🚬", "Аптека 🥡", "Другие несъедобные товары ❔", "Назад в меню выбора"]
    keyboard.add(*buttons)
    await message.answer("Выберите подходящую категорию:", reply_markup=keyboard)


@dp.message_handler(Text(equals="Услуги"))
async def services(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Другие услуги ❔", "Назад в меню выбора"]
    keyboard.add(*buttons)
    await message.answer("Выберите подходящую категорию:", reply_markup=keyboard)


@dp.message_handler(Text(equals=["Алкоголь 🍷", "Аптека 💊", "Напитки 🥤", "Молочная продукция 🥛",
                                 "Другие съедобные товары ❔", "Табачка 🚬", "Аптека 🥡",
                                 "Другие несъедобные товары ❔", "Другие услуги ❔"]))
async def listing(message: types.Message):

    url = f"http://127.0.0.1:8000/posts/?status=A&category={reversed_categories[message.text]}"
    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data={})
    # print(response.json())
    # join'им путь до исполняемого файла и путь от него до локального хранилища пользовательского запроса на листинг
    with open(os.path.join("bot_data", "requested_posts", f"{message.from_user.id}.json"), 'w', encoding='utf-8') as f:
        # TODO фильтрацию и по активности и по категории см.выше
        json.dump({'posts': response.json()}, f)
    if not response.json():
        await message.answer("Нет объявлений в выбранной категории!")
    else:
        await send_post_page(message, page=1, user_id=message.from_user.id)
        # print(message.text)


# user_id == const
# pagination
# https://pypi.org/project/python-telegram-bot-pagination/
# https://habr.com/ru/post/501812/
# https://github.com/ksinn/python-telegram-bot-pagination
async def send_post_page(message, page, user_id):
    path = os.path.join("bot_data", "requested_posts", f"{user_id}.json")
    # print(path)
    with open(path, 'r', encoding='utf-8') as f:
        post_pages = json.load(f)['posts']
    # print('Title:', post_pages)
    # print('Size:', len(post_pages))

    paginator = InlineKeyboardPaginator(
        len(post_pages),
        current_page=page,
        data_pattern='post#{page}'  # always CONST
    )
    line = post_pages[page-1]  # в строчке хранится одно из объявлений выбранной для листинга категории
    # print(line)
    paginator.add_after(
        InlineKeyboardButton('❤ В избранное️', callback_data=f"addfavour_{line['id']}_{user_id}"), # by user
        InlineKeyboardButton('💔 Удалить из избранного', callback_data=f"remfavour_{line['id']}_{user_id}")
    )  # by user

    headers = {
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", line['image'], headers=headers, data={})
    buttons = [
        types.InlineKeyboardButton(text="Подробнее...", callback_data=f"detail_{line['id']}")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    # GET / posts / < id > / favourite_by
    # Возвращает список объектов вида {user = < user_id >, post = < id >}
    fav_by_url = f"http://127.0.0.1:8000/posts/{line['id']}/favourite_by"
    fav_by = requests.request('GET', fav_by_url, auth=('admin', 'admin'), headers={})
    # print(fav_by_url, fav_by.status_code, fav_by.text, len(fav_by.json()))

    # собираем объявления
    # достаём ссылку на VK у продавца и чекаем наличие тега для адресации
    url = f"http://127.0.0.1:8000/bot_users/{line['author']}"
    author_data_response = requests.request('GET', url, headers=headers).json()
    author_tag = f"\n\n[Написать в Telegram](https://t.me/{author_data_response['nickname']})\n"
    # print(author_tag)
    await message.answer_photo(photo=response.content,  # ограничение на 1024 символа TODO
                               caption=f"Название: {line['header']}\n\n"
                                       f"Описание: {line['description']}\n\n"
                                       f"Цена: {str(line['price'])}₽\n\n"
                                       f"Статус: {statuses[line['status']]}\n\n"
                                       f"[Написать ВК]({author_data_response['vk_link']})"
                                       f"{author_tag if not 'empty_tag_' in author_tag else ''}"
                                       f"\n❤ Лайков: ️{len(fav_by.json())}"  # author id
                                       f"[\u2002](http://127.0.0.1:8000/posts/{line['id']})"  # post id
                                       f"[\u2002](http://127.0.0.1:8000/bot_users/{line['author']})",

                               disable_notification=True,
                               reply_markup=paginator.markup,
                               parse_mode='Markdown')

# f"[](Уникальный номер объявления: {line['id']})",


# # подробнее про callbacks
# # https://docs.aiogram.dev/en/latest/telegram/types/callback_query.html
@dp.callback_query_handler(Text(startswith="post"))
async def posts_page_callback(call):
    page = int(call.data.split('#')[1])
    user_id = call.from_user.id  # готово
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    # print("call.message", page, user_id)
    await send_post_page(call.message, page, user_id)


@dp.callback_query_handler(Text(startswith="addfavour"))
async def posts_page_favour(call):
    # print(call.data)
    url = f"http://127.0.0.1:8000/bot_users/{int(call.data.split('_')[2])}/add_favourite/"
    response = requests.request("POST", url, auth=('admin', 'admin'), headers={},
                                data={'add': int(int(call.data.split('_')[1]))})
    # print(f'Code {response.status_code}')
    if response.status_code == 200:
        await call.answer('Объявление успешно добавлено в избранное ❤️')
    else:
        await call.answer('Объявление уже в избранном ❤️')


@dp.callback_query_handler(Text(startswith="remfavour"))
async def posts_page_favour(call):
    url = f"http://127.0.0.1:8000/bot_users/{int(call.data.split('_')[2])}/remove_favourite/"
    response = requests.request("POST", url, auth=('admin', 'admin'), headers={},
                                data={'remove': int(int(call.data.split('_')[1]))})
    if response.status_code == 200:
        await call.answer('Объявление успешно удалено из избранного 💔️')
    else:
        await call.answer('Объявление отсутствует в избранном ❗️️')
# end of buy


@dp.message_handler(Text(equals=["Настройки⚙️"]))
async def edit_profile(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Ссылка на VK", "Назад в главное меню"]
    keyboard.add(*buttons)
    await message.answer("Выберите раздел:", reply_markup=keyboard)


@dp.message_handler(Text(equals=["Ссылка на VK"]))
async def edit_profile(message: types.Message):
    await message.answer("Вставьте ссылку на ваш профиль VK:\n\n\nWarning:Любые другие ссылки будут проигнорированы.",
                         reply_markup=types.ReplyKeyboardRemove())


# подробнее про regexp (регулярные выражения)
# https://habr.com/ru/post/349860/
@dp.message_handler(regexp='^(http:\/\/|https:\/\/)?(www.)?(vk\.com|vkontakte\.ru)\/(id\d|[a-zA-Z0-9_.])+$')
async def edit_vk_link(message: types.Message):
    # print(message.text)
    uid = message.from_user.id  # unique id
    tag = message.from_user.username  # tag
    url = f"http://127.0.0.1:8000/bot_users/{uid}/update_vk_link/"
    # print(url)
    payload = json.dumps({
        "vk_link": message.text
    })

    headers = {  # TODO check necessity of Content-Type in headers
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.status_code)
    # print(response.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Назад в главное меню"]
    keyboard.add(*buttons)
    await message.answer("Ссылка изменена успешно!", reply_markup=keyboard)


# листинг объявлений пользователя в развернутом виде (одно сообщение содержит ВСЮ информацию об объявлении)
# инлайн-кнопка редакта под каждым объявлением с data = edit_{post_id}
@dp.callback_query_handler(Text(startswith="own"))
async def list_user_posts(call):

    url = f"http://127.0.0.1:8000/posts?author={call.from_user.id}"  # can be a problem
    # print(url)

    response = requests.request("GET", url, headers={}, data={})

    # print(response.text)

    lines = response.json()   # каждая строчка - данные об одном объявлении юзера в JSON
    if not lines:
        # await call.message.answer("У Вас нет созданных объявлений.")
        await call.answer("У Вас нет созданных объявлений 😔")
        return
    # print(lines[0]['author'])

    # photo = InputFile(os.path.join(os.getcwd(), f"app/handlers/source/329581882.jpg"))
    for i in range(len(lines)):
        response = requests.request("GET", lines[i]['image'], headers={}, data={})
        buttons = [
            types.InlineKeyboardButton(text="Редактировать ✏️", callback_data=f"edit_{lines[i]['id']}"),
            types.InlineKeyboardButton(text="Удалить 🗑", callback_data=f"delete_{lines[i]['id']}")
            ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)

        # print(lines[i])
        fav_by_url = f"http://127.0.0.1:8000/posts/{lines[i]['id']}/favourite_by"
        fav_by = requests.request('GET', fav_by_url, auth=('admin', 'admin'), headers={})

        await call.message.answer_photo(photo=response.content,  # ограничение на 1024 символа TODO
                                        caption=fmt.text(
                                            # fmt.hunderline() - подчеркнуть, fmt.hstrikethrough() - зачеркнуть
                                            fmt.text(fmt.hbold("Название:"), lines[i]['header']),
                                            fmt.text(fmt.hbold("Описание:"), lines[i]['description']),
                                            fmt.text(fmt.hbold("Категория:"), categories[lines[i]['category']]),
                                            fmt.text(fmt.hbold("Цена:"), str(lines[i]['price']) + "₽"),
                                            fmt.text(fmt.hbold("Статус:"), statuses[lines[i]['status']]),
                                            fmt.text(fmt.hbold("❤ Лайков:"), len(fav_by.json())),
                                            sep="\n\n"), parse_mode="HTML", disable_notification=True,
                                        reply_markup=keyboard)
        await call.answer()


# редакт выбранного по инлайн-кнопке объявления (триггер на edit_{post["id"]})
# инлайн-кнопки, в data которых содержится update_KEY_POSTID
# кнопки в низу экрана для выхода в меню
@dp.callback_query_handler(Text(startswith="edit_"))
async def send_random_value(call: types.CallbackQuery):
    # await call.message.answer('АЕ')
    # await call.answer(text=call.data.split('_')[1], show_alert=True)
    url = f"http://127.0.0.1:8000/posts/{call.data.split('_')[1]}"
    response = requests.request("GET", url, headers={}, data={})
    # print(response.text)
    buttons = [
        types.InlineKeyboardButton(text="Название", callback_data=f"update_header_{response.json()['id']}"),
        types.InlineKeyboardButton(text="Описание", callback_data=f"update_description_{response.json()['id']}"),
        types.InlineKeyboardButton(text="Цену", callback_data=f"update_price_{response.json()['id']}"),
        types.InlineKeyboardButton(text="Статус", callback_data=f"update_status_{response.json()['id']}"),
        types.InlineKeyboardButton(text="Картинку", callback_data=f"update_image_{response.json()['id']}")
    ]
    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    await call.message.answer_photo(photo=requests.request("GET", response.json()['image'], headers={}, data={}).content,
                                    caption=fmt.text(
                                        # fmt.hunderline() - подчеркнуть, fmt.hstrikethrough() - зачеркнуть
                                        fmt.text(fmt.hbold("Название:"), response.json()['header']),
                                        fmt.text(fmt.hbold("Описание:"), response.json()['description']),
                                        fmt.text(fmt.hbold("Категория:"), categories[response.json()['category']]),
                                        fmt.text(fmt.hbold("Цена:"), str(response.json()['price']) + "₽"),
                                        fmt.text(fmt.hbold("Статус:"), statuses[response.json()['status']]),
                                        fmt.text(fmt.hbold('--------\n'), fmt.hitalic('Что пожелаете редактировать?'),
                                                 sep=''),
                                        sep="\n\n"), parse_mode="HTML",
                                    reply_markup=keyboard)
    await call.answer()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Начать работу!", "Настройки⚙️", "Назад в главное меню"]
    keyboard.add(*buttons)
    await call.message.answer("Вы можете воспользоваться клавиатурой 🙃", reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="delete_"))
async def delete_post(call: types.CallbackQuery):
    url = f"http://127.0.0.1:8000/posts/{call.data.split('_')[1]}"
    response = requests.request("DELETE", url, auth=('admin', 'admin'), headers={}, data={})
    await call.answer(text="Объявление успешно удалено!\n\nВоспользуйтесь клавиатурой в самом низу экрана...", show_alert=True)


# @dp.callback_query_handler(Text(startswith="update_"))
# async def send_random_value(call: types.CallbackQuery): # update_{key}_{id}
#     pass
@dp.callback_query_handler(Text(startswith="favourite_"))
async def list_favourite_posts(call):
    url = f"http://127.0.0.1:8000/bot_users/{int(call.data.split('_')[1])}/favourite/"
    response = requests.request("GET", url, auth=('admin', 'admin'), headers={})
    # print(url, response.status_code)
    # print(response.json())
    posts = []  # list of jsons
    for i in range(0, len(response.json())):
        url = f"http://127.0.0.1:8000/posts/{response.json()[i]['post']}"
        get_fav_post = requests.request("GET", url, auth=('admin', 'admin'), headers={})
        posts.append(get_fav_post.json())


    # join'им путь до исполняемого файла и путь от него до локального хранилища пользовательского запроса на листинг
    with open(os.path.join("bot_data", "requested_posts", f"{call.from_user.id}.json"), 'w', encoding='utf-8') as f:
        json.dump({'posts': posts}, f)
    if not posts:
        await call.answer("Нет избранных объявлений!")
    else:
        await send_post_page(call.message, page=1, user_id=call.from_user.id )
        await call.answer('Отображены избранные ❤️')

    # {user = < id >, post = < post_id >}


async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    register_handlers_post(dp)  # Регистрация хендлеров FSM для создания нового объявления
    register_handlers_edit(dp)  # Регистрация хендлеров FSM для редактирования выбранного объявления
    # register_handlers_common(dp, config.tg_bot.admin_id)
    register_handlers_common(dp, list(config.tg_bot.admin_id[1:len(config.tg_bot.admin_id)-1].split(', ')))
    # Установка команд бота
    await set_commands(bot)
    await dp.start_polling()


def run_bot():
    asyncio.run(main())


if __name__ == '__main__':
    run_bot()
