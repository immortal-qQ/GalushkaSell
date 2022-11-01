from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import re
import os


# https://tproger.ru/translations/finite-state-machines-theory-and-implementation/
class CreatePost(StatesGroup):
    waiting_for_category = State()
    waiting_for_subcategory = State()
    waiting_for_post_header = State()
    waiting_for_post_description = State()
    waiting_for_photo = State()
    waiting_for_post_price = State()


async def category_choosing(message: types.Message):  # "Продать" | Выбор категорий
    # print(message.text, 'IN sell_start')
    headers = {
        'Content-Type': 'application/json'
    }
    url = f"http://127.0.0.1:8000/bot_users/{message.from_user.id}"
    response = requests.request("GET", url, headers=headers)
    if response.json()["state"] == 'A':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Съедобные товары", "Несъедобные товары", "Услуги", "Назад в меню"]
        keyboard.add(*buttons)
        await message.answer(
            "Создание нового объявления начато успешно!\n\nВыберите подходящую категорию для продажи Вашего товара:",
            reply_markup=keyboard)
        await CreatePost.waiting_for_category.set()  # становимся в состояние выбора подкатегории
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Abuse это плохо!", reply_markup=keyboard)


async def category_chosen(message: types.Message, state: FSMContext):  # Выбор подкатегорий
    # print(message.text, 'IN sell_manage')
    if message.text == 'Съедобные товары':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Алкоголь 🍷", "Аптека 💊", "Напитки 🥤", "Молочная продукция 🥛", "Другие съедобные товары ❔", "Отмена ❌"]
        keyboard.add(*buttons)
        await message.answer("Выберите подходящую подкатегорию для продажи Вашего товара:", reply_markup=keyboard)
        await CreatePost.waiting_for_subcategory.set()  # становимся в состояние I

    elif message.text == 'Несъедобные товары':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Табачка 🚬", "Аптека 🥡", "Другие несъедобные товары ❔", "Отмена ❌"]
        keyboard.add(*buttons)
        await message.answer("Выберите подходящую подкатегорию для продажи Вашего товара:", reply_markup=keyboard)
        await CreatePost.waiting_for_subcategory.set()

    elif message.text == 'Услуги':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Другие услуги ❔", "Отмена ❌"]
        keyboard.add(*buttons)
        await message.answer("Выберите подходящую подкатегорию для продажи Вашего товара:", reply_markup=keyboard)
        await CreatePost.waiting_for_subcategory.set()

    elif message.text == 'Назад в меню':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)


async def subcategory_chosen(message: types.Message, state: FSMContext):  # state "category_chosen"
    # print(message.text, 'IN final_category')
    if message.text == 'Отмена ❌':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)
        return

    available_names = ["Алкоголь 🍷", "Аптека 💊", "Напитки 🥤", "Молочная продукция 🥛",
                       "Другие съедобные товары ❔", "Табачка 🚬", "Аптека 🥡",
                       "Другие несъедобные товары ❔", "Другие услуги ❔"]
    if message.text in available_names:
        await state.update_data(person_id=message.from_user.id, chosen_category=message.text)
    else:
        print('Error: Category key word was not recognized')
        await message.answer("Проверьте корректность ввода категории!")
        return

    await state.update_data(chosen_category=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Отмена ❌"]
    keyboard.add(*buttons)
    await message.answer("Введите название вашего объявления:", reply_markup=keyboard)
    await CreatePost.waiting_for_post_header.set()  # становимся в состояние


# Обратите внимание: есть второй аргумент
async def post_header_chosen(message: types.Message, state: FSMContext):
    # print(message.text, 'IN post_header_chosen')
    if message.text == 'Отмена ❌':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)
        return
    # Для простых шагов можно не указывать название состояния, обходясь next()
    await state.update_data(chosen_header=message.text)
    await CreatePost.next()  # Встаём в состояние III

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Отмена ❌"]
    keyboard.add(*buttons)
    # reply_markup=types.ReplyKeyboardRemove()
    await message.answer("Введите подробное описание к Вашему объявлению:", reply_markup=keyboard)


