from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import os
import re


class EditPost(StatesGroup):
    waiting_for_value = State()


async def send_random_value(call: types.CallbackQuery, state: FSMContext):  # update_{key}_{post_id}

    url = f"http://127.0.0.1:8000/posts/{call.data.split('_')[2]}/update_{call.data.split('_')[1]}/"
    # print(url)

    keys = {
        'price': 'Укажите новую цену вашего объявления или отмените редактирование объявления, '
                 'нажав на соответствующую кнопку:',
        'description': 'Укажите новое описание вашего объявления или отмените редактирование объявления, '
                       'нажав на соответствующую кнопку:',
        'header': 'Укажите новое название вашего объявления или отмените редактирование объявления, '
                  'нажав на соответствующую кнопку:',
        'status': 'Выберите новый статус вашего объявления или отмените редактирование объявления, '
                  'нажав на соответствующую кнопку:',
        'image': 'Укажите новое изображение вашего объявления или отмените редактирование объявления, '
                  'нажав на соответствующую кнопку:',
    }
    # buttons = [
    #     types.InlineKeyboardButton(text="Отменить",
    #                                callback_data=f"edit_{call.data.split('_')[2]}")
    # ]
    # keyboard = types.InlineKeyboardMarkup(row_width=2)
    # keyboard.add(*buttons)

    await state.update_data(address=url)  # в address хранится url запрос на изменение чего-то
    await EditPost.waiting_for_value.set()
    #
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Активно", "Приостановлено", "Отмена"] if str(call.data.split('_')[1]) == 'status' \
        else ["Отмена"]
    keyboard.add(*buttons)

    await call.message.answer(keys[str(call.data.split('_')[1])],
                              reply_markup=keyboard) #TODO скорее всего добавить parsemode и вкинуть url, чтобы можно было узнать а)Статус, если его меняем б) Потребность чекать цифру, если меняем цену
    await call.answer()


async def get_value(message: types.Message, state: FSMContext):
    # print(message.text, message.content_type)

    user_data = await state.get_data()  # достаём адрес запроса на обновление
    # print(user_data)
    url = user_data['address']
    updated = True  # апдейт прошёл без ошибок

    if message.content_type == "photo":
        path = os.path.join("bot_data", "temp_photo", f'{message.from_user.id}.jpg')
        await message.photo[-1].download(destination_file=path)
        files = [
            ('image',
             (f"{message.from_user.id}.jpg",  # join путь до исполняемого файла и путь от него до фотки юзера
              open(os.path.join("bot_data", "temp_photo", f'{message.from_user.id}.jpg'), 'rb'),
              'image/jpeg'))
        ]
        headers = {
            'Authorization': 'Basic YWRtaW46YWRtaW4=',
        }
        response = requests.request("POST", url, headers=headers, data={}, files=files)
        # print(response.text)
        await state.finish()

    elif message.text == 'Отмена':
        post_id = (str(url.split('posts/')[1]).split('/')[0])
        buttons = [
            types.InlineKeyboardButton(text="Вернуться к редактированию объявления ✏️",
                                       callback_data=f"edit_{post_id}")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        await message.answer('Редактирование объявления успешно отменено!', reply_markup=keyboard)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Начать работу!", "Настройки⚙️", "Назад в главное меню"]
        keyboard.add(*buttons)
        await message.answer("Вы можете воспользоваться клавиатурой 🙃", reply_markup=keyboard)

        await state.finish()
        return
    else:
        await state.update_data(value=message.text)
        statuses = {
            'Активно': 'A',
            'Приостановлено': 'S'
        }
        try:
            data = {
                str(url.split('_')[1][0:len(url.split('_')[1]) - 1]): statuses[message.text]
            }
        except KeyError:
            data = {
                str(url.split('_')[1][0:len(url.split('_')[1]) - 1]): message.text
            }

        # проверка на число, если меняем цену
        try:
            if re.fullmatch(r'\d{1,7}', data['price']) is None:
                updated = False
            else:
                data['price'] = int(data['price'])
                error = data[' ']
        except KeyError:
            response = requests.request("POST", url, auth=('admin', 'admin'), data=data)
            # print(url, data, response.status_code)

        await state.finish()

    # Возвращаем сообщение об усешном объявлении и возможность просмотреть результат (выход в main по callback)
    post_id = (str(url.split('posts/')[1]).split('/')[0])
    buttons = [
        types.InlineKeyboardButton(text="Просмотреть результат!", callback_data=f"edit_{post_id}")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    if updated:
        await message.answer('Данные в объявлении успешно обновлены ✅', reply_markup=keyboard)
    else:
        await message.answer('Было введено некорректное значение ❌', reply_markup=keyboard)


def register_handlers_edit(dp: Dispatcher):
    dp.register_callback_query_handler(send_random_value, lambda call: call.data.startswith('update'), state="*")  # Text(startswith="update_")
    dp.register_message_handler(get_value, content_types=["text", "photo"], state=EditPost.waiting_for_value)
