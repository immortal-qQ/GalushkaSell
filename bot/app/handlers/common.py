from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter
import json
import requests

# async def cmd_start(message: types.Message, state: FSMContext):
#     await state.finish()
#     await message.answer(
#         "Выберите, что хотите заказать: напитки (/drinks) или блюда (/food).",
#         reply_markup=types.ReplyKeyboardRemove()
#     )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())


# Просто функция, которая доступна только администратору,
# чей ID указан в файле конфигурации.
async def secret_freeze_command(message: types.Message):
    # print(json.loads(message.reply_to_message.as_json())['caption'])
    # rep = message.reply_to_message.as_json()  # old version
    rep = str(message.reply_to_message.as_json().split('http://127.0.0.1:8000/posts/')[1])
    # print(rep)
    url = 'http://127.0.0.1:8000/posts/' + (rep[0:rep.find('"')]) + '/update_status/'
    response = requests.request("POST", url, auth=('admin', 'admin'), headers={}, data={'status': 'S'})
    # print(url, response.status_code)
    await message.answer('Объявление успешно заморожено!')


async def secret_block_command(message: types.Message):
    rep = str(message.reply_to_message.as_json().split('http://127.0.0.1:8000/bot_users/')[1])
    # print(rep)
    url = 'http://127.0.0.1:8000/bot_users/' + (rep[0:rep.find('"')]) + '/update_state/'
    response = requests.request("POST", url, auth=('admin', 'admin'), headers={},
                                data={'state': 'B', 'requested_by': int(message.from_user.id)})

    # (Active | Blocked)
    if response.status_code == 200:
        await message.answer('Пользователь успешно заблокирован 😬!')
    else:
        await message.answer('Недостаточно прав для блокировки данного пользователя!😱')


def register_handlers_common(dp: Dispatcher, admin_id: list):
    # dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
    dp.register_message_handler(secret_freeze_command, IDFilter(user_id=admin_id), commands="freeze")
    dp.register_message_handler(secret_block_command, IDFilter(user_id=admin_id), commands="block")
