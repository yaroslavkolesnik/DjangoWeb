from django.core.management.base import BaseCommand
from django.conf import settings
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# 👇 Импортируем твои модели
from myapp.models import Product, Category, Brand

# Инициализация бота
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

user_data = {}


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **kwargs):
        self.stdout.write("Бот запущен...")
        bot.infinity_polling()


# --- НАЧАЛО ДИАЛОГА ---

@bot.message_handler(commands=['start'])
def start_message(message):
    # Очищаем данные
    user_data[message.chat.id] = {}

    # 1. Достаем все категории из базы данных
    categories = Category.objects.all()

    if not categories.exists():
        bot.send_message(message.chat.id, "В магазине пока нет категорий. Зайдите позже!")
        return

    # 2. Создаем клавиатуру с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Добавляем кнопки для каждой категории
    buttons = []
    for cat in categories:
        # cat.name - это название категории из базы (Телефон, Ноутбук и т.д.)
        buttons.append(types.KeyboardButton(cat.name))

    markup.add(*buttons)  # Добавляем все кнопки разом

    msg = bot.send_message(
        message.chat.id,
        "Привет! 👋 Я помогу выбрать технику.\nВыберите категорию из меню внизу:",
        reply_markup=markup
    )

    bot.register_next_step_handler(msg, step_category)


# --- ШАГ 1: ВЫБОР КАТЕГОРИИ ---

def step_category(message):
    chat_id = message.chat.id
    category_name = message.text

    # Проверяем, есть ли такая категория в базе
    # (Вдруг юзер не нажал кнопку, а написал "Космолет" вручную)
    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        msg = bot.send_message(chat_id, "Такой категории нет. Пожалуйста, выберите из кнопок внизу.")
        bot.register_next_step_handler(msg, step_category)
        return

    # Запоминаем ID категории и Имя
    user_data[chat_id]['category_id'] = category.id
    user_data[chat_id]['category_name'] = category.name

    # 3. Теперь давайте предложим БРЕНДЫ, которые есть В ЭТОЙ категории
    # Ищем товары этой категории и берем их бренды
    brands = Brand.objects.filter(product__category=category).distinct()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    buttons = []
    for brand in brands:
        buttons.append(types.KeyboardButton(brand.name))

    # Добавляем кнопку "Любой", если бренд не важен
    markup.add(types.KeyboardButton("Любой"))
    markup.add(*buttons)

    msg = bot.send_message(
        chat_id,
        f"Выбрано: {category.name}. \nКакой бренд вас интересует?",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, step_brand)


# --- ШАГ 2: ВЫБОР БРЕНДА ---

def step_brand(message):
    chat_id = message.chat.id
    brand_name = message.text

    user_data[chat_id]['brand'] = brand_name

    # Убираем кнопки (ReplyKeyboardRemove), чтобы юзер вводил цену руками
    markup = types.ReplyKeyboardRemove()

    msg = bot.send_message(
        chat_id,
        "Понял. А какой у вас бюджет? (Напишите максимальную сумму, например: 30000)",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, step_price)


# --- ШАГ 3: ЦЕНА ---

def step_price(message):
    chat_id = message.chat.id
    try:
        price = int(message.text.replace(' ', ''))
        user_data[chat_id]['price'] = price
        show_results(message)
    except ValueError:
        msg = bot.send_message(chat_id, "Пожалуйста, введите сумму цифрами (например: 25000).")
        bot.register_next_step_handler(msg, step_price)


# --- ФИНАЛ: ВЫВОД ---

def show_results(message, page=1):
    # Определяем chat_id (откуда пришел вызов: кнопка или текст)
    chat_id = message.chat.id if isinstance(message, types.Message) else message.message.chat.id

    data = user_data.get(chat_id)

    if not data:
        bot.send_message(chat_id, "Данные устарели. Начните /start")
        return

    # 1. Формируем запрос
    products = Product.objects.filter(published=True, category_id=data['category_id'], price__lte=data['price'])
    if data['brand'].lower() != 'любой':
        products = products.filter(brand__name__icontains=data['brand'])

    # Сортировка: Сначала в наличии
    products = products.order_by('-quantity', 'price')

    # 2. ПАГИНАЦИЯ
    ITEMS_PER_PAGE = 5
    count = products.count()

    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    products_page = products[start_index:end_index]

    if products_page.exists():
        if page == 1:
            bot.send_message(chat_id, f"Нашел {count} вариантов:")

        for product in products_page:
            keyboard = InlineKeyboardMarkup()

            # Кнопка "Инфо" (нужна всегда)
            btn_specs = InlineKeyboardButton(text="📜 Инфо", callback_data=f"specs_{product.id}")

            # 👇 ГЛАВНОЕ ИСПРАВЛЕНИЕ ЗДЕСЬ
            if product.quantity > 0:
                # ТОВАР ЕСТЬ
                status_text = "✅ В наличии"
                caption = f"📦 <b>{product.name}</b>\n{status_text}\n💰 {product.price} грн"

                # Добавляем кнопку "Купить" + "Инфо"
                btn_url = InlineKeyboardButton(text="🌐 Купить", url=f"http://127.0.0.1:8000/product/{product.slug}/")
                keyboard.add(btn_url, btn_specs)
            else:
                # ТОВАРА НЕТ
                status_text = "❌ Нет в наличии"
                # Добавляем телефон прямо в текст
                phone_text = "\n📞 <b>Заказ по телефону:</b>\n+38 (098) 120-86-49"
                caption = f"📦 <b>{product.name}</b>\n{status_text}\n💰 {product.price} грн{phone_text}"

                # Кнопку "Купить" НЕ добавляем, только "Инфо"
                keyboard.add(btn_specs)

            # Отправляем фото
            if product.image:
                try:
                    with open(product.image.path, 'rb') as photo:
                        bot.send_photo(chat_id, photo, caption=caption, parse_mode='HTML', reply_markup=keyboard)
                except:
                    bot.send_message(chat_id, caption, parse_mode='HTML', reply_markup=keyboard)
            else:
                bot.send_message(chat_id, caption, parse_mode='HTML', reply_markup=keyboard)

        # 3. КНОПКИ НАВИГАЦИИ (СТРАНИЦЫ)
        nav_keyboard = InlineKeyboardMarkup()
        nav_buttons = []

        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"page_{page - 1}"))

        nav_buttons.append(InlineKeyboardButton(text=f"{page} стр.", callback_data="noop"))

        if end_index < count:
            nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"page_{page + 1}"))

        nav_keyboard.row(*nav_buttons)

        bot.send_message(chat_id, "Перейти на другую страницу:", reply_markup=nav_keyboard)

    else:
        bot.send_message(chat_id, "На этой странице пусто.")


