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


load_dotenv()

LOG = structlog.get_logger()

bot = Bot(os.getenv('MAX_TOKEN'))
dp = Dispatcher()

class UserRole(Enum):
    STUDENT = "student"
    APPLICANT = "applicant"
    STAFF = "staff"


# Временное хранилище ролей пользователей (БД)
user_roles = {}

# Главное меню
async def get_main_menu(role: UserRole):
    builder = InlineKeyboardBuilder()

    if role == UserRole.APPLICANT:
        builder.row(CallbackButton(text="🎓 Поступление", payload="admission"))
        builder.row(CallbackButton(text="📅 Дни открытых дверей", payload="open_days"))
        builder.row(CallbackButton(text="🏫 Информация о вузе", payload="university_info"))

    elif role == UserRole.STUDENT:
        builder.row(CallbackButton(text="📚 Расписание", payload="schedule"))
        builder.row(CallbackButton(text="🎯 Проектная деятельность", payload="projects"))
        builder.row(CallbackButton(text="💼 Карьера", payload="career"))
        builder.row(CallbackButton(text="📋 Деканат", payload="deanery"))
        builder.row(CallbackButton(text="🏠 Общежитие", payload="dormitory"))
        builder.row(CallbackButton(text="🎪 Мероприятия", payload="events"))
        builder.row(CallbackButton(text="📚 Библиотека", payload="library"))

    elif role == UserRole.STAFF:
        builder.row(CallbackButton(text="✈️ Командировки", payload="business_trips"))
        builder.row(CallbackButton(text="🏖️ Отпуска", payload="vacations"))
        builder.row(CallbackButton(text="🏢 Офис", payload="office"))
        builder.row(CallbackButton(text="🎪 Мероприятия", payload="events"))

    builder.row(CallbackButton(text="🔄 Сменить роль", payload="change_role"))

    return builder

@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Отправьте команду /start'
    )
    async with engine.begin() as conn:
        result = await conn.execute(select(Students.name).where(Students.id == 2))
        result = result.scalar_one_or_none()
        if not result:
            await event.bot.send_message(
                chat_id=event.chat_id,
                text="студент не найден"
            )
        else:
            await event.bot.send_message(
                chat_id=event.chat_id,
                text = result
            )

# Стартовый хендлер
@dp.message_created(Command("/start"))
async def start_handler(event: MessageCreated):
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="👨‍🎓 Абитуриент", payload="role_applicant"))
    builder.row(CallbackButton(text="👨‍🎓 Студент", payload="role_student"))
    builder.row(CallbackButton(text="👨‍🏫 Сотрудник", payload="role_staff"))

    await event.message.answer(
        "👋 Добро пожаловать в Цифровой ВУЗ!\n\n"
        "Выберите вашу роль для доступа к соответствующим сервисам:",
        attachments=[builder.as_markup()]
    )


# Обработка выбора роли
@dp.message_callback(F.callback.payload.startswith("role_"))
async def role_selection_handler(event: MessageCallback):
    payload = event.callback.payload
    user_id = event.from_user.user_id

    if payload == "role_applicant":
        role = UserRole.APPLICANT
        welcome_text = f"🎓 Добро пожаловать, абитуриент {event.from_user.first_name}!"
        user_roles[user_id] = role
    elif payload == "role_student":
        role = UserRole.STUDENT
        welcome_text = f"👨‍🎓 Добро пожаловать, студент {event.from_user.first_name}!"
        user_roles[user_id] = role
    elif payload == "role_staff":
        role = UserRole.STAFF
        welcome_text = f"👨‍🏫 Добро пожаловать, сотрудник {event.from_user.first_name}!"
        user_roles[user_id] = role
    else:
        return

    menu = await get_main_menu(role)

    await event.message.edit(
        text=f"{welcome_text}\n\nВыберите нужный раздел:",
        attachments=[menu.as_markup()]
    )


