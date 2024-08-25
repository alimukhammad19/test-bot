import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from districts import districts
from schools import schools
from configs import BOT_TOKEN
import aiohttp


DB_URL = ""

async def get_dollar_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['rates']['UZS']  # O'zbekiston so'miga nisbatan kurs
            else:
                return None

async def start(update: Update, context: CallbackContext):
    # Foydalanuvchini kutib olish
    keyboard = [
        [InlineKeyboardButton(district_name, callback_data=str(district_id))]
        for district_id, district_name in districts.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Xush kelibsiz!✅\nUshbu bot orqali Surxondaryo viloyati joylashgan maktablari haqida qisqacha ma'lumot olishingiz mumkin.✅\nTumanni tanlang!",
        reply_markup=reply_markup
    )

async def dollar(update: Update, context: CallbackContext):
    # Dollar kursini olish va foydalanuvchiga ko'rsatish
    dollar_rate = await get_dollar_rate()
    if dollar_rate:
        await update.message.reply_text(f"💵Hozirda mamlakatimizda dollar kursi: 1 USD = {dollar_rate} UZS ga teng")
    else:
        await update.message.reply_text("Dollar kursini olishda xatolik yuz berdi.")

async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "❌Muammo yuzaga kelgan bo'lsa murojaat qiling,\n\nMurojaat uchun:📞 +99890-411-01-35"
    )

async def handle_text(update: Update, context: CallbackContext):
    user_input = update.message.text.strip().lower()
    
    district_id = None
    for id, name in districts.items():
        if user_input == name.lower():
            district_id = id
            break
    
    if district_id is not None:
        school_list = schools.get(district_id, [])
        if not school_list:
            await update.message.reply_text("❌Bu tumanda maktablar topilmadi.")
            return

        keyboard = [
            [InlineKeyboardButton(school['name'], callback_data=f'{district_id}_{school_index}')] for school_index, school in enumerate(school_list, 1)
        ]
        keyboard.append([InlineKeyboardButton("Orqaga", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text=f"{districts[district_id]} tumanidagi maktablar ro'yxati:\n\nMaktabni tanlang:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "❌Xatolik!!! \n Tugmalardan foydalaning.✅"
        )

async def district_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    district_index = int(query.data)

    school_list = schools.get(district_index, [])
    if not school_list:
        await query.edit_message_text(text="Bu tumanda maktablar topilmadi.")
        return

    district_name = districts.get(district_index, "Nomalum tuman")

    keyboard = [
        [InlineKeyboardButton(school['name'], callback_data=f'{district_index}_{school_index}')] for school_index, school in enumerate(school_list, 1)
    ]
    keyboard.append([InlineKeyboardButton("Orqaga", callback_data='back')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"{district_name} tumanidagi maktablar ro'yxati:🏛\n\nMaktabni tanlang:",
        reply_markup=reply_markup
    )

async def school_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("back"):
        if data == 'back':
            keyboard = [
                [InlineKeyboardButton(district_name, callback_data=str(district_id))]
                for district_id, district_name in districts.items()
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Xush kelibsiz!✅\nUshbu bot orqali Surxondaryo viloyati joylashgan maktablari haqida qisqacha ma'lumot olishingiz mumkin.✅\nTumanni tanlang",
                reply_markup=reply_markup
            )
        else:
            district_id = int(data.split('_')[1])
            school_list = schools.get(district_id, [])
            if not school_list:
                await query.edit_message_text(text="Bu tumanda maktablar topilmadi.")
                return

            district_name = districts.get(district_id, "Nomalum tuman")

            keyboard = [
                [InlineKeyboardButton(school['name'], callback_data=f'{district_id}_{school_index}')] for school_index, school in enumerate(school_list, 1)
            ]
            keyboard.append([InlineKeyboardButton("Orqaga", callback_data=f'back_{district_id}')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f"{district_name} tumanidagi maktablar ro'yxati:🏛\n\nMaktabni tanlang:",
                reply_markup=reply_markup
            )
        return
    
    district_index, school_index = map(int, query.data.split('_'))

    if district_index in schools and 0 < school_index <= len(schools[district_index]):
        school_info = schools[district_index][school_index - 1]
        school_details = (
            f"🏛{school_info['name']} haqida ma'lumot:\n\n"
            f"🤵🏻‍♂️Direktor: {school_info['director']}\n\n"
            f"📞Telefon: {school_info['phone']}\n\n"
            f"👩🏻‍💼O'qituvchilar soni: {school_info['teachers']}\n\n"
            f"👱🏻‍♂️👩O'quvchilar soni: {school_info['students']}"
        )
        await query.edit_message_text(
            text=school_details,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Boshqa maktablar", callback_data=str(district_index))]
                ]
            )
        )
    else:
        await query.edit_message_text(text="Maktab haqida ma'lumot topilmadi.")

def main():
    print("Start")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dollar", dollar))  # Dollar kursi uchun komanda qo'shildi
    application.add_handler(CommandHandler("help", help))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.add_handler(CallbackQueryHandler(district_handler, pattern='^[0-9]+$'))
    application.add_handler(CallbackQueryHandler(school_handler, pattern=r'^[0-9]+_[0-9]+$|^back(_[0-9]+)?$'))

    print("Bot ishlamoqda...")
    application.run_polling()

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(main())
    loop.run_forever()
