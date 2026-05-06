# bot_retriever_auto_delete.py
import sqlite3
import requests
import os
import sys
import time
import shutil

# ========== تنظیمات ==========
BALE_BOT_TOKEN = "1549488371:29XqdtNJn_kbHRh3Vb1gPzv_5DysVjT0H94"
FIRST_BOT_TOKEN = "8519561623:AAFKZYKfCgi1ktv4emEYjqZ1U-0euZdoN8k"
DB_PATH = "media_keys.db"
DOWNLOAD_DIR = "downloads"
BACKUP_DIR = "backup"  # پوشه پشتیبان اختیاری
# ============================

# آدرس API بیل
BALE_API_URL = f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{FIRST_BOT_TOKEN}"

def check_tokens():
    """بررسی توکن‌ها"""
    if not BALE_BOT_TOKEN or BALE_BOT_TOKEN == "YOUR_BALE_BOT_TOKEN_HERE":
        print("❌ خطا: توکن ربات بیل وارد نشده!")
        return False
    
    try:
        resp = requests.get(f"{BALE_API_URL}/getMe", timeout=10)
        if resp.status_code == 200 and resp.json().get("ok"):
            print(f"✅ توکن بیل معتبر است")
        else:
            print("❌ توکن بیل نامعتبر است!")
            return False
    except Exception as e:
        print(f"❌ خطا در اتصال به بیل: {e}")
        return False
    
    if FIRST_BOT_TOKEN and FIRST_BOT_TOKEN != "YOUR_FIRST_BOT_TOKEN_HERE":
        try:
            resp = requests.get(f"{TELEGRAM_API_URL}/getMe", timeout=10)
            if resp.status_code == 200 and resp.json().get("ok"):
                print(f"✅ توکن تلگرام معتبر است")
            else:
                print("⚠️ توکن تلگرام نامعتبر است!")
        except:
            print("⚠️ خطا در اتصال به تلگرام!")
    else:
        print("⚠️ توکن تلگرام تنظیم نشده!")
    
    return True

def check_database():
    """بررسی دیتابیس"""
    if not os.path.exists(DB_PATH):
        print(f"❌ فایل دیتابیس '{DB_PATH}' وجود ندارد!")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='media_keys'")
        if not cursor.fetchone():
            print("❌ جدول media_keys در دیتابیس وجود ندارد!")
            conn.close()
            return False
        conn.close()
        print("✅ دیتابیس پیدا شد")
        return True
    except Exception as e:
        print(f"❌ خطا در خواندن دیتابیس: {e}")
        return False

def download_file(file_id, file_name):
    """دانلود فایل از تلگرام"""
    if not FIRST_BOT_TOKEN or FIRST_BOT_TOKEN == "YOUR_FIRST_BOT_TOKEN_HERE":
        return None, "توکن تلگرام تنظیم نشده"
    
    try:
        resp = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}", timeout=30)
        data = resp.json()
        
        if not data.get("ok"):
            return None, data.get("description", "خطا")
        
        file_path = data["result"]["file_path"]
        download_url = f"https://api.telegram.org/file/bot{FIRST_BOT_TOKEN}/{file_path}"
        
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        local_path = os.path.join(DOWNLOAD_DIR, file_name)
        
        r = requests.get(download_url, stream=True, timeout=60)
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return local_path, None
    except Exception as e:
        return None, str(e)

def send_message(chat_id, text):
    """ارسال پیام به بیل"""
    try:
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        resp = requests.post(f"{BALE_API_URL}/sendMessage", json=payload, timeout=30)
        return resp.json().get("ok", False)
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")
        return False

def send_video(chat_id, video_path, caption=""):
    """ارسال ویدیو به بیل و بررسی موفقیت"""
    try:
        # بررسی وجود فایل
        if not os.path.exists(video_path):
            return False, "فایل وجود ندارد"
        
        # بررسی حجم فایل (حداکثر 50 مگابایت برای بیل)
        file_size = os.path.getsize(video_path) / (1024 * 1024)
        if file_size > 50:
            return False, f"حجم فایل {file_size:.1f} مگابایت است (حداکثر 50 مگابایت)"
        
        with open(video_path, "rb") as f:
            files = {
                "video": f
            }
            data = {
                "chat_id": chat_id,
                "caption": caption
            }
            resp = requests.post(f"{BALE_API_URL}/sendVideo", data=data, files=files, timeout=120)
            result = resp.json()
            
            if result.get("ok"):
                return True, "موفق"
            else:
                return False, result.get("description", "خطای ناشناخته")
    except Exception as e:
        return False, str(e)