# 👇 ОБРАБОТЧИК НАЖАТИЯ НА КНОПКУ "ХАРАКТЕРИСТИКИ"
@bot.callback_query_handler(func=lambda call: call.data.startswith('specs_'))
def callback_specs(call):
    # Получаем ID товара из data (было "specs_5", стало "5")
    product_id = int(call.data.split('_')[1])

    try:
        product = Product.objects.get(id=product_id)

        # Парсим JSON характеристик
        specs_text = "📋 <b>Характеристики:</b>\n"
        if product.specifications:
            for key, value in product.specifications.items():
                specs_text += f"- {key}: {value}\n"
        else:
            specs_text += "Нет описания."

        # Отправляем всплывающее уведомление (alert) или сообщение
        bot.answer_callback_query(call.id, text="Загружаю...", show_alert=False)
        bot.send_message(call.message.chat.id, f"📱 {product.name}\n\n{specs_text}", parse_mode='HTML')

    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, text="Товар не найден", show_alert=True)


# 👇 ОБРАБОТЧИК ЛИСТАНИЯ СТРАНИЦ
@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_pagination(call):
    # Получаем номер страницы из callback_data="page_2"
    page = int(call.data.split('_')[1])

    # Удаляем старое сообщение с кнопками навигации, чтобы не мусорить
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    # Вызываем функцию показа результатов с новой страницей
    show_results(call.message, page=page)

    # Обязательно отвечаем телеграму, чтобы кнопка не "крутилась"
    bot.answer_callback_query(call.id)


# Заглушка для кнопки с номером страницы (чтобы она не давала ошибок при нажатии)
@bot.callback_query_handler(func=lambda call: call.data == 'noop')
def callback_noop(call):
    bot.answer_callback_query(call.id)


# 👇 ГЛОБАЛЬНЫЙ ПОИСК ПО НАЗВАНИЮ
# Этот обработчик ловит любой текст, который не попал в другие кнопки
@bot.message_handler(func=lambda message: True)
def global_search(message):
    chat_id = message.chat.id
    query = message.text.strip()

    # Игнорируем слишком короткие запросы (менее 2 букв)
    if len(query) < 2:
        bot.send_message(chat_id, "Введите хотя бы 2 буквы для поиска. 🔍")
        return

    bot.send_message(chat_id, f"🔍 Ищу товары по запросу: \"{query}\"...")

    # Ищем в названии товара (icontains = без учета регистра)
    products = Product.objects.filter(published=True, name__icontains=query)

    # Сортируем: сначала те, что в наличии
    products = products.order_by('-quantity', 'price')

    if products.exists():
        count = products.count()
        # Показываем только первые 5, чтобы не перегружать (пагинацию тут делать сложнее)
        products_to_show = products[:5]

        bot.send_message(chat_id, f"Найдено товаров: {count}. Вот первые результаты:")

        for product in products_to_show:
            keyboard = InlineKeyboardMarkup()
            btn_specs = InlineKeyboardButton(text="📜 Инфо", callback_data=f"specs_{product.id}")

            if product.quantity > 0:
                status_text = "✅ В наличии"
                caption = f"📦 <b>{product.name}</b>\n{status_text}\n💰 {product.price} грн"
                btn_url = InlineKeyboardButton(text="🌐 Купить", url=f"http://127.0.0.1:8000/product/{product.slug}/")
                keyboard.add(btn_url, btn_specs)
            else:
                status_text = "❌ Нет в наличии"
                phone_text = "\n📞 <b>Заказ по телефону:</b>\n+38 (099) 123-45-67"
                caption = f"📦 <b>{product.name}</b>\n{status_text}\n💰 {product.price} грн{phone_text}"
                keyboard.add(btn_specs)

            # Отправка фото
            if product.image:
                try:
                    with open(product.image.path, 'rb') as photo:
                        bot.send_photo(chat_id, photo, caption=caption, parse_mode='HTML', reply_markup=keyboard)
                except:
                    bot.send_message(chat_id, caption, parse_mode='HTML', reply_markup=keyboard)
            else:
                bot.send_message(chat_id, caption, parse_mode='HTML', reply_markup=keyboard)

        if count > 5:
            bot.send_message(chat_id, f"⚠️ Показано 5 из {count}. Уточните запрос, чтобы найти конкретный товар.")

    else:
        # Предлагаем вернуться в меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/start"))
        bot.send_message(chat_id, "Ничего не найдено 😔. Проверьте название или используйте каталог.",
                         reply_markup=markup)