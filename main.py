import os
import logging
from flask import Flask
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# ==========================================================
# ТАНЗИМОТИ АДМИН (РАҚАМҲОИ ТЕЛЕФОНИ ХУДРО ДАР ИН ҶО НАВИСЕД)
# ==========================================================
TOKEN = "8929448397:AAHqNt1jm2DTAT60PQsEid7ImZyW7QfGtb0"

SPITAMEN_PHONE = "+992-111-22-81-81"  # Рақами телефони Спитамен-и худро нависед
DUSHANBE_CITY_PHONE = "+992-111-22-81-81"  # Рақами телефони Душанбе Сити-и худро нависед
ADMIN_USERNAME = "@ISMAT2001IMS"  # Ссылкаи Телеграми худро нависед (бе аломати @)

# ==========================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Базаи маҳсулот ва нархҳо мувофиқи скриншотҳо
PRODUCTS = {
    "diamonds": {
        "110_dm": {"name": "💎 110 Алмос (100+10)", "price": 8.95},
        "341_dm": {"name": "💎 341 Алмос (310+31)", "price": 27.00},
        "572_dm": {"name": "💎 572 Алмос (520+52)", "price": 45.00},
        "1166_dm": {"name": "💎 1166 Алмос (1060+106)", "price": 85.00},
        "2398_dm": {"name": "💎 2398 Алмос (2180+218)", "price": 171.00},
        "6160_dm": {"name": "💎 6160 Алмос (5600+560)", "price": 430.00}
    },
    "vouchers": {
        "lite_v": {"name": "🎫 Недельный ваучер Lite", "price": 4.75},
        "week_v": {"name": "🎫 Ваучер на неделю", "price": 17.00},
        "month_v": {"name": "🎫 Ваучер на месяц", "price": 63.00}
    },
    "passes": {
        "lv6": {"name": "🚀 Пропуск прокачки (LV 6)", "price": 3.80},
        "lv10": {"name": "🚀 Пропуск прокачки (LV 10)", "price": 6.75},
        "lv15": {"name": "🚀 Пропуск прокачки (LV 15)", "price": 6.75},
        "lv20": {"name": "🚀 Пропуск прокачки (LV 20)", "price": 6.75},
        "lv25": {"name": "🚀 Пропуск прокачки (LV 25)", "price": 6.75},
        "lv30": {"name": "🚀 Пропуск прокачки (LV 30)", "price": 9.35}
    }
}

# Менюи Асосӣ (/start)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Каталоги маҳсулот", callback_data="show_categories")
    builder.button(text="ℹ️ Кӯмак / Алоқа", callback_data="help_info")
    builder.adjust(1)
    
    await message.answer(
        f"Ассалому алейкум, {message.from_user.full_name}!\n"
        f"Хуш омадед ба боти фурӯши алмосҳои Free Fire.\n\n"
        f"Дар ин ҷо шумо метавонед алмос ва ваучерҳоро бо нархи арзон ва қулай харед. 👇",
        reply_markup=builder.as_markup()
    )

# Интихоби Категорияҳо
@dp.callback_query(F.data == "show_categories")
async def show_categories(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Алмосҳо (Diamonds)", callback_data="cat_diamonds")
    builder.button(text="🎫 Ваучерҳо (Vouchers)", callback_data="cat_vouchers")
    builder.button(text="🚀 Пропуск прокачки", callback_data="cat_passes")
    builder.button(text="⬅️ Ба қафо", callback_data="back_to_main")
    builder.adjust(1)
    
    await callback.message.edit_text("Лутфан, категорияи маҳсулотро интихоб кунед:", reply_markup=builder.as_markup())

# Намоиши маҳсулоти дохили категория
@dp.callback_query(F.data.startswith("cat_"))
async def show_products_by_category(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    category_products = PRODUCTS.get(category, {})
    
    builder = InlineKeyboardBuilder()
    for item_id, info in category_products.items():
        builder.button(text=f"{info['name']} — {info['price']} смн.", callback_data=f"buy_{category}_{item_id}")
    
    builder.button(text="⬅️ Ба қафо", callback_data="show_categories")
    builder.adjust(1)
    
    await callback.message.edit_text("Маҳсулоти дилхоҳатонро интихоб кунед:", reply_markup=builder.as_markup())

# Интихоби тарзи пардохт
@dp.callback_query(F.data.startswith("buy_"))
async def choose_payment_method(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    category = parts[1]
    item_id = parts[2]
    
    item_info = PRODUCTS.get(category, {}).get(item_id)
    if not item_info:
        await callback.answer("Маҳсулот ёфт нашуд.")
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Spitamen Bank", callback_data=f"pay_spitamen_{category}_{item_id}")
    builder.button(text="📱 Dushanbe City", callback_data=f"pay_dcity_{category}_{item_id}")
    builder.button(text="⬅️ Ба қафо", callback_data=f"cat_{category}")
    builder.adjust(2, 1)
    
    await callback.message.edit_text(
        f"🎁 *Шумо интихоб кардед:* {item_info['name']}\n"
        f"💰 *Нарх:* {item_info['price']} сомонӣ\n\n"
        f"Лутфан, усули пардохтро интихоб кунед:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

# Дастурамали пардохт (бо рақами телефон)
@dp.callback_query(F.data.startswith("pay_"))
async def payment_instruction(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    bank = parts[1]
    category = parts[2]
    item_id = parts[3]
    
    item_info = PRODUCTS.get(category, {}).get(item_id)
    
    if bank == "spitamen":
        bank_name = "Spitamen Bank"
        phone_number = SPITAMEN_PHONE
    else:
        bank_name = "Dushanbe City"
        phone_number = DUSHANBE_CITY_PHONE
        
    instruction = (
        f"💳 *Пардохт тавассути {bank_name}:*\n\n"
        f"Маблағро ба ин рақами телефон (интиқоли пул ба корт) фиристед:\n"
        f"👉 `{phone_number}`\n\n"
        f"💵 Маблағи гузаронидашаванда: *{item_info['price']} сомонӣ*\n\n"
        f"⚠️ *Муҳим:* Пас аз пардохт, чек (скриншот)-и пардохт ва Free Fire ID-и худро ба администратор фиристед."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Ба қафо", callback_data=f"buy_{category}_{item_id}")
    
    await callback.message.edit_text(instruction, parse_mode="Markdown", reply_markup=builder.as_markup())

# Бозгашт ба аввал
@dp.callback_query(F.data == "back_to_main")
async def back_main(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Каталоги маҳсулот", callback_data="show_categories")
    builder.button(text="ℹ️ Кӯмак / Алоқа", callback_data="help_info")
    builder.adjust(1)
    await callback.message.edit_text("Лутфан тугмаи зерро пахш кунед:", reply_markup=builder.as_markup())

# Кӯмак ва Алоқа
@dp.callback_query(F.data == "help_info")
async def help_info(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Ба қафо", callback_data="back_to_main")
    await callback.message.edit_text(
        f"ℹ *Маълумоти бот:*\n\n"
        f"Пас аз гузаронидани маблағ, чек ва ID-и худро ба админ равон кунед. Алмосҳо дар давоми 5-15 дақиқа гузаронида мешаванд.\n\n"
        f"📞 Алоқа бо администратор: @{ADMIN_USERNAME}", 
        parse_mode="Markdown", 
        reply_markup=builder.as_markup()
    )

@app.route('/')
def home():
    return "Бот кор карда истодааст!"

async def start_bot():
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
  
