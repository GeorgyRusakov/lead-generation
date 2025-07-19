from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from handlers import admin_id
from db import get_all_users, get_last10_users

import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials


router = Router()


@router.message((F.from_user.id == admin_id) & (F.text == '👥stats'))
async def admin_stats(message: Message):
    user_data = await get_all_users()
    await message.answer(text=f'На текущий момент в базе данных содержатся записи о {len(user_data)} пользователях')


@router.message((F.from_user.id == admin_id) & (F.text == '🧑‍🧑‍🧒last10'))
async def admin_last10(message: Message):
    user_data = await get_last10_users()
    text = f'Вот список последних 10 пользователей:\n\n'
    for user in user_data:
        text += f'<code>{user["telegram_id"]} - {user["username"]}</code>\n'
    await message.answer(text)


@router.message((F.from_user.id == admin_id) & (F.text == '📁export'))
async def admin_stats(message: Message):
    user_data = await get_all_users()
    with open('user_doc.csv', 'w') as f:
        writer = csv.DictWriter(
            f, fieldnames=list(user_data[0].keys()), quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for d in user_data:
            writer.writerow(d)
    await message.answer_document(document=FSInputFile(path='user_doc.csv'),
                                  caption='Вот список пользователей в формате "csv".\n'
                                  'Данные также появятся в google таблице')

    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('gs_credentials.json', scope)
    client = gspread.authorize(credentials)

    sheet = client.open("Table1").sheet1
    users = list()
    for user in user_data:
        users.append(list(user.values()))
    sheet.insert_rows(users)

    os.remove('user_doc.csv')









