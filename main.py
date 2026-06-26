import os
import logging
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token ကို Environment Variable မှ ခေါ်ယူခြင်း
TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = 7771663458

# Web Server (Bot ကို အပြင်ကနေ လှမ်းနိုးရန်)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is alive!"

def run_server(): app.run(host='0.0.0.0', port=8080)
Thread(target=run_server, daemon=True).start()

def get_time():
    now = datetime.now(pytz.timezone('Asia/Yangon'))
    return f"{now.strftime('%H:%M')} clock\n{now.strftime('%d.%m.%Y')}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else "@Tear808"
    msg = f"👤 Name: {user.full_name}\n🆔 ID: {user.id}\n🔗 Username: {username}\n⏰ {get_time()}"
    
    photos = await user.get_profile_photos()
    if photos.total_count > 0:
        await update.message.reply_photo(photo=photos.photos[0][0].file_id, caption=msg)
    else:
        await update.message.reply_text(msg)

async def track_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for m in update.message.new_chat_members:
            await update.message.reply_text(f"🎉 ကြိုဆိုပါတယ် {m.full_name}!\n🆔 {m.id}\n📅 {get_time()}\n\n[မဂ်လာပရှင့်😍ကြိုဆိုပာတယ်နော်Mamber lay ray💝 မင်းgpရှိရင်နာကိုထည့်ပေးနော် 🫣အာဘွား🙂‍↔️🙂‍↔️]")
    
    if update.message.left_chat_member:
        m = update.message.left_chat_member
        await update.message.reply_text(f"👋 ထွက်ခွာသွားပါပြီ: {m.full_name}\n🆔 {m.id}\n📅 {get_time()}\n\n[သိပတယ်တစ်ချိန်ကျရင် မင်းထားခဲ့မယ်ဆိုတာ🥺ဟိုလူရင်ခွင်မပျောရင်ပြန်လာခဲ့နောါတီကောင်မကြီးကမင်းအတွက်အမြဲတမ်းအဆင့်သင့်ပေး😓😓]")

async def forward_to_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        await context.bot.forward_message(chat_id=OWNER_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, track_members))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_owner))
    app.run_polling()

if __name__ == '__main__':
    main()