def delete_from_database(user_key):
    """حذف رکورد از دیتابیس"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # دریافت اطلاعات قبل از حذف
        cursor.execute("SELECT name, file_id, file_path FROM media_keys WHERE user_key = ?", (user_key,))
        result = cursor.fetchone()
        
        if result:
            # حذف از دیتابیس
            cursor.execute("DELETE FROM media_keys WHERE user_key = ?", (user_key,))
            conn.commit()
            print(f"✅ رکورد با کلید '{user_key}' از دیتابیس حذف شد")
            conn.close()
            return True, result
        else:
            conn.close()
            return False, None
    except Exception as e:
        print(f"❌ خطا در حذف از دیتابیس: {e}")
        return False, None

def delete_file(file_path):
    """حذف فایل از سرور"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ فایل {file_path} از سرور حذف شد")
            return True
        return False
    except Exception as e:
        print(f"❌ خطا در حذف فایل: {e}")
        return False

def backup_before_delete(file_path, user_key):
    """اختیاری: قبل از حذف یک نسخه پشتیبان بگیر"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backup_path = os.path.join(BACKUP_DIR, f"{user_key}_{int(time.time())}.mp4")
        shutil.copy2(file_path, backup_path)
        print(f"✅ نسخه پشتیبان در {backup_path} ذخیره شد")
        return True
    except Exception as e:
        print(f"⚠️ خطا در ایجاد پشتیبان: {e}")
        return False

def get_updates(offset=None):
    """دریافت آپدیت‌ها از بیل"""
    try:
        url = f"{BALE_API_URL}/getUpdates"
        if offset:
            url += f"?offset={offset}"
        
        resp = requests.get(url, timeout=30)
        data = resp.json()
        
        if data.get("ok"):
            return data.get("result", [])
        return []
    except Exception as e:
        print(f"خطا در دریافت آپدیت: {e}")
        return []

def process_message(message):
    """پردازش پیام دریافتی"""
    try:
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        
        if not text:
            return
        
        if text == "/start":
            send_message(chat_id, 
                        "🎬 به ربات دریافت ویدیو خوش آمدید!\n\n"
                        "🔑 لطفا کلید خود را وارد کنید:\n\n"
                        "⚠️ توجه: پس از دریافت موفق ویدیو، کلید شما از سیستم حذف خواهد شد و دیگر قابل استفاده نیست.")
            return
        
        # جستجوی کلید در دیتابیس
        send_message(chat_id, "🔍 در حال جستجوی کلید...")
        
        if not os.path.exists(DB_PATH):
            send_message(chat_id, "❌ خطای دیتابیس! لطفا بعداً تلاش کنید.")
            return
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # بررسی ساختار دیتابیس
        cursor.execute("PRAGMA table_info(media_keys)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'file_id' in columns:
            cursor.execute('SELECT name, file_id, user_key FROM media_keys WHERE user_key = ?', (text,))
            result = cursor.fetchone()
            file_type = "file_id"
        elif 'file_path' in columns:
            cursor.execute('SELECT name, file_path, user_key FROM media_keys WHERE user_key = ?', (text,))
            result = cursor.fetchone()
            file_type = "file_path"
        else:
            send_message(chat_id, "❌ خطا در ساختار دیتابیس!")
            conn.close()
            return
        
        conn.close()
        
        if not result:
            send_message(chat_id, f"❌ کلید '{text}' یافت نشد!\n\n"
                        "دلایل احتمالی:\n"
                        "1. کلید اشتباه وارد شده\n"
                        "2. این کلید قبلاً استفاده شده و حذف گردیده\n"
                        "3. کلید معتبر نیست")
            return
        
        name, file_ref, user_key = result
        send_message(chat_id, f"✅ کلید معتبر است!\n📹 در حال دریافت {name}...\n⚠️ پس از ارسال، کلید حذف می‌شود.")
        
        file_path = None
        is_temp_file = False
        
        if file_type == "file_id":
            if not FIRST_BOT_TOKEN or FIRST_BOT_TOKEN == "YOUR_FIRST_BOT_TOKEN_HERE":
                send_message(chat_id, "❌ خطا: توکن تلگرام تنظیم نشده!")
                return
            
            send_message(chat_id, "📥 در حال دانلود فایل...")
            file_path, error = download_file(file_ref, f"{name}.mp4")
            
            if error:
                send_message(chat_id, f"❌ خطا در دانلود: {error}")
                return
            is_temp_file = True
        else:
            file_path = file_ref
            if not os.path.exists(file_path):
                send_message(chat_id, "❌ فایل روی سرور وجود ندارد!")
                return
        
        # ارسال ویدیو
        send_message(chat_id, "📤 در حال ارسال ویدیو به بیل...")
        
        success, error_msg = send_video(chat_id, file_path, f"🎬 {name}\n🔑 {user_key}\n✅ دریافت شد!")
        
        if success:
            send_message(chat_id, "✅ ویدیو با موفقیت ارسال شد!\n🗑️ در حال حذف کلید از سیستم...")
            
            # ========== مرحله حذف ==========
            # 1. حذف از دیتابیس
            deleted, deleted_data = delete_from_database(user_key)
            
            if deleted:
                send_message(chat_id, "✅ کلید از دیتابیس حذف شد.\n🔒 این کلید دیگر قابل استفاده نیست.")
            else:
                send_message(chat_id, "⚠️ خطا در حذف از دیتابیس! لطفا به پشتیبانی اطلاع دهید.")
            
            # 2. حذف فایل فیزیکی (اگر فایل موقت دانلود شده بود)
            if is_temp_file and file_path and os.path.exists(file_path):
                # اختیاری: قبل از حذف پشتیبان بگیر
                # backup_before_delete(file_path, user_key)
                
                if delete_file(file_path):
                    print(f"فایل موقت {file_path} حذف شد")
                else:
                    print(f"خطا در حذف فایل {file_path}")
            
            # 3. اگر فایل از نوع file_path بود و در پوشه ذخیره‌سازی بود
            elif not is_temp_file and file_path and os.path.exists(file_path):
                send_message(chat_id, "⚠️ این فایل روی سرور ذخیره شده است. برای حذف دستی اقدام شود.")
                
        else:
            send_message(chat_id, f"❌ خطا در ارسال ویدیو!\n{error_msg}\n\n"
                        "ویدیو حذف نشد و کلید همچنان معتبر است.\n"
                        "لطفا دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.")
            
            # اگر ارسال ناموفق بود، فایل موقت را پاک کن
            if is_temp_file and file_path and os.path.exists(file_path):
                delete_file(file_path)
            
    except Exception as e:
        print(f"خطا در پردازش پیام: {e}")
        try:
            send_message(chat_id, f"❌ خطای سیستمی: {str(e)[:100]}\nلطفا دوباره تلاش کنید.")
        except:
            pass

def main():
    print("=" * 50)
    print("🚀 در حال راه‌اندازی ربات بیل (نسخه با حذف خودکار)...")
    print("=" * 50)
    
    # بررسی توکن‌ها
    if not check_tokens():
        print("❌ خطا در توکن‌ها. برنامه خاتمه یافت.")
        sys.exit(1)
    
    # بررسی دیتابیس
    if not check_database():
        print("⚠️ دیتابیس وجود ندارد!")
        response = input("ادامه می‌دهید؟ (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # ایجاد پوشه‌های مورد نیاز
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    print("\n✅ ربات با موفقیت راه‌اندازی شد!")
    print("📡 در حال دریافت پیام‌ها...")
    print("⚠️ پس از ارسال موفق، ویدیو و کلید از سیستم حذف می‌شوند.")
    print("=" * 50 + "\n")
    
    # حلقه اصلی دریافت آپدیت
    last_update_id = 0
    
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            
            for update in updates:
                if "message" in update:
                    process_message(update["message"])
                last_update_id = update["update_id"]
            
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 ربات متوقف شد.")
            break
        except Exception as e:
            print(f"خطا در حلقه اصلی: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
