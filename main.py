import os
import json
import random
import asyncio
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from datetime import datetime
import pytz

TOKEN = os.environ.get('BOT_TOKEN')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
OWNER_ID = 7771663458
TARGET_BOT = "Feel_Type_Bot"
DATA_FILE = "data.json"

app = Flask(__name__)
bot = Bot(TOKEN)
application = Application.builder().token(TOKEN).build()
group_ids = set()

def get_time():
    tz = pytz.timezone('Asia/Yangon')
    now = datetime.now(tz)
    return f"{now.strftime('%H:%M')} clock | {now.strftime('%d.%m.%Y')}"

# 1. စာသင်ပေးခြင်း
async def learn(update, context):
    if update.effective_user.id == OWNER_ID and "#" in " ".join(context.args):
        q, a = " ".join(context.args).split("#", 1)
        data = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f: data = json.load(f)
        data[q.strip().lower()] = a.strip()
        with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)
        await update.message.reply_text(f"✅ သင်ပေးလိုက်ပါပြီ။\nမေး: {q}\nဖြေ: {a}")

# 2. Command များ
async def start(update, context):
    kb = [[InlineKeyboardButton("ဆက်သွယ်ရန် (Bot)", url=f"https://t.me/{TARGET_BOT}")]]
    await update.message.reply_text("🌟 မင်္ဂလာပါ! အကူအညီအတွက် ခလုတ်ကို နှိပ်ပါ 👇", reply_markup=InlineKeyboardMarkup(kb))

# 3. Member စနစ် (ကဗျာလေးများနှင့်)
async def track_members(update, context):
    if update.message.new_chat_members:
        for m in update.message.new_chat_members:
            txt = (f"✨ ─── ⋆⋅☆⋅⋆ ─── ✨\n\n🎀 ကြိုဆိုပါတယ် ချစ်မိတ်ဆွေ {m.full_name} ရေ 🎀\n\n"
                   f"🌸 ပန်းသလိုလန်း၊ ရွှင်လန်းခြင်းများစွာနဲ့\nနွေးထွေးစွာ ကြိုဆိုလိုက်ပါတယ်ခင်ဗျာ။\n\n"
                   f"📅 {get_time()}\n✨ ─── ⋆⋅☆⋅⋆ ─── ✨")
            await update.message.reply_text(txt)
    if update.message.left_chat_member:
        m = update.message.left_chat_member
        txt = (f"🌧 ─── ⋆⋅❄⋅⋆ ─── 🌧\n\n🥀 အလွမ်းမျက်ရည်နဲ့ နှုတ်ဆက်ပါရစေ {m.full_name} ခင်ဗျာ...\n\n"
               f"💔 ထွက်ခွာသွားလည်း အမြဲသတိရနေမှာပါ။\n💫 ကံကြမ္မာပေးရင် ပြန်ဆုံကြပါဦးမယ်နော်။\n\n"
               f"📅 {get_time()}\n🌧 ─── ⋆⋅❄⋅⋆ ─── 🌧")
        await update.message.reply_text(txt)

# 4. Message Handler (Forward, Reaction, Auto-Reply)
async def handle_all(update, context):
    if not update.message or not update.message.text: return
    if update.message.chat.type in ['group', 'supergroup']:
        group_ids.add(update.message.chat.id)
        try: await update.message.set_reaction(reaction=random.choice(["❤️", "👍", "🔥"]))
        except: pass
    if update.message.chat.type == "private":
        await context.bot.forward_message(chat_id=OWNER_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for q, a in data.items():
                    if q in update.message.text.lower(): await update.message.reply_text(a)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("learn", learn))
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER, track_members))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    asyncio.run(application.process_update(Update.de_json(request.get_json(force=True), bot)))
    return "ok"

if __name__ == '__main__':
    bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
  
