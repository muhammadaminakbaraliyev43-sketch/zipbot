import asyncio
import logging
import os
import shutil
import zipfile
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

# --- SOZLAMALAR ---
# Railway-da o'zgaruvchilarni (Variables) bo'limida BOT_TOKEN ni kiriting
# Yoki mahalliy kompyuterda test qilish uchun tokeningizni shu yerga yozing:
BOT_TOKEN = os.getenv("BOT_TOKEN") 

# Yuklab olingan fayllar saqlanadigan asosiy papka
DOWNLOADS_DIR = "downloads"

# Loggingni yoqish (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlari
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- YORDAMCHI FUNKSIYALAR ---

def get_user_dir(user_id):
    """Foydalanuvchi uchun shaxsiy papka yo'lini qaytaradi"""
    return os.path.join(DOWNLOADS_DIR, str(user_id))

def clean_user_dir(user_id):
    """Foydalanuvchi papkasini tozalaydi"""
    path = get_user_dir(user_id)
    if os.path.exists(path):
        shutil.rmtree(path)

# --- HANDLERLAR (BOT MANTIG'I) ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Salom! Men fayllarni ZIP arxivga aylantirib beruvchi botman.\n\n"
        "1. Menga istalgancha fayl (rasm, video, hujjat) yuboring.\n"
        "2. Yakunlash uchun /zip buyrug'ini bosing.\n"
        "3. Bekor qilish uchun /clear buyrug'ini bosing."
    )
    # Eski fayllar qolib ketgan bo'lsa tozalaymiz
    clean_user_dir(message.from_user.id)

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    clean_user_dir(message.from_user.id)
    await message.answer("🗑 Barcha yuklangan fayllar tozalandi. Yangidan boshlashingiz mumkin.")

@dp.message(F.document | F.photo | F.video | F.audio)
async def handle_files(message: types.Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    # Papkani yaratamiz
    os.makedirs(user_dir, exist_ok=True)

    file_id = None
    file_name = None

    # Fayl turini aniqlash va nom berish
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        # Eng yuqori sifatdagisini olamiz
        file_id = message.photo[-1].file_id
        file_name = f"photo_{message.photo[-1].file_unique_id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{message.video.file_unique_id}.mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{message.audio.file_unique_id}.mp3"

    # Faylni yuklab olish
    if file_id:
        file_path = os.path.join(user_dir, file_name)
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, file_path)
        await message.answer(f"✅ {file_name} qabul qilindi.")

@dp.message(Command("zip"))
async def cmd_zip(message: types.Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    # Agar fayllar bo'lmasa
    if not os.path.exists(user_dir) or not os.listdir(user_dir):
        await message.answer("⚠️ Hali hech qanday fayl yuklamadingiz.")
        return

    await message.answer("📦 Arxivlanmoqda, kuting...")

    # Zip fayl nomi
    zip_filename = f"archive_{user_id}.zip"
    zip_path = os.path.join(DOWNLOADS_DIR, zip_filename)

    try:
        # Arxiv yaratish
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(user_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Arxiv ichida papka nomisiz saqlash uchun arcname ishlatamiz
                    zipf.write(file_path, arcname=file)

        # Arxivni foydalanuvchiga yuborish
        archive = FSInputFile(zip_path)
        await message.answer_document(archive, caption="Mana arxiv faylingiz! 🎁")

    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")
    
    finally:
        # Tozalash ishlari (papka va zip faylni o'chirish)
        clean_user_dir(user_id)
        if os.path.exists(zip_path):
            os.remove(zip_path)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Xatolik: BOT_TOKEN topilmadi!")
    else:
        asyncio.run(main())
