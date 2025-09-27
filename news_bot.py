import os
import asyncio
from datetime import datetime
from twikit import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# --- CONFIGURATION ---
# The Twitter username we want to scrape for news
TWITTER_USER_TO_FOLLOW = "myanimelist"
# The ID of the Telegram chat where the news should be sent.
# NOTE: This variable is no longer strictly needed as /start saves the ID to bot_data.
NEWS_CHAT_ID = os.environ.get("NEWS_CHAT_ID", "0")

# --- SECRETS FROM RENDER ENVIRONMENT ---
# The bot token (from BotFather)
# CORRECT: Use the key name "BOT_TOKEN" to get the secret value from Render.
TOKEN = os.environ.get("BOT_TOKEN")
# Your Twitter/X credentials (these need to be added as environment variables in Render!)
# CORRECT: Use the key name "TW_USERNAME" to get the secret value from Render.
TW_USERNAME = os.environ.get("TW_USERNAME")
# CORRECT: Use the key name "TW_PASSWORD" to get the secret value from Render.
TW_PASSWORD = os.environ.get("TW_PASSWORD")
# --- END SECRETS ---


# --- 1. BOT HANDLERS (Commands users send) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and saves the chat ID for news."""
    # This is the ID of the chat where the user sent the command. We need this!
    chat_id = update.effective_chat.id

    # Save the chat ID so the background job knows where to send the news
    context.application.user_data['NEWS_CHAT_ID'] = chat_id

    await update.message.reply_text(
        f"Hello! I am your MAL News Bot. Your Chat ID ({chat_id}) has been saved."
        f"\nI will now start checking the @{TWITTER_USER_TO_FOLLOW} account periodically (every 15 minutes)."
    )

async def check_news_manually(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows a user to manually trigger a news check with /check_news."""
    await update.message.reply_text("Manually checking for new news posts...")
    # Call the core checking function
    await check_for_new_tweets(context)
    # The response after the check will be a tweet, or a 'No new tweets found' message from the main job.


# --- 2. THE NEWS CHECKING FUNCTION (The core logic) ---

async def check_for_new_tweets(context: ContextTypes.DEFAULT_TYPE):
    """Scrapes Twitter/X and sends new tweets to the saved chat ID."""

    # Get the chat ID from the application's user_data (set by /start)
    chat_id = context.application.user_data.get('NEWS_CHAT_ID')

    # Fail gracefully if we don't know where to send the message
    if not chat_id:
        print("NEWS_CHAT_ID not found. User needs to run /start.")
        return

    # A simple way to track the last tweet ID sent
    # We use bot_data which is persistent across runs (good for Replit)
    last_tweet_id = context.application.bot_data.get('LAST_TWEET_ID', 0)
    new_tweets_to_send = []

    try:
        # **Scraping Setup:**
        # Twikit needs a Client instance for scraping
        tw_client = Client()

        # Log in with your Twitter/X credentials
        # It's an async call, so we use await
        await tw_client.login(TW_USERNAME, TW_PASSWORD)

        # Find the MyAnimeList user
        user = await tw_client.get_user_by_screen_name(TWITTER_USER_TO_FOLLOW)

        # Get the latest 10 tweets (safe margin to not miss anything)
        tweets = await user.get_tweets('Tweets', count=10)

        latest_id_found = last_tweet_id

        # 2. Process Tweets
        # Process in reverse order (oldest first) to keep the correct chronological order
        for tweet in reversed(tweets):
            current_id = int(tweet.id)

            # If the current tweet is NEWER than the last one we sent (or if it's the first run)
            if current_id > last_tweet_id:

                # Format the message using MarkdownV2 syntax for links and bold text
                message_text = (
                    f"✨ *NEW MAL NEWS* ✨\n\n"
                    f"{tweet.full_text}\n\n"
                    # The URL must be escaped for MarkdownV2, but twikit provides the text
                    # We create the link manually here. Escaping the dot in x\.com is critical.
                    f"[View on X](https://x.com/{TWITTER_USER_TO_FOLLOW}/status/{current_id})"
                )
                new_tweets_to_send.append((message_text, current_id))

        # 3. Send New Tweets
        if new_tweets_to_send:
            for text, new_id in new_tweets_to_send:
                # Send the message to the user/chat
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    # Use MARKDOWN_V2 for rich formatting
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                # Update the ID tracker after each successful send
                latest_id_found = max(latest_id_found, new_id)

            # Save the ID of the very latest tweet we sent
            if latest_id_found > context.application.bot_data.get('LAST_TWEET_ID', 0):
                context.application.bot_data['LAST_TWEET_ID'] = latest_id_found
                print(f"Updated LAST_TWEET_ID to {latest_id_found}")
        else:
            await context.bot.send_message(chat_id=chat_id, text="No new tweets found on @myanimelist.")
            print("No new tweets found.")

    except Exception as e:
        # Send an error message to the chat so you know something broke
        # Note: We must escape the backticks for MarkdownV2
        error_message = f"🚨 *Error during news check:* \n`{str(e).replace('`', '’')}` \n_Please check your Render secrets or Twitter account status._"
        await context.bot.send_message(chat_id=chat_id, text=error_message, parse_mode=ParseMode.MARKDOWN_V2)
        print(f"Error: {e}")


# --- 3. BOT INITIALIZATION ---

def main():
    if not TOKEN or not TW_USERNAME or not TW_PASSWORD:
        # We also check the configuration values since the logic depends on them.
        print("ERROR: One or more required environment variables (BOT_TOKEN, TW_USERNAME, TW_PASSWORD) are missing.")
        # If secrets are missing, stop the bot from running.
        return

    # Build the application with the token and enable the job_queue for scheduling
    application = ApplicationBuilder().token(TOKEN).job_queue().build()

    # Initialize the LAST_TWEET_ID to 0 if it's not set
    if 'LAST_TWEET_ID' not in application.bot_data:
        application.bot_data['LAST_TWEET_ID'] = 0

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check_news", check_news_manually))

    # Add the scheduled job: Run the check_for_new_tweets function every 15 minutes (900 seconds)
    application.job_queue.run_repeating(check_for_new_tweets, interval=900, first=5)

    print("Bot is starting. Ready for /start and scheduled checks.")
    application.run_polling()

if __name__ == '__main__':
    # Removed the Replit-specific asyncio fix.
    main()
