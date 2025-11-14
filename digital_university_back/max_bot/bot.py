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
        builder.row(CallbackButton(text="💼 Карьера", payload="@student-career"))
        builder.row(CallbackButton(text="📋 Деканат", payload="@student-deanery"))
        builder.row(CallbackButton(text="🏠 Общежитие", payload="@student-dormitory"))
        builder.row(CallbackButton(text="🎪 Мероприятия", payload="@student-events"))
        builder.row(CallbackButton(text="📚 Библиотека", payload="@student-library"))

    elif role == "professor":
        builder.row(CallbackButton(text="✈️ Командировки", payload="@professor-business-trips"))
        builder.row(CallbackButton(text="🏖️ Отпуска", payload="@professor-vacations"))
        builder.row(CallbackButton(text="🏢 Офис", payload="@professor-office"))
        builder.row(CallbackButton(text="🎪 Мероприятия", payload="@professor-events"))

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
    request = requests.get(f"http://localhost:8000/digital_university/api/v1/presense/{max_id}")
    statement = bool(request.json())
    print(statement)

    if not statement:

        requests.post(f"http://localhost:8000/digital_university/api/v1/assign/{max_id}")

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
    max_id = event.from_user.user_id

    if payload == "@auto-set-role-applicant":
        requests.post(f"http://localhost:8000/digital_university/api/v1/assign/{max_id}/applicant")
    elif payload == "@auto-set-role-student":
        requests.post(f"/digital_university/api/v1/assign/{max_id}/student")
    elif payload == "@auto-set-role-professor":
        requests.post(f"/digital_university/api/v1/assign/{max_id}/professor")




@dp.message_callback()
async def main_menu_handler(event: MessageCallback):
    payload = event.callback.payload
    user_id = event.from_user.user_id

    await event.answer()

    if payload == "@applicant-admission":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Подать заявление", payload="@applicant-application"))
        builder.row(CallbackButton(text="📊 Проверить статус", payload="@applicant-check-status"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🎓 **Поступление**\n\n"
                 "Здесь вы можете подать заявление на поступление, проверить статус заявления.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@applicant-open-days":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Записаться", payload="@applicant-sign-up-on-open-day"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📅 **Дни открытых дверей**\n\n"
                 "Запишитесь на день открытых дверей!",
            attachments=[builder.as_markup()]
        )

    elif payload == "@applicant-university-info":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏫 О вузе", payload="@applicant-about-university"))
        builder.row(CallbackButton(text="📊 Программы", payload="@applicant-studying-programmes"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏫 **Информация о вузе**\n\n"
                 "Узнайте больше о нашем вузе и образовательных программах.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-schedule":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Текущее расписание", payload="@student-current-schedule"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📚 **Расписание**\n\n"
                 "Просматривайте актуальное расписание.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-projects":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💡 Предложить проект", payload="@student-new-project"))
        builder.row(CallbackButton(text="👥 Найти команду", payload="@student-find-team"))
        builder.row(CallbackButton(text="📋 Доступные проекты", payload="@student-available-projects"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🎯 **Проектная деятельность**\n\n"
                 "Предлагайте свои проекты, находите команду или присоединяйтесь к существующим проектам",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-career":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💼 Вакансии", payload="@student-vacancies"))
        builder.row(CallbackButton(text="📝 Резюме", payload="@student-resume"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="💼 **Карьера**\n\n"
                 "Центр карьеры поможет вам найти работу или составить резюме",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-deanery":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📄 Заказать справку", payload="@student-order-inquiry"))
        builder.row(CallbackButton(text="💳 Оплата обучения", payload="@student-studying-payment"))
        builder.row(CallbackButton(text="📝 Академический отпуск", payload="@student-academic-vacation"))
        builder.row(CallbackButton(text="🚗 Перевод", payload="@student-translation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📋 **Деканат**\n\n"
                 "Оформляйте справки, оплачивайте обучение и подавайте заявления "
                 "на академический отпуск или перевод.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-dormitory":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💳 Оплата проживания", payload="@student-living-payment"))
        builder.row(CallbackButton(text="🛠️ Техподдержка", payload="@student-dormitory-support"))
        builder.row(CallbackButton(text="👥 Гостевой пропуск", payload="@student-guest-pass"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏠 **Общежитие**\n\n"
                 "Управляйте всеми вопросами, связанными с проживанием в общежитии.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-events":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Календарь событий", payload="@student-events"))
        builder.row(CallbackButton(text="🎫 Зарегистрироваться", payload="@student-sign-up-on-events"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🎪 **Мероприятия**\n\n"
                 "Просматривайте календарь мероприятий и регистрируйтесь "
                 "как участник или зритель.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@student-library":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📚 Просмотр заказанных книг", payload="@student-books"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="📚 **Библиотека**\n\n"
                 "Заказывайте книги и получайте доступ к электронной библиотеке.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@staff-business-trips":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Оформить командировку", payload="@staff-business-trip"))
        builder.row(CallbackButton(text="📊 Отчеты", payload="@staff-reports"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="✈️ **Командировки**\n\n"
                 "Оформляйте и согласовывайте заявки на командировки, "
                 "а также подавайте отчеты по возвращении.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@staff-vacations":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏖️ Оформить отпуск", payload="@staff-vacation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏖️ **Отпуска**\n\n"
                 "Оформляйте и согласовывайте заявки на отпуск.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@staff-office":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📄 Справки", payload="@staff-order-inquiry"))
        builder.row(CallbackButton(text="👥 Гостевой пропуск", payload="@staff-guest-pass"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="@all-main-menu"))

        await event.message.edit(
            text="🏢 **Офис**\n\n"
                 "Заказывайте справки с места работы и оформляйте гостевые пропуска в офис.",
            attachments=[builder.as_markup()]
        )

    elif payload == "@all-main-menu":
        menu = await get_main_menu(current_role)
        role_text = {
            UserRole.APPLICANT: "абитуриент",
            UserRole.STUDENT: "студент",
            UserRole.STAFF: "сотрудник"
        }

        await event.message.edit(
            text=f"👋 Добро пожаловать, {role_text[current_role]} {event.from_user.first_name}!\n\nВыберите нужный раздел:",
            attachments=[menu.as_markup()]
        )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())