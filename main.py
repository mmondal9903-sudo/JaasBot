from keep_alive import keep_alive

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7603627166:AAG_cFC5z9Qd1RxsKn8ew57QYVQW09lTCZ4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Welcome to my Anime Bot 🎉")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Hope you're doing great.\n\n"
        "This bot was created to support our anime channel and make everything more convenient for you. "
        "Stay tuned for updates and enjoy your time with us!"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Need to reach out?\n\n"
        "You can contact us through our official chat group.\n\n"
        "Just type /buttons and tap the 'Join Chat' button to get the link. See you there!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    user_text = update.message.text.lower().strip()

    if "hi" in user_text or "hello" in user_text:
        await update.message.reply_text("👋 Hello there! How can I assist you today?")
    elif "bye" in user_text:
        await update.message.reply_text("👋 Goodbye! See you again soon.")
    else:
        await update.message.reply_text(
            "🙏 I'm still learning. Right now I only understand simple greetings like 'hi' or 'bye'."
        )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – Greet the user\n"
        "/help – Show this help message\n"
        "Type anything – I’ll repeat it!"
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 Visit My Channel", url="https://t.me/Animevhispers")],
        [InlineKeyboardButton("💬 Join Chat Group", url="https://t.me/+ZMir6d1LpfowZmI1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 Select an option:", reply_markup=reply_markup)



app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(CommandHandler("buttons", buttons))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("contact", contact))


keep_alive()
app.run_polling()
