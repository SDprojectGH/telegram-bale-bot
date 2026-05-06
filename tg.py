# bot_saver_stable.py
import sqlite3
import os
import sys
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = "8519561623:AAFKZYKfCgi1ktv4emEYjqZ1U-0euZdoN8k"
DB_PATH = "media_keys.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                user_key TEXT UNIQUE NOT NULL,
                file_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ دیتابیس ایجاد شد.")
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False
    finally:
        conn.close()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎬 ربات ذخیره‌کننده مدیا\n\n"
        "1. ویدیو بفرست\n"
        "2. کلید وارد کن"
    )

def handle_media(update: Update, context: CallbackContext):
    if update.message.video:
        file_id = update.message.video.file_id
        context.user_data['pending_file_id'] = file_id
        update.message.reply_text("✅ ویدیو دریافت شد. حالا کلید رو وارد کن:")
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data['pending_file_id'] = file_id
        update.message.reply_text("✅ عکس دریافت شد. حالا کلید رو وارد کن:")
    else:
        update.message.reply_text("❌ فقط ویدیو یا عکس بفرست.")

def handle_key(update: Update, context: CallbackContext):
    if 'pending_file_id' not in context.user_data:
        update.message.reply_text("❌ اول ویدیو بفرست، بعد کلید رو وارد کن.")
        return
    
    user_key = update.message.text.strip()
    if not user_key or len(user_key) < 3:
        update.message.reply_text("❌ کلید باید حداقل 3 کاراکتر باشه.")
        return
    
    file_id = context.user_data['pending_file_id']
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM media_keys")
        count = cursor.fetchone()[0]
        next_name = f"v{count + 1}"
        
        cursor.execute('INSERT INTO media_keys (name, user_key, file_id) VALUES (?, ?, ?)', 
                      (next_name, user_key, file_id))
        conn.commit()
        
        update.message.reply_text(f"✅ ذخیره شد!\nنام: {next_name}\nکلید: {user_key}")
        context.user_data.clear()
        
    except sqlite3.IntegrityError:
        update.message.reply_text("❌ این کلید قبلا استفاده شده.")
    except Exception as e:
        update.message.reply_text(f"❌ خطا: {e}")
    finally:
        conn.close()

def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ توکن ربات رو وارد کن!")
        sys.exit(1)
    
    if not init_db():
        sys.exit(1)
    
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video | Filters.photo, handle_media))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_key))
    
    print("✅ ربات اول اجرا شد...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
