import telebot
import instaloader
import os
from flask import Flask, request

# ===============================
# Bot tokeni va webhook URL
BOT_TOKEN = "8505343593:AAFRtBsxIS8sMFo9PpsZ8vKPA7dpYZCNEf0"
WEBHOOK_URL = "https://instabot-otohir.onrender.com"  # Render Web Service URL
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
# ===============================

# Instaloader sozlamalari
loader = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False
)

# Agar private video yuklamoqchi bo'lsangiz:
# loader.login("INSTAGRAM_USERNAME", "INSTAGRAM_PASSWORD")

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Bot ishlayapti!")

# Habarlarni qabul qilish
@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    print(f"Received URL: {url}")

    try:
        shortcode = url.split("/")[-2]
    except IndexError:
        bot.reply_to(message, "Link noto‘g‘ri")
        return

    try:
        loader_message = bot.send_message(message.chat.id, "Video yuklanyapti...")
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)

        video_file = None
        for file in os.listdir(shortcode):
            if file.endswith(".mp4"):
                video_file = os.path.join(shortcode, file)
                break

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
        print("ERROR:", e)

# ===============================
# Flask route webhook uchun
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Webhookni o‘rnatish va serverni ishga tushurish
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=5000)
