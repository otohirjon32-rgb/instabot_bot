import telebot
import instaloader
import os

# ===============================
# Bot tokeni
BOT_TOKEN = "8505343593:AAFRtBsxIS8sMFo9PpsZ8vKPA7dpYZCNEf0"
bot = telebot.TeleBot(BOT_TOKEN)
# ===============================

# Instaloader sozlamalari
loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)

# Agar private video yuklamoqchi bo'lsangiz, login qo'shing
# loader.login("INSTAGRAM_USERNAME", "INSTAGRAM_PASSWORD")

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Bot ishlayapti!")

# Habarlarni qabul qilish
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    print(f"Received URL: {url}")  # Loglash

    try:
        shortcode = url.split("/")[-2]
        print(f"Extracted shortcode: {shortcode}")
    except IndexError:
        bot.reply_to(message, "Link noto‘g‘ri")
        return

    try:
        loader_message = bot.send_message(message.chat.id, "Video yuklanyapti...")

        # Video postni yuklash
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)

        # Yuklangan videoni topish
        video_file = None
        for file in os.listdir(shortcode):
            if file.endswith(".mp4"):
                video_file = os.path.join(shortcode, file)
                break

        print(f"Files in folder: {os.listdir(shortcode)}")  # Loglash

        if video_file:
            with open(video_file, "rb") as video:
                bot.send_video(message.chat.id, video)
                bot.delete_message(message.chat.id, loader_message.message_id)

            # Fayllarni tozalash
            for f in os.listdir(shortcode):
                os.remove(os.path.join(shortcode, f))
            os.rmdir(shortcode)
        else:
            bot.delete_message(message.chat.id, loader_message.message_id)
            bot.reply_to(message, "Video topilmadi")

    except Exception as e:
        bot.delete_message(message.chat.id, loader_message.message_id)
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")
        print("ERROR:", e)  # Loglash

# Botni ishga tushirish
bot.infinity_polling()