#
async def post_description_chosen(message: types.Message, state: FSMContext):
    # print(message.text, 'IN post_description_chosen')
    if message.text == 'Отмена ❌':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)
        return
    await state.update_data(chosen_description=message.text)
    await CreatePost.waiting_for_photo.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Отмена ❌"]
    keyboard.add(*buttons)
    await message.answer("Отправьте изображение, которое характеризует ваше объявление:", reply_markup=keyboard)


# Типы содержимого тоже можно указывать по-разному.
async def photo_chosen(message: types.Message, state: FSMContext):
    # print(message.text, 'IN photo_chosen')
    # print(message.content_type)
    # создадим клавиатуру для отмены создания объявления
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Отмена ❌"]
    keyboard.add(*buttons)

    if message.text == 'Отмена ❌':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)
        return
    if message.content_type == 'photo':

        path = os.path.join("bot_data", "temp_photo", f'{message.from_user.id}.jpg')
        await message.photo[-1].download(destination_file=path)
        # print(message.photo[-1].file_id, message.photo[-1].file_unique_id)

        await state.update_data(chosen_photo=os.path.join("bot_data", "temp_photo", f"{message.from_user.id}.jpg"))
        await CreatePost.next()
        await message.answer("Теперь введите сумму (в рублях) для продажи:", reply_markup=keyboard)
        return
    # если было введено что-то помимо картинки или Отмена ❌
    await message.answer("Некорректное значение!", reply_markup=keyboard)
    return


async def post_price_chosen(message: types.Message, state: FSMContext):
    # print(message.text, 'IN post_price_chosen')
    if message.text == 'Отмена ❌':
        await state.finish()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Купить", "Продать", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Создание объявления успешно отменено.\nВоспользуйтесь клавиатурой...",
                             reply_markup=keyboard)
        return
    if re.fullmatch(r'\d{1,7}', message.text) is None:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Отмена ❌"]
        keyboard.add(*buttons)
        await message.answer("Некорректное значение! Введите только число!", reply_markup=keyboard)
        return
    await state.update_data(chosen_price=message.text.lower())

    user_data = await state.get_data()  # в хранилище т к записали в хранилище
    categories = {
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
    # POST
    url = "http://127.0.0.1:8000/posts/"
    payload = {
        'author': user_data['person_id'],
        'category': categories[user_data['chosen_category']],
        'price': user_data['chosen_price'],
        'header': user_data['chosen_header'],
        'description': user_data['chosen_description'],
        'status': "A"
    }

    files = [
        ('image', (f"{user_data['person_id']}.jpg",  # join'им путь до исполняемого файла и путь от него до фотки юзера
                   open(os.path.join("bot_data", "temp_photo", f'{user_data["person_id"]}.jpg'), 'rb'),
                   'image/jpeg'))
    ]
    headers = {
            'Authorization': 'Basic YWRtaW46YWRtaW4=',
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    # print(response.text)
    # print(user_data) # то, что насобирал FSM

    buttons = [
        types.InlineKeyboardButton(text="Посмотреть результат", callback_data=f"edit_{response.json()['id']}")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.answer('Объявление успешно создано!', reply_markup=keyboard)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Купить", "Продать", "Назад в главное меню"]
    keyboard.add(*buttons)
    await message.answer("Что пожелаете?", reply_markup=keyboard)
    await state.finish()


# про фильтры подробнее:
# https://docs.aiogram.dev/en/latest/dispatcher/filters.html#making-own-filters-custom-filters
def register_handlers_post(dp: Dispatcher):
    dp.register_message_handler(category_choosing, lambda msg: msg.text.lower() == 'продать', state="*")
    dp.register_message_handler(category_chosen, state=CreatePost.waiting_for_category)
    dp.register_message_handler(subcategory_chosen, state=CreatePost.waiting_for_subcategory)
    dp.register_message_handler(post_header_chosen, state=CreatePost.waiting_for_post_header)
    dp.register_message_handler(post_description_chosen, state=CreatePost.waiting_for_post_description)
    dp.register_message_handler(photo_chosen, content_types=["text", "photo"], state=CreatePost.waiting_for_photo)
    dp.register_message_handler(post_price_chosen, state=CreatePost.waiting_for_post_price)
