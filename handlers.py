from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton,
    InlineKeyboardMarkup, Message
)
from redis.asyncio import Redis
from keyboard_generation import create_inline_kb
from db import add_user, get_user_by_id

redis = Redis(host='localhost')

storage = RedisStorage(redis=redis)

router = Router()


class FSMFillForm(StatesGroup):
    fill_name = State()
    fill_phone = State()
    fill_time = State()


Buttons: dict[str, str] = {
        'btn_1': '12:00',
        'btn_2': '13:00',
        'btn_3': '14:00',
        'btn_4': '15:00',
        'btn_5': '16:00',
        'btn_6': '17:00',
        'btn_7': '18:00'
    }


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='Привет! Это бот для сбора заявок. Расскажи немного о себе'
        'и потом с тобой свяжется администратор.'
             'Отправь команду /fillform и погнали!'
    )


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы прервали заполнение анкеты\n\n'
             'Чтобы снова перейти к заполнению анкеты - '
             'отправьте команду /fillform'
    )
    await state.clear()


@router.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, введите ваше ФИО')
    await state.set_state(FSMFillForm.fill_name)


@router.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите ваш возраст')
    await state.set_state(FSMFillForm.fill_phone)


@router.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'отправьте команду /cancel')


@router.message(StateFilter(FSMFillForm.fill_phone),
            lambda x: x.text.isdigit())
async def process_age_sent(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)

    keyboard = create_inline_kb(1, **Buttons)

    await message.answer(text='Спасибо!\n\nА теперь выберете желаемое время визита',
                         reply_markup=keyboard)
    await state.set_state(FSMFillForm.fill_time)


@router.message(StateFilter(FSMFillForm.fill_phone))
async def warning_not_age(message: Message):
    await message.answer(
        text='Номер должен быть введен целым числом без пробелов и любых знаков препинания\n\n'
             'Попробуйте еще раз\n\nЕсли вы хотите прервать '
             'заполнение анкеты - отправьте команду /cancel'
    )


@router.callback_query(StateFilter(FSMFillForm.fill_time),
                   F.data.in_(list(Buttons.keys())))
async def process_education_press(callback: CallbackQuery, state: FSMContext):
    # Cохраняем данные об образовании по ключу "education"
    await state.update_data(time=callback.data)
    id_user = callback.from_user.id
    data = await state.get_data()
    await add_user(id_user, data['name'], data['phone_number'], data['time'])
    await state.clear()

    await callback.message.edit_text(
        text='Спасибо! Ваши данные сохранены!\n\n'
             'Чтобы посмотреть данные вашей '
             'анкеты - отправьте команду /showdata'

    )


@router.message(StateFilter(FSMFillForm.fill_time))
async def warning_not_education(message: Message):
    await message.answer(
        text='Пожалуйста, пользуйтесь кнопками при выборе времени\n\n'
             'Если вы хотите прервать заполнение анкеты - отправьте '
             'команду /cancel'
    )


@router.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user:
        await message.answer(
            text=f'Имя {user["username"]}\n'
                 f'Номер телефона: {user["phone_number"]}\n'
                 f'Время приема: {user["time"]}\n'

        )
    else:
        # Если анкеты пользователя в базе нет - предлагаем заполнить
        await message.answer(
            text='Вы еще не заполняли анкету. Чтобы приступить - '
            'отправьте команду /fillform'
        )


