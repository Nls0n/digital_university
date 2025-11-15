import asyncio
import structlog
from enum import Enum
from maxapi import Bot, Dispatcher
from maxapi.filters import F
from maxapi.types import Command, BotStarted, MessageCreated, MessageCallback
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import LinkButton, CallbackButton
from dotenv import load_dotenv
import os
from sqlalchemy import select, update, delete
from digital_university_back.app.database import engine
from digital_university_back.app.models import *
import requests

load_dotenv()
LOG = structlog.get_logger()
bot = Bot(os.getenv('MAX_TOKEN'))
dp = Dispatcher()

async def get_main_menu(role):
    builder = InlineKeyboardBuilder()

    if role == "applicant":
        builder.row(CallbackButton(text="🎓 Поступление", payload="@applicant-admission"))
        builder.row(CallbackButton(text="📅 Дни открытых дверей", payload="@applicant-open-days"))
        builder.row(CallbackButton(text="🏫 Информация о вузе", payload="@applicant-university-info"))

    elif role == "student":
        builder.row(CallbackButton(text="📚 Расписание", payload="@student-schedule"))
        builder.row(CallbackButton(text="🎯 Проектная деятельность", payload="@student-projects"))
        builder.row(CallbackButton(text="📋 Деканат", payload="@student-deanery"))

    elif role == "professor":
        builder.row(CallbackButton(text="✈️ Командировки", payload="@professor-business-trips"))
        builder.row(CallbackButton(text="🏖️ Отпуска", payload="@professor-vacations"))

    return builder


@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Отправьте команду /start'
    )


@dp.message_created(Command("start"))
async def start_handler(event: MessageCreated):
    max_id = event.from_user.user_id
    request = requests.get(f"http://gutech-nelson.amvera.io/digital_university/api/v1/presense/{max_id}")
    presence = bool(request.json())
    print(presence)

    if not presence:

        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/assign/{max_id}")

        builder_auto = InlineKeyboardBuilder()
        builder_auto.row(CallbackButton(text="🎓 Абитуриент", payload="@auto-set-role-applicant"))
        builder_auto.row(CallbackButton(text="👨‍🎓 Студент", payload="@auto-set-role-student"))
        builder_auto.row(CallbackButton(text="👨‍🏫 Сотрудник", payload="@auto-set-role-professor"))

        await event.message.answer(
            f"👋 Добро пожаловать в Цифровой ВУЗ, {event.from_user.first_name}!\n"
            "Я вижу вас впервые, так что давайте познакомимся!\n"
            "Выберите вашу роль для доступа к соответствующим сервисам:",
            attachments=[builder_auto.as_markup()]
        )

    else:
        builder_con = InlineKeyboardBuilder()
        builder_con.row(CallbackButton(text="➡️ Продолжить", payload="@auto-success"))

        await event.message.answer(
            f"👋 Добро пожаловать в Цифровой ВУЗ, {event.from_user.first_name}!\n"
            "Нажмите 'ПРОДОЛЖИТЬ' для перехода к сервисам:",
            attachments=[builder_con.as_markup()]
        )

@dp.message_callback(F.callback.payload.startswith("@auto-"))
async def role_selection_handler(event: MessageCallback):
    payload = event.callback.payload
    user_first_name = event.from_user.first_name
    max_id = event.from_user.user_id

    if payload == "@auto-set-role-applicant":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/assign/{max_id}/applicant")
    elif payload == "@auto-set-role-student":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/assign/{max_id}/student")
    elif payload == "@auto-set-role-professor":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/assign/{max_id}/professor")

    request = requests.get(f"http://gutech-nelson.amvera.io/digital_university/api/v1/student/{max_id}/role")
    role = str(request.json()['role'])
    print(role)

    roles = {'applicant': 'Абитуриент', 'student': 'Студент', 'professor': 'Сотрудник'}

    menu = await get_main_menu(role)

    await event.message.edit(
        text=f"{roles[role]} {user_first_name}\n\nВыберите нужный раздел:",
        attachments=[menu.as_markup()]
    )


@dp.message_callback(F.callback.payload.startswith("@act-applicant-"))
async def applicant_handler(event: MessageCallback):
    payload = event.callback.payload
    max_id = event.from_user.user_id

    if payload == "@act-applicant-application":

        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/application")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📝 **Подать заявление**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )


    if payload == "@act-applicant-check-status":

        request = requests.get(f"http://localhost::8000/digital_university/api/v1/statements/{max_id}")
        string = request.text
        print(string)

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📝 **Статус заявления**\n\n"
                 f"Статус: {string}\n.",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-applicant-sign-up-on-open-day":

        import random

        name = random.randint(1, 10**3)

        requests.put(f"http://gutech-nelson.amvera.io/digital_university/api/v1/opendoordays/{name}/student/{max_id}")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text=f"📅 **Записаться на день открытых дверей**\n\n"
                "Вы успешно записались на день открытых дверей.\n",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-applicant-about-university":

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text=f"🏫 **Информация об университете**\n\n"
                "Информация об университете...\n",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-applicant-studying-programmes":

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text=f"🏫 **Информация об образовательных программах**\n\n"
                 "Информация об образовательных программах...\n",
            attachments=[builder.as_markup()]
        )