# Обработка главного меню
@dp.message_callback()
async def main_menu_handler(event: MessageCallback):
    payload = event.callback.payload
    user_id = event.from_user.user_id

    current_role = user_roles.get(user_id, UserRole.STUDENT)

    await event.answer()

    # Абитуриенты
    if payload == "admission":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Подать заявление", payload="@app-apply-to-univ"))
        builder.row(CallbackButton(text="📊 Проверить статус", payload="@app-check-status"))
        builder.row(CallbackButton(text="❓ Частые вопросы", payload="@app-faq"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🎓 **Поступление**\n\n"
                 "Здесь вы можете подать заявление на поступление, проверить статус заявления "
                 "или ознакомиться с часто задаваемыми вопросами.",
            attachments=[builder.as_markup()]
        )

    elif payload == "open_days":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Записаться", payload="@app-sign-up-for-open-days"))
        builder.row(CallbackButton(text="👀 Виртуальный тур", payload="@app-virtual-tour"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="📅 **Дни открытых дверей**\n\n"
                 "Запишитесь на день открытых дверей или совершите виртуальный тур по нашему кампусу!",
            attachments=[builder.as_markup()]
        )

    elif payload == "university_info":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏫 О вузе", payload="@app-about-univ"))
        builder.row(CallbackButton(text="📊 Программы", payload="@app-programs"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🏫 **Информация о вузе**\n\n"
                 "Узнайте больше о нашем вузе и образовательных программах.",
            attachments=[builder.as_markup()]
        )

    # Студенты
    elif payload == "schedule":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Текущее расписание", payload="@stu-show-schedule"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="📚 **Расписание**\n\n"
                 "Просматривайте актуальное расписание.",
            attachments=[builder.as_markup()]
        )

    elif payload == "projects":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💡 Предложить проект", payload="@stu-new-project"))
        builder.row(CallbackButton(text="👥 Найти команду", payload="@stu-find-team"))
        builder.row(CallbackButton(text="📋 Доступные проекты", payload="@stu-available-projects"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🎯 **Проектная деятельность**\n\n"
                 "Предлагайте свои проекты, находите команду или присоединяйтесь к существующим проектам",
            attachments=[builder.as_markup()]
        )

    elif payload == "career":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💼 Вакансии", payload="@stu-vacancies"))
        builder.row(CallbackButton(text="📝 Резюме", payload="@stu-resume"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="💼 **Карьера**\n\n"
                 "Центр карьеры поможет вам найти работу или составить резюме",
            attachments=[builder.as_markup()]
        )

    elif payload == "deanery":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📄 Заказать справку", payload="@stu-order-inquiry"))
        builder.row(CallbackButton(text="💳 Оплата обучения", payload="@stu-study-payment"))
        builder.row(CallbackButton(text="📝 Академический отпуск", payload="@stu-academic-vacation"))
        builder.row(CallbackButton(text="🚗 Перевод", payload="@stu-translation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="📋 **Деканат**\n\n"
                 "Оформляйте справки, оплачивайте обучение и подавайте заявления "
                 "на академический отпуск или перевод.",
            attachments=[builder.as_markup()]
        )

    elif payload == "dormitory":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="💳 Оплата проживания", payload="@stu-dormitory-payment"))
        builder.row(CallbackButton(text="🛠️ Техподдержка", payload="@stu-dormitory-support"))
        builder.row(CallbackButton(text="👥 Гостевой пропуск", payload="@stu-guest-pass"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🏠 **Общежитие**\n\n"
                 "Управляйте всеми вопросами, связанными с проживанием в общежитии.",
            attachments=[builder.as_markup()]
        )

    elif payload == "events":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📅 Календарь событий", payload="@stu-events"))
        builder.row(CallbackButton(text="🎫 Зарегистрироваться", payload="@stu-reg-on-events"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🎪 **Мероприятия**\n\n"
                 "Просматривайте календарь мероприятий и регистрируйтесь "
                 "как участник или зритель.",
            attachments=[builder.as_markup()]
        )

    elif payload == "library":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📚 Заказать книги", payload="@stu-library-order"))
        builder.row(CallbackButton(text="💻 Электронная библиотека", payload="@stu-elibrary"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="📚 **Библиотека**\n\n"
                 "Заказывайте книги и получайте доступ к электронной библиотеке.",
            attachments=[builder.as_markup()]
        )

    # Сотрудники
    elif payload == "business_trips":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📝 Оформить командировку", payload="@staff-business-trip"))
        builder.row(CallbackButton(text="📊 Отчеты", payload="@staff-reports"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="✈️ **Командировки**\n\n"
                 "Оформляйте и согласовывайте заявки на командировки, "
                 "а также подавайте отчеты по возвращении.",
            attachments=[builder.as_markup()]
        )

    elif payload == "vacations":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="🏖️ Оформить отпуск", payload="@staff-vacation"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🏖️ **Отпуска**\n\n"
                 "Оформляйте и согласовывайте заявки на отпуск.",
            attachments=[builder.as_markup()]
        )

    elif payload == "office":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="📄 Справки", payload="@staff-order-inquiry"))
        builder.row(CallbackButton(text="👥 Гостевой пропуск", payload="@staff-guest-pass"))
        builder.row(CallbackButton(text="⬅️ Назад", payload="back_to_main"))

        await event.message.edit(
            text="🏢 **Офис**\n\n"
                 "Заказывайте справки с места работы и оформляйте гостевые пропуска в офис.",
            attachments=[builder.as_markup()]
        )

    # Навигация
    elif payload == "back_to_main":
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

    elif payload == "change_role":
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="👨‍🎓 Абитуриент", payload="role_applicant"))
        builder.row(CallbackButton(text="👨‍🎓 Студент", payload="role_student"))
        builder.row(CallbackButton(text="👨‍🏫 Сотрудник", payload="role_staff"))

        await event.message.edit(
            text="Выберите вашу роль:",
            attachments=[builder.as_markup()]
        )


# Обработка текстовых сообщений
@dp.message_created(F.message.body.text)
async def text_message_handler(event: MessageCreated):
    text = event.message.body.text.lower()

    if text in ['/start', 'старт', 'начать', 'меню']:
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="👨‍🎓 Абитуриент", payload="role_applicant"))
        builder.row(CallbackButton(text="👨‍🎓 Студент", payload="role_student"))
        builder.row(CallbackButton(text="👨‍🏫 Сотрудник", payload="role_staff"))

        await event.message.answer(
            "👋 Добро пожаловать в Цифровой ВУЗ!\n\n"
            "Выберите вашу роль для доступа к соответствующим сервисам:",
            attachments=[builder.as_markup()]
        )
    else:
        await event.message.answer(
            "Используйте кнопки меню для навигации. "
            "Если вы хотите вернуться в главное меню, отправьте /start"
        )


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())