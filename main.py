import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# تنظیمات توکن از متغیر محیطی
TOKEN = os.environ.get('TOKEN')

if not TOKEN:
    raise ValueError("لطفاً توکن ربات را در متغیر محیطی TOKEN تنظیم کنید")

# تابع محاسبه Fitness Age
def calculate_fitness_age(step_test, grip_strength, chair_stand, sit_reach, tug, sex):
    fitness_age = (
        79.807 
        - (0.017 * step_test) 
        - (0.203 * grip_strength) 
        - (0.031 * chair_stand) 
        - (0.052 * sit_reach) 
        + (0.985 * tug) 
        - (3.468 * sex)
    )
    return round(fitness_age, 1)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! 👋",
        reply_markup=None
    )
    await update.message.reply_text(
        "🤖 ربات محاسبه سن تناسب اندام\n\n"
        "دستورات قابل استفاده:\n"
        "/start - نمایش این پیام\n"
        "/help - راهنمای کامل\n"
        "/fitnessage [پارامترها] - محاسبه سن تناسب اندام\n\n"
        "مثال:\n"
        "<code>/fitnessage 100 30.5 12 25.0 8.5 1</code>"
    )

# دستور /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 راهنمای استفاده:\n\n"
        "1. پارامترهای مورد نیاز:\n"
        "   - تعداد قدم در 2 دقیقه\n"
        "   - قدرت گیرش دست (kg)\n"
        "   - تعداد بلندشدن از صندلی در 30 ثانیه\n"
        "   - انعطاف‌پذیری (cm)\n"
        "   - زمان تست TUG (ثانیه)\n"
        "   - جنسیت (1=مرد، 2=زن)\n\n"
        "2. مثال کامل:\n"
        "<code>/fitnessage 100 30.5 12 25.0 8.5 1</code>"
    )
    await update.message.reply_text(help_text)

# دستور /fitnessage
async def fitness_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 6:
            await update.message.reply_text(
                "⚠️ پارامترهای نادرست!\n"
                "الگوی صحیح:\n"
                "<code>/fitnessage قدم قدرت_گیرش بلندشدن انعطاف TUG جنسیت</code>\n\n"
                "مثال:\n"
                "<code>/fitnessage 100 30.5 12 25.0 8.5 1</code>"
            )
            return

        args = [float(arg) if '.' in arg else int(arg) for arg in context.args[:5]]
        sex = int(context.args[5])
        
        if sex not in [1, 2]:
            await update.message.reply_text("⚠️ جنسیت باید 1 (مرد) یا 2 (زن) باشد")
            return

        age = calculate_fitness_age(*args, sex)
        
        if age < 60:
            status = "✅ عالی! بهتر از میانگین سنی"
        elif 60 <= age <= 75:
            status = "👍 خوب! در محدوده طبیعی"
        else:
            status = "💡 نیاز به بهبود! با پزشک مشورت کنید"

        result = (
            f"🎯 نتایج:\n\n"
            f"• سن تناسب اندام: <b>{age} سال</b>\n"
            f"• وضعیت: {status}\n\n"
            f"📊 پارامترهای ورودی:\n"
            f"- قدم‌زدن: {args[0]}\n"
            f"- قدرت گیرش: {args[1]} kg\n"
            f"- بلندشدن از صندلی: {args[2]} بار\n"
            f"- انعطاف‌پذیری: {args[3]} cm\n"
            f"- زمان TUG: {args[4]} ثانیه\n"
            f"- جنسیت: {'مرد' if sex == 1 else 'زن'}"
        )
        await update.message.reply_text(result)

    except (ValueError, IndexError):
        await update.message.reply_text(
            "⚠️ خطا در پردازش داده‌ها!\n"
            "لطفاً مطمئن شوید:\n"
            "- همه پارامترها عدد هستند\n"
            "- فرمت صحیح رعایت شده\n\n"
            "مثال صحیح:\n"
            "<code>/fitnessage 100 30.5 12 25.0 8.5 1</code>"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لاگ خطاها"""
    print(f"⚠️ خطا در پردازش پیام: {context.error}")

def main():
    # ساخت Application
    application = ApplicationBuilder().token(TOKEN).build()

    # ثبت هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fitnessage", fitness_age))
    
    # هندلر پیام‌های متنی
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))
    
    # هندلر خطاها
    application.add_error_handler(error_handler)

    # اجرای ربات
    print("🤖 ربات در حال اجرا...")
    application.run_polling()

if __name__ == "__main__":
    main()