@dp.message_callback(F.callback.payload.startswith("@act-student-"))
async def student_handler(event: MessageCallback):
    payload = event.callback.payload
    max_id = event.from_user.user_id

    if payload == "@act-student-current-schedule":

        request = requests.get(f"http://gutech-nelson.amvera.io/digital_university/api/v1/schedule/student/{max_id}")
        data = request.json()

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        result_text = "Ваше расписание:\n\n"

        for day_name in days:
            day_schedule = getattr(data, day_name)
            if day_schedule:
                result_text += f"📅 {day_name.capitalize()}:\n"
                for pair in day_schedule:
                    result_text += f"• {pair.subject} ({pair.start.strftime('%H:%M')}-{pair.end.strftime('%H:%M')})\n"
                    result_text += f"  Преподаватель: {pair.professor}\n"
                    result_text += f"  Аудитория: {pair.audience}\n\n"

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text=result_text,
            attachments=[builder.as_markup()]
        )


    if payload == "@act-student-available-project":

        request = requests.get(f"http://gutech-nelson.amvera.io/digital_university/api/v1/projects")
        lst = request.json()

        result_text = "*** Доступные проекты:\n"
        i = 0

        for project in lst:
            i += 1
            result_text += f"{i}. {project}\n"

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text=result_text,
            attachments=[builder.as_markup()]
        )

    if payload == "@act-student-studying-payment":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/inquiry")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="💳 **Оплата обучения**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-student-academic-vacation":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/payment")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📝 **Академический отпуск**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-student-translation":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/inquiry")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🚗 **Перевод**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )


@dp.message_callback(F.callback.payload.startswith("@act-professor-"))
async def professor_handler(event: MessageCallback):
    payload = event.callback.payload
    max_id = event.from_user.user_id

    if payload == "@act-staff-business-trip":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/business-trips")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="✈️ **Запрос командировки**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )

    if payload == "@act-staff-vacation":
        requests.post(f"http://gutech-nelson.amvera.io/digital_university/api/v1/statements/{max_id}/vacations")

        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏖️ **Запрос отпуска**\n\n"
                 "Заявление успешно подано.",
            attachments=[builder.as_markup()]
        )


@dp.message_callback()
async def main_menu_handler(event: MessageCallback):
    payload = event.callback.payload
    max_id = event.from_user.user_id
    user_first_name = event.from_user.first_name

    await event.answer()

    if payload == "@applicant-admission":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Подать заявление", payload="@act-applicant-application"))
        builder.row(CallbackButton(text="📊 Проверить статус", payload="@act-applicant-check-status"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🎓 **Поступление**\n\n"
                 "Здесь вы можете подать заявление на поступление, проверить статус заявления.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@applicant-open-days":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Записаться", payload="@act-applicant-sign-up-on-open-day"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📅 **Дни открытых дверей**\n\n"
                 "Запишитесь на день открытых дверей!",
            attachments=[builder.as_markup()]
        )

    elif payload == "@applicant-university-info":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏫 О вузе", payload="@act-applicant-about-university"))
        builder.row(CallbackButton(text="📊 Программы", payload="@act-applicant-studying-programmes"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏫 **Информация о вузе**\n\n"
                 "Узнайте больше о нашем вузе и образовательных программах.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-schedule":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Текущее расписание", payload="@act-student-current-schedule"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📚 **Расписание**\n\n"
                 "Просматривайте актуальное расписание.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-projects":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📋 Доступные проекты", payload="@act-student-available-projects"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@act-all-main-menu"))

        await event.message.edit(
            text="🎯 **Проектная деятельность**\n\n"
                 "Присоединяйтесь к существующим проектам",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-deanery":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💳 Оплата обучения", payload="@act-student-studying-payment"))
        builder.row(CallbackButton(text="📝 Академический отпуск", payload="@act-student-academic-vacation"))
        builder.row(CallbackButton(text="🚗 Перевод", payload="@act-student-translation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📋 **Деканат**\n\n"
                 "Оформляйте справки, оплачивайте обучение и подавайте заявления "
                 "на академический отпуск или перевод.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@staff-business-trips":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Оформить командировку", payload="@act-staff-business-trip"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="✈️ **Командировки**\n\n"
                 "Оформляйте и согласовывайте заявки на командировки, "
                 "а также подавайте отчеты по возвращении.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@staff-vacations":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏖️ Оформить отпуск", payload="@act-staff-vacation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏖️ **Отпуска**\n\n"
                 "Оформляйте и согласовывайте заявки на отпуск.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@all-main-menu":
        request = requests.get(f"http://gutech-nelson.amvera.io/digital_university/api/v1/student/{max_id}/role")
        role = str(request.json()['role'])
        print(role)

        roles = {'applicant': 'Абитуриент', 'student': 'Студент', 'professor': 'Сотрудник'}

        menu = await get_main_menu(role)

        await event.message.edit(
            text=f"{roles[role]} {user_first_name}\n\nВыберите нужный раздел:",
            attachments=[menu.as_markup()]
        )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())