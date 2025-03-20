import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.db.chat_history import add_user, verify_user, create_session
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or user.first_name
    
    if not await verify_user(user_id):
        await add_user(user_id, username, "telegram")
    
    session_id = await create_session(user_id, "Chat from Telegram")
    await update.message.reply_text(f"Chào {username}! Phiên chat của bạn đã bắt đầu (ID: {session_id}). Gửi tin nhắn để trò chuyện!")
    context.user_data["session_id"] = session_id

def run_telegram_bot():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    run_telegram_bot()