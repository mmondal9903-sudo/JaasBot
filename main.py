import logging
# Added ReplyKeyboardMarkup and KeyboardButton for persistent chat buttons
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, MenuButtonCommands
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your actual token
TOKEN = "7603627166:AAG_cFC5z9Qd1RxsKn8ew57QYVQW09lTCZ4" 

# Set up basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# The keep_alive function is assumed to be defined in a separate 'keep_alive.py' file
from keep_alive import keep_alive 

# ----------------- 1. HANDLER FUNCTIONS -----------------

# --- START COMMAND (Includes the new Reply Keyboard) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and displays the main Reply Keyboard."""
    
    # 1. Define the buttons for the Reply Keyboard (appears above the input field)
    keyboard = [
        # Row 1: These buttons will trigger the respective functionality
        [KeyboardButton("❓ Help & Info"), KeyboardButton("💬 Contact & Links")]
    ]
    
    # 2. Create the ReplyKeyboardMarkup object
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,      # Makes the keyboard a better size
        one_time_keyboard=False    # Keeps the keyboard visible always
    )
    
    await update.message.reply_text(
        f"Hey! Welcome to my Anime Bot 🎉\n\nChoose an option below or use a command:",
        reply_markup=reply_markup
    )

# --- REPLY BUTTON HANDLER ---

async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles messages sent by tapping the persistent Reply Keyboard buttons."""
    user_text = update.message.text
    
    if user_text == "❓ Help & Info":
        # Combines the logic from /about and /help
        await about(update, context) 
        await help_command(update, context)
        
    elif user_text == "💬 Contact & Links":
        # Triggers the inline buttons functionality
        await buttons(update, context)

# --- EXISTING COMMANDS (Kept for /help, /about, etc.) ---

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /about command and is triggered by a Reply Button."""
    await update.message.reply_text(
        "👋 Hello! Hope you're doing great.\n\n"
        "This bot was created to support our anime channel and make everything more convenient for you. "
        "Stay tuned for updates and enjoy your time with us!"
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /contact command."""
    await update.message.reply_text(
        "💬 Need to reach out?\n\n"
        "You can contact us through our official chat group.\n\n"
        "Just type /buttons and tap the 'Join Chat' button to get the link. See you there!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles simple greetings or replies when no button/command is matched."""
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
    """Handles the /help command and is triggered by a Reply Button."""
    await update.message.reply_text(
        "**Available Commands:**\n"
        "/start – Greet the user and show the menu buttons\n"
        "/help – Show this help message\n"
        "/about – Learn about this bot\n"
        "/buttons – Show useful inline links (Channel/Chat)\n"
        "\n**Other Interactions:**\n"
        "Use the buttons at the bottom for quick actions.\n"
        "Type 'hi' or 'bye' for a simple response.",
        parse_mode="Markdown"
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /buttons command and shows inline buttons (attached to the message)."""
    keyboard = [
        [InlineKeyboardButton("📢 Visit My Channel", url="https://t.me/Animevhispers")],
        [InlineKeyboardButton("💬 Join Chat Group", url="https://t.me/+ZMir6d1LpfowZmI1")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👇 Select a link option:", reply_markup=reply_markup)

# --- COMMAND SETUP ---

async def set_commands(application):
    """Sets the list of commands shown in the Telegram menu."""
    commands = [
        ("start", "Start the bot and show menu"),
        ("about", "Learn about this bot"),
        ("contact", "How to contact us"), # This is now less necessary with the buttons
        ("help", "List available commands"),
        ("buttons", "Show useful links")
    ]
    await application.bot.set_my_commands(
        [BotCommand(cmd, desc) for cmd, desc in commands]
    )
    await application.bot.set_chat_menu_button(
        menu_button=MenuButtonCommands()
    )


# ----------------- 2. BOT INITIALIZATION AND RUNNING -----------------

# Build the application
app = ApplicationBuilder().token(TOKEN).with_job_queue().build()

# Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("contact", contact))
app.add_handler(CommandHandler("buttons", buttons))

# Add the new MessageHandler for the Reply Keyboard buttons
# The regex looks for the exact text on the buttons we defined in 'start'
button_filter = filters.Regex("^(❓ Help & Info|💬 Contact & Links)$")
app.add_handler(MessageHandler(button_filter, handle_reply_button))

# General Text Handler (must come after all other text handlers)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# Run set_commands once when the bot starts
app.job_queue.run_once(lambda ctx: set_commands(app), when=0)

# Start the keep_alive server (for 24/7 hosting on platforms like Replit)
keep_alive() 

# Start the bot polling for updates
logger.info("Bot started and polling for updates...")
app.run_polling()
