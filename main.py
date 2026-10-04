import logging
import os
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

orders_logger = logging.getLogger("orders")
orders_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("orders.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
orders_logger.addHandler(file_handler)

TOKEN = "8707859450:AAFpnZIR2jByQbiy-isTTOk04eBbwlL5pis"
MY_TELEGRAM_ID = 5963495496

# --- إعداد خادم Flask الـويب لتلبية متطلبات Render ---
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is running 24/7!"
# -------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    text = (
        f"أهلاً بك يا غالي {user.first_name} في متجر قسائم الإنترنت في النجف 🌐\n\n"
        "🔹 مخصصون لبيع كارتات *المشروع الوطني* و*شركة صباح* بأفضل الأسعار.\n"
        "اختر القسم المطلوب من الأزرار أدناه:"
    )
    keyboard = [
        [InlineKeyboardButton("🌐 قسائم المشروع الوطني", callback_data="nat_menu")],
        [InlineKeyboardButton("🌐 قسائم شركة صباح", callback_data="sabah_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "main_menu":
        context.user_data.clear()
        text = (
            f"أهلاً بك يا غالي {user.first_name} في متجر قسائم الإنترنت في النجف 🌐\n\n"
            "اختر القسم المطلوب من الأزرار أدناه:"
        )
        keyboard = [
            [InlineKeyboardButton("🌐 قسائم المشروع الوطني", callback_data="nat_menu")],
            [InlineKeyboardButton("🌐 قسائم شركة صباح", callback_data="sabah_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "nat_menu":
        text = "اختر فئة كارتات *المشروع الوطني* المطلوبة:"
        keyboard = [
            [InlineKeyboardButton("🔹 35 ألف (60 ميجا)", callback_data="nat_35")],
            [InlineKeyboardButton("🔹 45 ألف (125 ميجا)", callback_data="nat_45")],
            [InlineKeyboardButton("🔹 65 ألف (250 ميجا)", callback_data="nat_65")],
            [InlineKeyboardButton("🔹 100 ألف (500 ميجا)", callback_data="nat_100")],
            [InlineKeyboardButton("⬅ القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "sabah_menu":
        text = "اختر باقة *شركة صباح* المطلوبة:"
        keyboard = [
            [InlineKeyboardButton("🔹 برونز (35 ألف - 50 ميجا)", callback_data="sabah_35")],
            [InlineKeyboardButton("🔹 سيلفر (45 ألف - 100 ميجا)", callback_data="sabah_45")],
            [InlineKeyboardButton("🔹 جولد (65 ألف - 180 ميجا)", callback_data="sabah_65")],
            [InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data in ["nat_35", "nat_45", "nat_65", "nat_100", "sabah_35", "sabah_45", "sabah_65"]:
        is_nat = data.startswith("nat_")
        price_val = int(data.split("_")[1])
        if is_nat:
            package_name = f"المشروع الوطني - {price_val} ألف"
        else:
            pkg_title = "برونز (35 ألف)" if price_val == 35 else ("سيلفر (45 ألف)" if price_val == 45 else "جولد (65 ألف)")
            package_name = f"شركة صباح - {pkg_title}"
        context.user_data["package_name"] = package_name
        context.user_data["price_per_card"] = price_val
        context.user_data["step"] = "waiting_quantity"
        text = (
            f"لقد اخترت: *{package_name}*\n\n"
            "✍️ *يرجى كتابة عدد القسائم التي تريد شراءها الآن برقم صحيح (مثال: 7):*"
        )
        keyboard = [[InlineKeyboardButton("⬅️ القائمة الرئيسية", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "confirm_order":
        package_name = context.user_data.get("package_name", "غير محدد")
        quantity = context.user_data.get("quantity", 1)
        total_price = context.user_data.get("total_price", 0)
        text = f"📦 طلبك: *{package_name}*\n🔢 العدد: *{quantity}*\n💰 المجموع: *{total_price} ألف دينار*\n\nيرجى تحديد *طريقة الدفع* المفضلة لديك:"
        keyboard = [
            [InlineKeyboardButton("💵 دفع كاش (عند الاستلام)", callback_data="pay_cash")],
            [InlineKeyboardButton("💳 ماستر كارد / زين كاش", callback_data="pay_master")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data in ["pay_cash", "pay_master"]:
        is_cash = (data == "pay_cash")
        package_name = context.user_data.get("package_name", "غير محدد")
        quantity = context.user_data.get("quantity", 1)
        total_price = context.user_data.get("total_price", 0)
        context.user_data["payment_method"] = "كاش عند الاستلام" if is_cash else "ماستر كارد / زين كاش"

        if is_cash:
            context.user_data["step"] = "waiting_address"
            text = (
                "✅ *تم اختيار الدفع كاش عند الاستلام*\n\n"
                f"🔹 الطلب: *{package_name}*\n"
                f"🔢 العدد: *{quantity}*\n"
                f"💰 المجموع: *{total_price} ألف دينار*\n\n"
                "📍 الآن أرسل *موقعك الجغرافي (Location)* أو اكتب عنوانك بالتفصيل هنا."
            )
            keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            context.user_data["step"] = "waiting_receipt"
            text = (
                "💳 *طريقة الدفع: ماستر كارد / زين كاش*\n\n"
                "يرجى التحويل على الرقم الموحد:\n`07852720800`\n\n"
                f"📦 الطلب: *{package_name}*\n"
                f"🔢 العدد: *{quantity}*\n"
                f"💰 المجموع: *{total_price} ألف دينار*\n\n"
                "📸 *أرسل صورة وصل التحويل هنا في الدردشة ليتم تأكيد طلبك!*"
            )
            keyboard = [[InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data.startswith("admin_yes_") or data.startswith("admin_no_"):
        parts = data.split("_")
        action = parts[1]
        target_user_id = int(parts[2])
        if action == "yes":
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="🎉 *تمت الموافقة على طلبك وتجهيز القسائم!*\n\nشكراً لتعاملكم معنا ❤️",
                    parse_mode="Markdown"
                )
                await query.edit_message_text(query.message.text + "\n\n🟢 *تمت الموافقة وإرسال القسائم للزبون بنجاح.*", parse_mode="Markdown")
            except Exception as e:
                await query.edit_message_text(query.message.text + f"\n\n⚠️ تمت الموافقة ولكن فشل إرسال إشعار للزبون: {e}")
        else:
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="❌ نعتذر منك، تم رفض الطلب أو إلغاؤه من قبل الإدارة.",
                    parse_mode="Markdown"
                )
                await query.edit_message_text(query.message.text + "\n\n🔴 *تم رفض الطلب بنجاح.*", parse_mode="Markdown")
            except Exception as e:
                await query.edit_message_text(query.message.text + f"\n\n⚠️ تم الرفض ولكن فشل إرسال إشعار للزبون: {e}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name
    username = f"@{user.username}" if user.username else "بدون معرف"
    user_id = user.id
    step = context.user_data.get("step")

    if step == "waiting_quantity":
        text_input = update.message.text.strip() if update.message.text else ""
        if not text_input.isdigit():
            await update.message.reply_text("⚠️ يرجى كتابة رقم صحيح فقط للكمية (مثلاً: 7):")
            return
        quantity = int(text_input)
        if quantity <= 0:
            await update.message.reply_text("⚠️ يرجى إدخال عدد أكبر من الصفر:")
            return
        price_per_card = context.user_data.get("price_per_card", 0)
        total_price = quantity * price_per_card
        package_name = context.user_data.get("package_name", "غير محدد")
        context.user_data["quantity"] = quantity
        context.user_data["total_price"] = total_price
        context.user_data["step"] = "confirm_step"
        summary_text = (
            "📋 *ملخص الطلب:*\n\n"
            f"🔹 الباقة: *{package_name}*\n"
            f"🔹 سعر القسيمة: *{price_per_card} ألف*\n"
            f"🔢 العدد المطلوب: *{quantity} قسائم*\n"
            f"💰 *المجموع الكلي: {total_price} ألف دينار*\n\n"
            "اضغط على زر التأكيد أدناه لإرسال الطلب:"
        )
        keyboard = [
            [InlineKeyboardButton("✅ تأكيد شراء القسائم", callback_data="confirm_order")],
            [InlineKeyboardButton("❌ إلغاء وتراجع", callback_data="main_menu")]
        ]
        await update.message.reply_text(summary_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    elif step == "waiting_receipt" and update.message.photo:
        package_name = context.user_data.get("package_name", "غير محدد")
        quantity = context.user_data.get("quantity", 1)
        total_price = context.user_data.get("total_price", 0)
        photo_file_id = update.message.photo[-1].file_id
        await update.message.reply_text(
            "✅ *تم استلام صورة الوصل بنجاح!*\n\n⏳ جاري مراجعة طلبك وتجهيز القسائم من قبل الإدارة الآن.",
            parse_mode="Markdown"
        )
        admin_caption = (
            "🚨 *طلب تحويل إلكتروني جديد بانتظار الإرسال!*\n\n"
            f"👤 الاسم: {name}\n"
            f"🆔 المعرف: {username}\n"
            f"📦 الباقة: {package_name}\n"
            f"🔢 العدد المطلوب: {quantity}\n"
            f"💰 السعر الكلي: {total_price} ألف دينار\n\n"
            "هل تريد إرسال القسائم لهذا الزبون الآن؟"
        )
        admin_keyboard = [[
            InlineKeyboardButton("✅ نعم، إرسال القسائم", callback_data=f"admin_yes_{user_id}"),
            InlineKeyboardButton("❌ لا، رفض", callback_data=f"admin_no_{user_id}")
        ]]
        await context.bot.send_photo(
            chat_id=MY_TELEGRAM_ID,
            photo=photo_file_id,
            caption=admin_caption,
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        orders_logger.info(
            f"نوع الدفع: إلكتروني | المستخدم: {name} ({user_id}, {username}) | الباقة: {package_name} | العدد: {quantity} | المجموع: {total_price} ألف | صورة الوصل: {photo_file_id}"
        )
        context.user_data.clear()
        return

    elif step == "waiting_address":
        package_name = context.user_data.get("package_name", "غير محدد")
        quantity = context.user_data.get("quantity", 1)
        total_price = context.user_data.get("total_price", 0)
        address_details = ""
        if update.message.location:
            lat = update.message.location.latitude
            lon = update.message.location.longitude
            address_details = f"موقع جغرافي: {lat}, {lon}"
            await context.bot.send_location(chat_id=MY_TELEGRAM_ID, latitude=lat, longitude=lon)
        elif update.message.text:
            address_details = update.message.text
        else:
            await update.message.reply_text("⚠️ يرجى إرسال موقعك الجغرافي أو كتابة عنوانك بالتفصيل بالنص:")
            return
        await update.message.reply_text(
            "✅ *تم تسجيل طلبك وعنوانك بنجاح!*\n\n⏳ جاري معالجة الطلب من قبل الإدارة لإرسال المندوب.",
            parse_mode="Markdown"
        )
        admin_msg = (
            "🚨 *طلب كاش جديد بانتظار الموافقة!*\n\n"
            f"👤 الاسم: {name}\n"
            f"🆔 المعرف: {username}\n"
            f"📦 الباقة: {package_name}\n"
            f"🔢 العدد المطلوب: {quantity}\n"
            f"💰 السعر الكلي: {total_price} ألف دينار\n"
            f"📍 العنوان/الموقع: {address_details}\n\n"
            "هل تريد إرسال القسائم لهذا الزبون الآن؟"
        )
        admin_keyboard = [[
            InlineKeyboardButton("✅ نعم، إرسال القسائم", callback_data=f"admin_yes_{user_id}"),
            InlineKeyboardButton("❌ لا، رفض", callback_data=f"admin_no_{user_id}")
        ]]
        await context.bot.send_message(
            chat_id=MY_TELEGRAM_ID,
            text=admin_msg,
            reply_markup=InlineKeyboardMarkup(admin_keyboard),
            parse_mode="Markdown"
        )
        orders_logger.info(
            f"نوع الدفع: كاش عند الاستلام | المستخدم: {name} ({user_id}, {username}) | الباقة: {package_name} | العدد: {quantity} | المجموع: {total_price} ألف | العنوان: {address_details}"
        )
        context.user_data.clear()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("❌ حدث خطأ في البوت:", exc_info=context.error)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO | filters.LOCATION | filters.TEXT & ~filters.COMMAND, message_handler))
    
    port = int(os.environ.get("PORT", 10000))
    print(f"🤖 البوت يعمل على المنفذ {port}...")
    
    # تشغيل البوت مباشرة بدون خيوط معقدة
    app.run_polling()

if __name__ == '__main__':
    main()
# update
