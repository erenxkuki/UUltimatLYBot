# ========================================Tutorial==========================================#
#                                                                                                                                                                                                 #
#                                                               Cach cai bot tu A - Z by LongHip12                                                                    #
#                                                               B1: Tai Vscode tai https://code.visualstudio.com                                           #
#                                                               B2: Tai Python tai https://python.org                                                                 #
#                                                               B3: Tai Extension Duoi day:                                                                                 #
#                                                               Python by Microsoft,Jupyter,Path Intellisense,vscodeicon (tuy chon)         #
#                                                               B5: tai package duoi day:                                                                                    #
#                                                               pip install -U discord.py pytz art colorama                                                      #
#                                                               Invite: https://pastefy.app/OA5O3MX3                                                           #
#                                                                                                                                                                                             #
# ========================================Code===========================================

import asyncio
import datetime
import itertools
import json
import os
import random
import re
import subprocess
import uuid
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional
import aiohttp
import discord
import pytz
import yt_dlp as youtube_dl
from colorama import Fore, Style, init
from discord import FFmpegPCMAudio, app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from help_pages import build_help_pages, HelpView
init(autoreset=True)
intents = discord.Intents.all()

# Token For Bot

load_dotenv()
BotToken = os.getenv("DISCORD_BOT_TOKEN")

# Config Path For ffmpeg
FFMPEG_PATH = "/data/data/ru.iiec.pydroid3/files/ffmpeg/ffmpeg"

try:
    result = subprocess.run([FFMPEG_PATH, '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ FFmpeg found: {result.stdout.splitlines()[0]}")
    else:
        print("❌ FFmpeg not working")
except Exception as e:
    print(f"❌ FFmpeg error: {e}")

# Create the structure for queueing songs - Dictionary of queues
SONG_QUEUES = {}

async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)

# Màu rainbow chroma
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

ascii_art = r"""
 _                          _          ____          _
| |      ___   _ __    ___ | | _   _  | __ )   ___  | |_
| |     / _ \ | '_ \  / _ \| || | | | |  _ \  / _ \ | __|
| |___ | (_) || | | ||  __/| || |_| | | |_) || (_) || |_
|_____| \___/ |_| |_| \___||_| \__, | |____/  \___/  \__|
                               |___/
"""

def print_chroma(text):
    cycle_colors = itertools.cycle(colors)
    result = ""
    for char in text:
        if char.strip():  # có ký tự
            result += next(cycle_colors) + char + Style.RESET_ALL
        else:  # giữ khoảng trắng
            result += char
    print(result)

print_chroma(ascii_art)
print(Fore.GREEN + "=" * 67)

# Thư mục dữ liệu (relative tới file main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # thư mục chứa main.py
DATA_DIR = os.path.join(BASE_DIR, "Bot_Data")

# Tên file
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist_users.json")
BANNED_FILE    = os.path.join(DATA_DIR, "blacklist_users.json")
DATA_FILE = Path(os.path.join(DATA_DIR, "data.json"))
LEVEL_FILE = Path(os.path.join(DATA_DIR, "levels.json"))
REACTION_FILE = Path(os.path.join(DATA_DIR, "reaction_roles.json"))
SHOP_FILE = Path(os.path.join(DATA_DIR, "shop.json"))
DAILY_FILE = Path(os.path.join(DATA_DIR, "daily_login.json"))
BOX_FILE = Path(os.path.join(DATA_DIR, "box.json"))
WORK_FILE = Path(os.path.join(DATA_DIR, "work.json"))
TAIXIU_HISTORY_FILE = Path(os.path.join(DATA_DIR, "taixiu_history.json"))
CONFIG_FILE = os.path.join(DATA_DIR, "ticket_config.json")
TICKET_DATA = os.path.join(DATA_DIR, "ticket_data.json")
TAG_FILE = os.path.join(DATA_DIR, "tag.json")

# Biến toàn cục
ALLOWED_USERS = {}
BANNED_USERS = {}

# Tạo folder nếu chưa tồn tại
os.makedirs(DATA_DIR, exist_ok=True)

# Nếu file chưa có, khởi tạo file rỗng
for p in (WHITELIST_FILE, BANNED_FILE):
    if not os.path.exists(p):
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERROR] Không thể tạo file {p}: {e}")
# Hàm load/save cho whitelist
def save_whitelist():
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            # lưu key dưới dạng string để JSON hợp lệ
            json.dump({str(k): v for k, v in ALLOWED_USERS.items()}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] Không thể lưu {WHITELIST_FILE}: {e}")

def load_whitelist():
    global ALLOWED_USERS
    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # chuyển key về int nếu có thể
        ALLOWED_USERS = {}
        for k, v in data.items():
            try:
                ALLOWED_USERS[int(k)] = v
            except Exception:
                ALLOWED_USERS[k] = v
    except Exception as e:
        print(f"[ERROR] Không thể đọc {WHITELIST_FILE}: {e}")
        ALLOWED_USERS = {}

# Hàm load/save cho blacklist
def save_banned_users():
    try:
        with open(BANNED_FILE, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in BANNED_USERS.items()}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] Không thể lưu {BANNED_FILE}: {e}")

def load_banned_users():
    global BANNED_USERS
    try:
        with open(BANNED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        BANNED_USERS = {}
        for k, v in data.items():
            try:
                BANNED_USERS[int(k)] = v
            except Exception:
                BANNED_USERS[k] = v
    except Exception as e:
        print(f"[ERROR] Không thể đọc {BANNED_FILE}: {e}")
        BANNED_USERS = {}
        
def load_json(file_path):
    """Đọc dữ liệu từ file JSON một cách an toàn"""
    try:
        # Chuyển đổi path thành Path object nếu là string
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        if file_path.exists():
            return json.loads(file_path.read_text(encoding='utf-8'))
        return {}
    except (json.JSONDecodeError, Exception) as e:
        print(f"[ERROR] Không thể đọc file {file_path}: {e}")
        return {}

def save_json(path, data):
    """Lưu dữ liệu vào file JSON"""
    try:
        # Chuyển đổi path thành Path object nếu là string
        if isinstance(path, str):
            path = Path(path)
        
        # Đảm bảo thư mục tồn tại
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] Không thể lưu file {path}: {e}")
        
# Tạo file shop mẫu nếu chưa có
if not SHOP_FILE.exists():
    default_shop = {
        "vip": {"price": 10000, "role_id": 1420718498530721864, "name": "VIP Role", "description": "Receive the VIP Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},
        "vipplus": {"price": 50000, "role_id": 1420718386786340977, "name": "Vip+ Role", "description": "Receive the VIP+ Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},
        "vipplusplus": {"price": 70000, "role_id": 1421143311900479588, "name": "Vip++ Role", "description": "Receive the VIP+ Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},                                                         
        "mvp": {"price": 100000, "role_id": 1421143426795307018, "name": "MVP Role", "description": "Receive the MVP Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},
        "mvpplus": {"price": 150000, "role_id": 1421143520034426971, "name": "MVP+ Role", "description": "Receive the MVP+ Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},
        "mvpplusplus": {"price": 300000, "role_id": 1421143612543991900, "name": "MVP++ Role", "description": "Receive the MVP++ Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."},
        "managerbot": {"price": 999999999999, "role_id": 1410600949646364702, "name": "Manager Role", "description": "Receive the Manager Rank on the Lonely Hub Script, Lonely Hub Forums, and Lonely Hub Discord."}
    }
    save_json(SHOP_FILE, default_shop)  # ĐÚNG: path trước, data sau

credits = load_json(DATA_FILE)
box = load_json(BOX_FILE)
levels = load_json(LEVEL_FILE)
reaction_roles = load_json(REACTION_FILE)
shop_data = load_json(SHOP_FILE)
daily_data = load_json(DAILY_FILE)
work_data = load_json(WORK_FILE)
taixiu_history = load_json(TAIXIU_HISTORY_FILE)

# ====== ECONOMY FUNCTIONS ======
def get_balance(user_id):
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    return credits.get(user_id, 0)

def add_balance(user_id, amount):
    """Thêm coin cho user"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    credits[user_id] = get_balance(user_id) + amount
    save_json(DATA_FILE, credits)
    return credits[user_id]

def remove_balance(user_id, amount):
    """Trừ coin của user"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    if get_balance(user_id) >= amount:
        credits[user_id] -= amount
        save_json(DATA_FILE, credits)
        return credits[user_id]
    return None

def set_balance(user_id, amount):
    """Đặt số dư coin cho user"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    credits[user_id] = amount
    save_json(DATA_FILE, credits)
    return credits[user_id]

def can_daily(user_id):
    """Kiểm tra user có thể nhận daily không"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    if user_id not in daily_data:
        return True
    
    last_daily = datetime.datetime.fromisoformat(daily_data[user_id]["last_claimed"])
    now = datetime.datetime.now()
    return (now - last_daily).days >= 1

def can_work(user_id):
    """Kiểm tra user có thể work không"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    if user_id not in work_data:
        return True, 0
    
    last_work_date = datetime.datetime.fromisoformat(work_data[user_id]["last_date"]).date()
    today = datetime.datetime.now().date()
    
    # Nếu khác ngày thì reset
    if last_work_date != today:
        work_data[user_id]["count"] = 0
        work_data[user_id]["last_date"] = today.isoformat()
        save_json(WORK_FILE, work_data)
        return True, 0
    
    return work_data[user_id]["count"] < 5, work_data[user_id]["count"]
    
# ====== ECONOMY FUNCTIONS ======

def get_box(user_id: int) -> int:
    return box.get(str(user_id), 0)

def add_box(user_id: int, amount: int):
    uid = str(user_id)
    box[uid] = get_box(uid) + amount
    save_json(BOX_FILE, box)  # ĐÚNG: path trước, data sau
    return box[uid]

def remove_box(user_id: int, amount: int):
    uid = str(user_id)
    if get_box(uid) >= amount:
        box[uid] -= amount
        save_json(BOX_FILE, box)  # ĐÚNG: path trước, data sau
        return box[uid]
    return None

def set_box(user_id: int, amount: int):
    uid = str(user_id)
    box[uid] = max(0, amount)
    save_json(BOX_FILE, box)  # ĐÚNG: path trước, data sau
    return box[uid]
    
def simple_embed(title: str, description: str, color: discord.Color = discord.Color.blue()):
    """
    Hàm tạo embed đơn giản để dùng lại nhiều lần
    """
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed
    
def update_daily(user_id):
    """Cập nhật thời gian daily"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    now = datetime.datetime.now()
    daily_data[user_id] = {
        "last_claimed": now.isoformat(),
        "date": now.strftime("%d/%m/%Y"),
        "time": now.strftime("%H:%M:%S")
    }
    save_json(DAILY_FILE, daily_data)

def update_work(user_id):
    """Cập nhật số lần work"""
    user_id = str(user_id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    today = datetime.datetime.now().date()
    
    if user_id not in work_data:
        work_data[user_id] = {"count": 0, "last_date": today.isoformat()}
    
    # Nếu khác ngày thì reset
    if datetime.datetime.fromisoformat(work_data[user_id]["last_date"]).date() != today:
        work_data[user_id]["count"] = 0
        work_data[user_id]["last_date"] = today.isoformat()
    
    work_data[user_id]["count"] += 1
    work_data[user_id]["last_work"] = datetime.datetime.now().isoformat()
    work_data[user_id]["date"] = datetime.datetime.now().strftime("%d/%m/%Y")
    work_data[user_id]["time"] = datetime.datetime.now().strftime("%H:%M:%S")
    save_json(WORK_FILE, work_data)
    
# Cấu hình bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=['!', '?', '.', '/'], intents=intents)

# URLs
ICON_URL = "https://i.imgur.com/TWW22k4.jpeg"
FOOTER_ICON_URL = "https://i.imgur.com/TWW22k4.jpeg"
BANNER_URL = ""

# Thiết lập múi giờ UTC+7
UTC7 = pytz.timezone('Asia/Bangkok')  # Bangkok là UTC+7

# GUILD ID bị cấm sử dụng spam và ghostping
RESTRICTED_GUILD_ID = 1409783780217983029
TARGET_GUILD_ID = 1409783780217983029
LOG_CHANNEL_ID = 1409785969200070776

def is_user_allowed(user_id):
    """Kiểm tra xem user có được phép sử dụng lệnh đặc biệt không"""
    return user_id in ALLOWED_USERS

def is_user_banned(user_id):
    """Kiểm tra xem user có bị cấm sử dụng bot không"""
    return user_id in BANNED_USERS

def load_ticket_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default

def save_ticket_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
def get_banned_users_table():
    """Hiển thị danh sách user bị ban (mobile-friendly)"""
    if not BANNED_USERS:
        return (
            "```\n📋 Danh sách người dùng bị cấm:\n"
            "--------------------------------\n"
            "Không có người dùng nào bị cấm\n"
            "--------------------------------\n```"
        )
    
    table = "```\n📋 Danh sách người dùng bị cấm:\n"
    table += "-" * 23 + "\n"
    for user_id, ban_info in BANNED_USERS.items():
        # Phòng khi ban_info không đủ key
        reason = ban_info.get("reason", "Không rõ")
        banned_by = ban_info.get("banned_by", "Không rõ")
        banned_at = ban_info.get("banned_at", "Không rõ")

        table += f"👤 User ID : {user_id}\n"
        table += f"📝 Lý do   : {reason}\n"
        table += f"🛡️ Bởi    : {banned_by}\n"
        table += f"⏰ Thời gian: {banned_at}\n"
        table += "-" * 23 + "\n"
    table += f"Tổng số: {len(BANNED_USERS)} user bị cấm\n```"
    return table

def get_allowed_users_table():
    """Đọc trực tiếp từ whitelist.json và trả về bảng user (mobile-friendly)."""
    if not os.path.exists(WHITELIST_FILE):
        return "⚠️ Hiện chưa có user nào trong whitelist."

    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return f"⚠️ Lỗi khi đọc whitelist.json: {e}"

    if not data:
        return "⚠️ Hiện chưa có user nào trong whitelist."

    table = "```\nDanh sách user whitelist:\n"
    table += "-" * 31 + "\n"
    for user_id, user_name in data.items():
        table += f"Tên: {user_name}\n"
        table += f"ID : {user_id}\n"
        table += "-" * 31 + "\n"
    table += f"Tổng số: {len(data)} user được cấp quyền admin\n```"
    return table

def setup_logging():
    """Tạo thư mục logs nếu chưa tồn tại"""
    if not os.path.exists('Logs'):
        os.makedirs('Logs')

def add_taixiu_history(user_id, dice, total, result, win, amount):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status = "win" if win else "lose"
    dice_str = f"{dice[0]},{dice[1]},{dice[2]}={total},{result.capitalize()}"

    record = {
        "time": now,
        "result": f"{status},{dice_str}",
        "amount": amount
    }

    user_id = str(user_id)
    if user_id not in taixiu_history:
        taixiu_history[user_id] = []
    taixiu_history[user_id].insert(0, record)
    taixiu_history[user_id] = taixiu_history[user_id][:5]
    save_json(TAIXIU_HISTORY_FILE, taixiu_history)  # ĐÃ SỬA THỨ TỰ THAM SỐ
    
def get_utc7_time():
    """Lấy thời gian hiện tại theo UTC+7"""
    now = datetime.datetime.now(UTC7)
    return now
    
ROLES = {
    "vip": {"role_id": 1420718498530721864, "name": "<:vip:1421359862780264489> VIP Rank"},
    "vipplus": {"role_id": 1420718386786340977, "name": "<:vipplus:1421359801975312436> Vip+ Rank"},
    "vipplusplus": {"role_id": 1421143311900479588, "name": "<:vipplusplus:1421359758711062619> Vip++ Rank"},
    "mvp": {"role_id": 1421143426795307018, "name": "<:mvp:1421359907030171699> MVP Rank"},
    "mvpplus": {"role_id": 1421143520034426971, "name": "<:mvpplus:1421359951028162560> MVP+ Rank"},
    "mvpplusplus": {"role_id": 1421143612543991900, "name": "<:mvpplusplus:1421359974092902481> MVP++ Rank"},
    "managerbot": {"role_id": 1410600949646364702, "name": "<:manager:1421365250690777139> Manager Rank"}
}

ROLE_PRIORITY = [
    ("managerbot", "[Manager]"),
    ("mvpplusplus", "[MVP++]"),
    ("mvpplus", "[MVP+]"),
    ("mvp", "[MVP]"),
    ("vipplusplus", "[Vip++]"),
    ("vipplus", "[Vip+]"),
    ("vip", "[VIP]")
]

@tasks.loop(seconds=1)  # check mỗi 30 giây
async def check_roles():
    await bot.wait_until_ready()
    guild = bot.get_guild(TARGET_GUILD_ID)
    if not guild:
        return

    for member in guild.members:
        if member.bot:
            continue  # bỏ qua bot

        # tìm role cao nhất user có
        highest_prefix = None
        for key, prefix in ROLE_PRIORITY:
            role_id = shop_data.get(key, {}).get("role_id")
            role = guild.get_role(role_id) if role_id else None
            if role and role in member.roles:
                highest_prefix = prefix
                break

        # nếu có role thì đổi tên
        if highest_prefix:
            if not member.display_name.startswith(highest_prefix):
                try:
                    await member.edit(nick=f"{highest_prefix} {member.name}")
                except Exception as e:
                    print(f"Lỗi đổi tên {member}: {e}")
        else:
            # nếu mất hết role thì reset nickname
            if member.nick and any(member.nick.startswith(p) for _, p in ROLE_PRIORITY):
                try:
                    await member.edit(nick=None)
                except Exception as e:
                    print(f"Lỗi reset tên {member}: {e}")
                    
def get_tag_emoji_for_dropdown(tag_name: str):
    """Chỉ lấy emoji cho dropdown, không trả về tag_name"""
    emoji_map = {
        "LGBT": "♀️",
        "PIG": "🐷", "PIG+": "🐷", "PIG++": "🐷",
        "GOD": "👼",
        "BETA TESTER": "🖥️",

        # Custom emoji
        "VIP": ("vip", 1421359862780264489),
        "VIP+": ("vipplus", 1421359801975312436),
        "VIP++": ("vipplusplus", 1421359758711062619),
        "MVP": ("mvp", 1421359907030171699),
        "MVP+": ("mvpplus", 1421359951028162560),
        "MVP++": ("mvpplusplus", 1421359974092902481),
        "Manager": ("manager", 1421365250690777139)
    }

    val = emoji_map.get(tag_name)
    if not val:
        return None

    # Nếu là tuple (custom emoji)
    if isinstance(val, tuple):
        name, emoji_id = val
        return discord.PartialEmoji(name=name, id=emoji_id)

    # Unicode emoji (string)
    return val

# Giữ nguyên hàm cũ cho các chỗ khác
def extract_name_and_emoji_from_tag(tag_name: str):
    emoji_map = {
        "LGBT": "♀️",
        "PIG": "🐷", "PIG+": "🐷", "PIG++": "🐷",
        "GOD": "👼",
        "BETA TESTER": "🖥️",

        # Custom emoji
        "VIP": ("vip", 1421359862780264489),
        "VIP+": ("vipplus", 1421359801975312436),
        "VIP++": ("vipplusplus", 1421359758711062619),
        "MVP": ("mvp", 1421359907030171699),
        "MVP+": ("mvpplus", 1421359951028162560),
        "MVP++": ("mvpplusplus", 1421359974092902481),
        "Manager": ("manager", 1421365250690777139)
    }

    val = emoji_map.get(tag_name)
    if not val:
        return None, tag_name

    # Nếu là tuple (custom emoji)
    if isinstance(val, tuple):
        name, emoji_id = val
        return discord.PartialEmoji(name=name, id=emoji_id), tag_name

    # Unicode emoji (string)
    return val, tag_name
    
# Thêm vào đầu file (sau setup_logging / get_utc7_time)
def log(message: str):
    """Hàm log đơn giản — in console và ghi file hàng ngày."""
    now = get_utc7_time()
    timestamp = now.strftime("[%H:%M:%S | %d/%m/%Y]")
    log_message = f"{timestamp} {message}"
    try:
        print(log_message)
        log_filename = now.strftime("Logs/command_log_%d-%m-%Y.txt")
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        # Không ném lỗi từ hàm log để tránh phá flow chính
        print(f"[LOG ERROR] {e}")

# -------------------
# Utility parsing roles
# -------------------
def parse_role_string(role_str: str) -> List[int]:
    """
    Accept input like: '<@&111> <@&222>'  or '111 222' or '111,222'
    Return list of ints (role IDs)
    """
    if not role_str:
        return []
    role_str = role_str.replace(",", " ")
    parts = role_str.split()
    ids = []
    for p in parts:
        if p.startswith("<@&") and p.endswith(">"):
            try:
                ids.append(int(p[3:-1]))
            except:
                continue
        else:
            try:
                ids.append(int(p))
            except:
                continue
    return ids
    
# -------------------
# CloseTicketView (xoá kênh sau 10s)
# -------------------
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Đóng Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        try:
            await channel.edit(overwrites=overwrites, name=f"closed-{channel.name}")
        except Exception:
            pass

        embed = discord.Embed(
            title="🔒 Ticket đã được đóng",
            description=f"Channel sẽ bị xóa sau 10 giây.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        if LOG_CHANNEL_ID:
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                lc_embed = discord.Embed(
                    title="🔒 Ticket Đóng",
                    description=f"Ticket {channel.mention} đã được đóng bởi {interaction.user.mention}. Xoá sau 10s.",
                    color=discord.Color.red()
                )
                await log_channel.send(embed=lc_embed)

        await asyncio.sleep(10)
        try:
            await channel.delete(reason=f"Ticket closed by {interaction.user}")
        except Exception as e:
            print(f"Lỗi xoá kênh ticket: {e}")
            
def add_ticket(channel_id, user_id):
    data = load_ticket_json(TICKET_DATA, {})
    data[str(channel_id)] = {
        "user_id": user_id,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "active": False
    }
    save_ticket_json(TICKET_DATA, data)

def set_active(channel_id):
    data = load_ticket_json(TICKET_DATA, {})
    if str(channel_id) in data:
        data[str(channel_id)]["active"] = True
        save_ticket_json(TICKET_DATA, data)
        
def log_command(user, command_name, guild_name, command_type="Text Command"):
    """Ghi log vào file và console"""
    # Lấy thời gian hiện tại theo UTC+7
    now = get_utc7_time()
    timestamp = now.strftime("[%H:%M:%S | %d/%m/%Y]")
    
    # Format log message
    log_message = f"{timestamp} {user}: {command_name} ({guild_name}) [{command_type}]"
    
    # Ghi vào console
    print(log_message)
    
    # Ghi vào file (theo ngày)
    log_filename = now.strftime("Logs/command_log_%d-%m-%Y.txt")
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write(log_message + '\n')
    
    return log_message

async def send_dm_notification(user, command_name, guild_name, command_type):
    """Gửi thông báo đến DM dạng Embed cho tất cả user được phép"""
    current_time = get_utc7_time()
    time_str = current_time.strftime("%H:%M:%S %d/%m/%Y")
    
    for user_id in ALLOWED_USERS.keys():
        try:
            user_obj = await bot.fetch_user(user_id)
            
            embed = discord.Embed(
                title="Lonely Hub Notification",
                color=discord.Color.blue(),
                timestamp=current_time
            )
            
            # Set author với icon
            embed.set_author(
                name="Lonely Hub Command Log",
                icon_url=ICON_URL
            )
            
            # Thêm các field theo format yêu cầu
            embed.add_field(
                name="[🤖] Command:",
                value=f"```{command_name}```",
                inline=False
            )
            
            embed.add_field(
                name="[👤] User:",
                value=f"```{user}```",
                inline=True
            )
            
            embed.add_field(
                name="[🏠] Server:",
                value=f"```{guild_name}```",
                inline=True
            )
            
            embed.add_field(
                name="[📝] Type:",
                value=f"```{command_type}```",
                inline=True
            )
            
            embed.add_field(
                name="[🕐] Command Run Time:",
                value=f"```{time_str} (UTC+7)```",
                inline=False
            )
            
            # Set footer với icon
            embed.set_footer(
                text=f"Lonely Hub | {time_str}",
                icon_url=FOOTER_ICON_URL
            )
            
            # Set thumbnail
            embed.set_thumbnail(url=ICON_URL)
            
            await user_obj.send(embed=embed)
            
        except Exception as e:
            print(f"Không thể gửi DM cho user {user_id}: {e}")

@bot.event
async def on_ready():
    # Load dữ liệu whitelist và blacklist từ file
    load_whitelist()
    load_banned_users()
    
    # In ra trạng thái bot
    print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} {Fore.GREEN}{bot.user}{Style.RESET_ALL} đã kết nối thành công!")
    print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Múi giờ: {Fore.YELLOW}UTC+7{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Đã load {Fore.BLUE}{len(ALLOWED_USERS)}{Style.RESET_ALL} user whitelist")
    print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Đã load {Fore.RED}{len(BANNED_USERS)}{Style.RESET_ALL} user bị cấm")
    
    try:
        synced = await bot.tree.sync()
        print(f"{Fore.CYAN}[Info]{Style.RESET_ALL} Đã đồng bộ {Fore.YELLOW}{len(synced)}{Style.RESET_ALL} slash command(s)")
        print("=" * 31 + "Console" + "=" * 29)
    except Exception as e:
        print(f"{Fore.RED}[Error]Lỗi đồng bộ slash commands: {Fore.YELLOW}{e}{Style.RESET_ALL}")
    
# ==================== CÁC LỆNH MỚI: BAN/UNBAN/WHITELIST ====================

# /box
@bot.tree.command(name="box", description="Xem số Mystery Box bạn đang có")
async def box_cmd(interaction: discord.Interaction):
    amount = get_box(interaction.user.id)
    embed = discord.Embed(
        title="📦 Kho Mystery Box",
        description=f"Bạn hiện có **{amount}** <:enderchest:1422102654766678116>",
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/box", guild_name, "Slash Command")
    await send_dm_notification(user, "/box", guild_name, "Slash Command")

# /boxopen
@bot.tree.command(name="boxopen", description="Mở Mystery Box")
async def boxopen(interaction: discord.Interaction):
    user_id = str(interaction.user.id)  # ĐẢM BẢO CHUYỂN THÀNH STRING

    if get_box(user_id) <= 0:
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Không có box",
                description="Bạn không có Mystery Box nào để mở!",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    # trừ box
    remove_box(user_id, 1)

    opening_embed = discord.Embed(
        description="<a:EnderChestNew:1422144204129304607>\n**Đang mở mystery box...**",
        color=discord.Color.orange()
    )

    # gửi tin nhắn trực tiếp trong channel
    channel = interaction.channel
    msg = await channel.send(embed=opening_embed)

    await asyncio.sleep(5)

    rewards = [
        ("200 Coins", 55),
        ("LGBT", 50),
        ("PIG", 20),
        ("PIG+", 15),
        ("PIG++", 10),
        ("GOD", 5),
        ("BETA TESTER", 1),
        (None, 100)  # không trúng gì
    ]
    choice = random.choices(
        [r for r, _ in rewards],
        weights=[w for _, w in rewards],
        k=1
    )[0]

    if choice is None:
        result_embed = discord.Embed(
            title="😢 Rất tiếc!",
            description="Bạn không nhận được gì từ Mystery Box.",
            color=discord.Color.red()
        )

    elif choice == "200 Coins":
        add_balance(user_id, 200)
        result_embed = discord.Embed(
            title="🎉 Chúc mừng!",
            description=f"Bạn nhận được **200 <:lonelycoin:1421380256148750429>**",
            color=discord.Color.green()
        )

    else:
        # add role nếu có trong tag.json
        tags = load_json(TAG_FILE)
        role_id = tags.get(choice)
        if role_id:
            member = interaction.guild.get_member(interaction.user.id)
            if member:
                role = interaction.guild.get_role(role_id)
                if role:
                    if role in member.roles:
                        result_embed = discord.Embed(
                            title="⚠️ Thông báo",
                            description=f"Bạn đã có rank **{choice}** rồi!",
                            color=discord.Color.orange()
                        )
                    else:
                        await member.add_roles(role)
                        result_embed = discord.Embed(
                            title="🎉 Chúc mừng!",
                            description=f"Bạn nhận được rank **{choice}**!",
                            color=discord.Color.green()
                        )

    # edit tin nhắn ban đầu thành kết quả
    await msg.edit(embed=result_embed)

    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/boxopen", guild_name, "Slash Command")
    
    await send_dm_notification(user, "/boxopen", guild_name, "Slash Command")
    
# ==================== ADMIN BOX COMMANDS ====================
# ==================== ADMIN BOX COMMANDS ====================
@bot.tree.command(name="join", description="Tham gia vào voice channel")
async def join(interaction: discord.Interaction):
    print(f"\n[JOIN] Command được gọi bởi {interaction.user.name}")
    
    try:
        # Kiểm tra xem user có trong voice channel không
        if not interaction.user.voice or not interaction.user.voice.channel:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bạn cần phải ở trong một voice channel!",
                color=discord.Color.red()
            )
            print("[JOIN] User không ở trong voice channel")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        print(f"[JOIN] User ở trong channel: {voice_channel.name}")
        
        # Kiểm tra quyền kết nối
        permissions = voice_channel.permissions_for(interaction.guild.me)
        if not permissions.connect:
            embed = discord.Embed(
                title="❌ Lỗi quyền",
                description="Tôi không có quyền kết nối đến voice channel này!",
                color=discord.Color.red()
            )
            print("[JOIN] Bot không có quyền connect")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Kiểm tra xem bot đã ở trong voice channel chưa
        voice_client = interaction.guild.voice_client
        
        if voice_client and voice_client.is_connected():
            print(f"[JOIN] Bot đang ở channel: {voice_client.channel.name}")
            if voice_client.channel.id == voice_channel.id:
                embed = discord.Embed(
                    title="⚠️ Thông báo",
                    description=f"Tôi đã ở trong voice channel **{voice_channel.name}** rồi!",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
                print("[JOIN] Bot đã ở trong channel này")
                return
            else:
                # Di chuyển sang channel khác
                print(f"[JOIN] Di chuyển từ {voice_client.channel.name} đến {voice_channel.name}")
                await voice_client.move_to(voice_channel)
                print("[JOIN] Đã di chuyển thành công")
        else:
            # Defer vì kết nối voice có thể mất thời gian
            await interaction.response.defer()
            print("[JOIN] Đã defer, đang kết nối...")
            
            # Kết nối đến voice channel
            voice_client = await voice_channel.connect(timeout=10.0, reconnect=True)
            print(f"[JOIN] Kết nối thành công: {voice_client.is_connected()}")
            
            # Đợi để đảm bảo kết nối ổn định
            await asyncio.sleep(0.3)

        # Tạo embed thông báo
        embed = discord.Embed(
            title="✅ Đã tham gia voice channel",
            description=f"Đã kết nối đến **{voice_channel.name}**",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Channel", value=voice_channel.mention, inline=True)
        embed.add_field(name="Thành viên", value=len(voice_channel.members), inline=True)
        
        if interaction.user.display_avatar:
            embed.set_footer(
                text=f"Yêu cầu bởi {interaction.user.display_name}", 
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name}")
        
        # Gửi tin nhắn - kiểm tra đã defer chưa
        print("[JOIN] Đang gửi thông báo...")
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)
        print("[JOIN] Đã gửi thông báo thành công!")
        
    except asyncio.TimeoutError:
        print("[JOIN] Lỗi timeout khi kết nối")
        embed = discord.Embed(
            title="❌ Lỗi kết nối",
            description="Không thể kết nối đến voice channel (timeout)!",
            color=discord.Color.red()
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f"[JOIN] Lỗi: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        embed = discord.Embed(
            title="❌ Lỗi hệ thống",
            description=f"Có lỗi xảy ra khi tham gia voice channel!",
            color=discord.Color.red()
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            print("[JOIN] Không thể gửi thông báo lỗi")

@bot.tree.command(name="leave", description="Rời khỏi voice channel")
async def leave(interaction: discord.Interaction):
    print(f"\n[LEAVE] Command được gọi bởi {interaction.user.name}")
    
    try:
        # Kiểm tra xem bot có trong voice channel không
        voice_client = interaction.guild.voice_client
        
        if not voice_client or not voice_client.is_connected():
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Tôi không ở trong voice channel nào!",
                color=discord.Color.red()
            )
            print("[LEAVE] Bot không ở trong voice channel")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Lưu thông tin channel TRƯỚC khi disconnect
        voice_channel = voice_client.channel
        voice_channel_name = voice_channel.name
        voice_channel_mention = voice_channel.mention
        print(f"[LEAVE] Bot đang ở channel: {voice_channel_name}")
        
        # Defer vì disconnect có thể mất thời gian
        await interaction.response.defer()
        print("[LEAVE] Đã defer, đang disconnect...")
        
        # Xóa queue của guild này
        guild_id = str(interaction.guild_id)
        if guild_id in SONG_QUEUES:
            SONG_QUEUES[guild_id].clear()
            print(f"[LEAVE] Đã xóa queue của guild {guild_id}")
        
        # Rời khỏi voice channel
        await voice_client.disconnect(force=True)
        print("[LEAVE] Đã disconnect")
        
        # Đợi để đảm bảo disconnect hoàn tất
        await asyncio.sleep(0.3)

        # Tạo embed thông báo
        embed = discord.Embed(
            title="👋 Đã rời voice channel",
            description=f"Đã rời khỏi **{voice_channel_name}**",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Channel", value=voice_channel_mention, inline=True)
        
        if interaction.user.display_avatar:
            embed.set_footer(
                text=f"Yêu cầu bởi {interaction.user.display_name}", 
                icon_url=interaction.user.display_avatar.url
            )
        else:
            embed.set_footer(text=f"Yêu cầu bởi {interaction.user.display_name}")
        
        print("[LEAVE] Đang gửi thông báo...")
        await interaction.followup.send(embed=embed)
        print("[LEAVE] Đã gửi thông báo thành công!")
        
    except Exception as e:
        print(f"[LEAVE] Lỗi: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        # Thử cleanup voice client
        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect(force=True)
                print("[LEAVE] Đã cleanup voice client")
        except:
            pass
        
        embed = discord.Embed(
            title="❌ Lỗi hệ thống",
            description=f"Có lỗi xảy ra khi rời voice channel!",
            color=discord.Color.red()
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            print("[LEAVE] Không thể gửi thông báo lỗi")

@bot.tree.command(name="skip", description="Skips the current playing song")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        await interaction.response.send_message("⏭️ Đã skip bài hát!")
    else:
        await interaction.response.send_message("❌ Không có bài hát nào đang phát!")


@bot.tree.command(name="pause", description="Pause the currently playing song.")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("❌ Tôi không ở trong voice channel!")

    if not voice_client.is_playing():
        return await interaction.response.send_message("❌ Không có bài hát nào đang phát!")
    
    voice_client.pause()
    await interaction.response.send_message("⏸️ Đã tạm dừng!")


@bot.tree.command(name="resume", description="Resume the currently paused song.")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        return await interaction.response.send_message("❌ Tôi không ở trong voice channel!")

    if not voice_client.is_paused():
        return await interaction.response.send_message("❌ Bài hát không bị tạm dừng!")
    
    voice_client.resume()
    await interaction.response.send_message("▶️ Đã tiếp tục phát!")


@bot.tree.command(name="stop", description="Stop playback and clear the queue.")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        return await interaction.response.send_message("❌ Tôi không kết nối đến voice channel!")

    guild_id_str = str(interaction.guild_id)
    if guild_id_str in SONG_QUEUES:
        SONG_QUEUES[guild_id_str].clear()

    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    await voice_client.disconnect()
    await interaction.response.send_message("🛑 Đã dừng phát và ngắt kết nối!")


@bot.tree.command(name="play", description="Play a song or add it to the queue.")
@app_commands.describe(song_query="Tên bài hát hoặc URL YouTube")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()
    print(f"\n[PLAY] Command được gọi bởi {interaction.user.name}")
    print(f"[PLAY] Tìm kiếm: {song_query}")

    # Kiểm tra user có trong voice channel không
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send("❌ Bạn cần phải ở trong voice channel!")
        return

    voice_channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client

    # CHỈ KIỂM TRA KẾT NỐI, KHÔNG TỰ ĐỘNG KẾT NỐI
    if voice_client is None:
        await interaction.followup.send("❌ Bot chưa tham gia voice channel! Hãy dùng lệnh `/join` trước.")
        return
    
    # Kiểm tra xem bot có ở cùng voice channel với user không
    if voice_client.channel != voice_channel:
        await interaction.followup.send("❌ Bot không ở trong voice channel của bạn! Hãy dùng lệnh `/join` hoặc mời bot vào channel của bạn.")
        return

    # Kiểm tra kết nối
    if not voice_client.is_connected():
        await interaction.followup.send("❌ Bot đã mất kết nối voice! Hãy dùng lệnh `/join` lại.")
        return

    # Gửi thông báo đang tìm kiếm
    search_msg = await interaction.followup.send("🔍 **Đang tìm kiếm...**")

    # Tìm kiếm YouTube với cấu hình TỐI ƯU TỐC ĐỘ
    try:
        # CẤU HÌNH TỐI ƯU CHO TỐC ĐỘ - GIẢM CHẤT LƯỢNG ĐỂ TẢI NHANH
        ydl_options = {
            "format": "bestaudio[abr<=64]/bestaudio",  # GIẢM XUỐNG 64kbps để tải nhanh
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "extractaudio": True,  # Chỉ lấy audio
            "audioformat": "mp3",
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "logtostderr": False,
            "no_call_home": True,
            "nooverwrites": True,
            "nopart": True,
            "skip_download": True,
            "source_address": "0.0.0.0",
            "extract_flat": False,
            "forcejson": True,
            "http_chunk_size": 1048576,  # Tăng chunk size
        }

        print(f"[PLAY] Đang tìm kiếm: {song_query}")
        
        # Xử lý query
        if song_query.startswith(('http://', 'https://', 'www.')):
            query = song_query
        else:
            query = f"ytsearch1:{song_query}"

        # Tìm kiếm với timeout
        try:
            results = await asyncio.wait_for(
                search_ytdlp_async(query, ydl_options), 
                timeout=15.0  # Timeout sau 15 giây
            )
        except asyncio.TimeoutError:
            await search_msg.edit(content="❌ **Tìm kiếm timeout!** Vui lòng thử lại.")
            return
        
        # Xử lý kết quả tìm kiếm
        if 'entries' in results:
            tracks = results['entries']
            if not tracks or tracks[0] is None:
                await search_msg.edit(content="❌ **Không tìm thấy kết quả!**")
                return
            first_track = tracks[0]
        else:
            first_track = results

        # Lấy thông tin bài hát
        audio_url = first_track.get('url')
        title = first_track.get('title', 'Không rõ tiêu đề')
        duration = first_track.get('duration', 'Không rõ')
        thumbnail = first_track.get('thumbnail', '')

        if not audio_url:
            await search_msg.edit(content="❌ **Không thể lấy URL audio!**")
            return

        print(f"[PLAY] Đã tìm thấy: {title}")
        print(f"[PLAY] Audio URL: {audio_url[:100]}...")

        # Thêm vào queue
        guild_id = str(interaction.guild_id)
        if guild_id not in SONG_QUEUES:
            SONG_QUEUES[guild_id] = deque()

        SONG_QUEUES[guild_id].append({
            'url': audio_url,
            'title': title,
            'duration': duration,
            'thumbnail': thumbnail
        })
        
        # Phát nhạc hoặc thêm vào queue
        if voice_client.is_playing() or voice_client.is_paused():
            embed = discord.Embed(
                title="🎵 Đã thêm vào queue",
                description=f"**{title}**",
                color=discord.Color.blue()
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            await search_msg.edit(content="", embed=embed)
        else:
            embed = discord.Embed(
                title="🎵 Đang phát",
                description=f"**{title}**",
                color=discord.Color.green()
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            await search_msg.edit(content="", embed=embed)
            await asyncio.sleep(0.5)
            await play_next_song(voice_client, guild_id, interaction.channel)

    except asyncio.TimeoutError:
        await search_msg.edit(content="❌ **Tìm kiếm quá lâu!** Vui lòng thử lại với từ khóa khác.")
    except Exception as e:
        print(f"[PLAY] Lỗi tìm kiếm/play: {e}")
        import traceback
        traceback.print_exc()
        await search_msg.edit(content=f"❌ **Có lỗi xảy ra:** {str(e)[:100]}...")


async def play_next_song(voice_client, guild_id, channel):
    """Phát bài hát tiếp theo trong queue"""
    try:
        print(f"[PLAY_NEXT] Đang chuẩn bị phát bài tiếp theo cho guild {guild_id}")
        
        # Kiểm tra kết nối
        if not voice_client or not voice_client.is_connected():
            print("[PLAY_NEXT] ❌ Không có kết nối voice")
            return

        if not SONG_QUEUES.get(guild_id) or not SONG_QUEUES[guild_id]:
            print("[PLAY_NEXT] ❌ Queue trống")
            # Không còn bài hát trong queue
            if voice_client.is_connected():
                await voice_client.disconnect()
            return

        # Lấy bài hát tiếp theo
        song_data = SONG_QUEUES[guild_id].popleft()
        audio_url = song_data['url']
        title = song_data['title']
        
        print(f"[PLAY_NEXT] Đang phát: {title}")

        # FFmpeg options TỐI ƯU TỐC ĐỘ
        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2",
            "options": "-vn"
        }

        try:
            # Tạo audio source với timeout
            source = discord.FFmpegOpusAudio(audio_url, executable=FFMPEG_PATH, **ffmpeg_options)
            print("[PLAY_NEXT] ✅ Đã tạo audio source")
        except asyncio.TimeoutError:
            print("[PLAY_NEXT] ❌ Timeout tạo audio source")
            await channel.send(f"❌ **Lỗi phát nhạc:** {title} (timeout)")
            await play_next_song(voice_client, guild_id, channel)
            return
        except Exception as e:
            print(f"[PLAY_NEXT] ❌ Lỗi tạo audio source: {e}")
            # Thử lại với options đơn giản hơn
            try:
                simple_ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2',
                    'options': '-vn -c:a libopus -b:a 64k'
                }
                source = discord.FFmpegOpusAudio(audio_url, **simple_ffmpeg_options)
                print("[PLAY_NEXT] ✅ Đã tạo audio source (lần 2)")
            except Exception as e2:
                print(f"[PLAY_NEXT] ❌ Lỗi tạo audio source lần 2: {e2}")
                await channel.send(f"❌ **Lỗi phát nhạc:** {title}")
                await play_next_song(voice_client, guild_id, channel)
                return

        def after_play(error):
            print(f"[AFTER_PLAY] Callback, error: {error}")
            if error:
                print(f"[AFTER_PLAY] ❌ Lỗi phát nhạc: {error}")

            loop = bot.loop
            if loop.is_closed():
                return

            coro = handle_after_play(voice_client, guild_id, channel, error)
            loop.create_task(coro)

        # Kiểm tra lại kết nối trước khi phát
        if voice_client.is_connected():
            voice_client.play(source, after=after_play)
            print("[PLAY_NEXT] ✅ Đã bắt đầu phát nhạc")
            
            # Gửi thông báo đang phát
            embed = discord.Embed(
                title="🎵 Đang phát",
                description=f"**{title}**",
                color=discord.Color.green()
            )
            await channel.send(embed=embed)
        else:
            print("[PLAY_NEXT] ❌ Mất kết nối khi chuẩn bị phát nhạc")
                
    except Exception as e:
        print(f"[PLAY_NEXT] ❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


async def handle_after_play(voice_client, guild_id, channel, error):
    """Xử lý sau khi phát nhạc xong"""
    try:
        print(f"[HANDLE_AFTER] Bắt đầu xử lý, error: {error}")
        
        # Đợi một chút
        await asyncio.sleep(1.0)
        
        # Kiểm tra kết nối trước khi phát bài tiếp theo
        if voice_client and voice_client.is_connected():
            print("[HANDLE_AFTER] Đang phát bài tiếp theo...")
            await play_next_song(voice_client, guild_id, channel)
        else:
            print("[HANDLE_AFTER] ❌ Không có kết nối voice")
            
    except Exception as e:
        print(f"[HANDLE_AFTER] ❌ Lỗi: {e}")


# Event để theo dõi voice state
@bot.event
async def on_voice_state_update(member, before, after):
    """Log voice state changes for debugging"""
    if member.id == bot.user.id:
        print(f"[VOICE_STATE] Bot voice state changed:")
        print(f"  Before: {before.channel.name if before.channel else 'None'}")
        print(f"  After: {after.channel.name if after.channel else 'None'}")
        
        # Nếu bot bị kick khỏi channel, xóa queue
        if before.channel and not after.channel:
            guild_id = str(before.channel.guild.id)
            if guild_id in SONG_QUEUES:
                SONG_QUEUES[guild_id].clear()
                print(f"[VOICE_STATE] Đã xóa queue cho guild {guild_id}")

@bot.tree.command(name="addbox", description="(Admin) Thêm Mystery Box cho user")
async def addbox(interaction: discord.Interaction, user: discord.User, amount: int):
    if not is_user_allowed(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)

    new_box = add_box(user.id, amount)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="✅ Đã Thêm Box",
            description=f"Thêm {amount} box cho {user.mention}\n📦 Tổng: {new_box}",
            color=discord.Color.green()
        )
    )
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/addbox", guild_name, "Slash Command")
    await send_dm_notification(user, "/addbox", guild_name, "Slash Command")


@bot.tree.command(name="removebox", description="(Admin) Trừ Mystery Box của user")
async def removebox(interaction: discord.Interaction, user: discord.User, amount: int):
    if not is_user_allowed(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)

    new_box = remove_box(user.id, amount)
    if new_box is None:
        return await interaction.response.send_message("❌ User không đủ box!", ephemeral=True)

    await interaction.response.send_message(
        embed=discord.Embed(
            title="⚠️ Đã Trừ Box",
            description=f"Trừ {amount} box của {user.mention}\n📦 Còn lại: {new_box}",
            color=discord.Color.orange()
        )
    )
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/removebox", guild_name, "Slash Command")
    await send_dm_notification(user, "/removebox", guild_name, "Slash Command")

# ==================== SHOP MANAGEMENT COMMANDS ====================

class ShopDropdown(discord.ui.Select):
    def __init__(self, shop_items):
        options = []
        for key, item in shop_items.items():
            options.append(discord.SelectOption(
                label=f"{item['name']} - {item['price']} coins",
                value=key,
                description=f"Role ID: {item['role_id']}"
            ))
        
        super().__init__(placeholder="🛒 Chọn item để quản lý...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_key = self.values[0]
        item = shop_data[selected_key]
        
        role = interaction.guild.get_role(item["role_id"])
        
        embed = discord.Embed(
            title=f"🛒 Thông tin item: {item['name']}",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Giá", value=f"{item['price']} <:lonelycoin:1421380256148750429>", inline=True)
        embed.add_field(name="👤 Role", value=role.mention if role else "Không tìm thấy", inline=True)
        embed.add_field(name="🆔 Role ID", value=item["role_id"], inline=True)
        embed.add_field(name="📝 Mô tả", value=item.get("description", "Không có mô tả"), inline=False)
        
        await interaction.response.send_message(
            embed=embed, 
            view=ShopActionView(selected_key), 
            ephemeral=True
        )

class ShopDropdownView(discord.ui.View):
    def __init__(self, shop_items):
        super().__init__(timeout=120)
        self.add_item(ShopDropdown(shop_items))

class ShopActionView(discord.ui.View):
    def __init__(self, item_key):
        super().__init__(timeout=120)
        self.item_key = item_key

    @discord.ui.button(label="✏️ Chỉnh sửa", style=discord.ButtonStyle.blurple)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditShopModal(self.item_key))

    @discord.ui.button(label="🗑️ Xóa", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_user_allowed(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
            return
        
        if self.item_key in shop_data:
            del shop_data[self.item_key]
            save_json(SHOP_FILE, shop_data)
            
            embed = discord.Embed(
                title="✅ Đã xóa item",
                description=f"Đã xóa item **{self.item_key}** khỏi shop",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Item không tồn tại!", ephemeral=True)

class EditShopModal(discord.ui.Modal, title="Chỉnh sửa Item Shop"):
    new_name = discord.ui.TextInput(label="Tên hiển thị", placeholder="Tên item (có thể chứa emoji)", required=True)
    new_price = discord.ui.TextInput(label="Giá", placeholder="Giá tiền (số nguyên)", required=True)
    new_description = discord.ui.TextInput(label="Mô tả", placeholder="Mô tả item", required=False, style=discord.TextStyle.paragraph)

    def __init__(self, item_key):
        super().__init__()
        self.item_key = item_key
        # Pre-fill current values
        if item_key in shop_data:
            item = shop_data[item_key]
            self.new_name.default = item["name"]
            self.new_price.default = str(item["price"])
            self.new_description.default = item.get("description", "")

    async def on_submit(self, interaction: discord.Interaction):
        if not is_user_allowed(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
            return

        if self.item_key not in shop_data:
            await interaction.response.send_message("❌ Item không tồn tại!", ephemeral=True)
            return

        try:
            price = int(self.new_price.value)
            if price < 0:
                await interaction.response.send_message("❌ Giá phải là số dương!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("❌ Giá phải là số hợp lệ!", ephemeral=True)
            return

        # Cập nhật thông tin
        shop_data[self.item_key]["name"] = str(self.new_name.value)
        shop_data[self.item_key]["price"] = price
        shop_data[self.item_key]["description"] = str(self.new_description.value) if self.new_description.value else "No description"
        
        save_json(SHOP_FILE, shop_data)

        embed = discord.Embed(
            title="✅ Đã cập nhật item",
            description=f"Đã cập nhật item **{self.item_key}**",
            color=discord.Color.green()
        )
        embed.add_field(name="🆕 Tên mới", value=self.new_name.value, inline=True)
        embed.add_field(name="💰 Giá mới", value=f"{price} <:lonelycoin:1421380256148750429>", inline=True)
        if self.new_description.value:
            embed.add_field(name="📝 Mô tả mới", value=self.new_description.value, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="shop-add", description="(Admin) Thêm item mới vào shop")
@app_commands.describe(
    name="Tên hiển thị của item (có thể chứa emoji)",
    role="Role sẽ được cấp khi mua item",
    price="Giá của item",
    description="Mô tả của item (tùy chọn)"
)
async def shop_add(interaction: discord.Interaction, name: str, role: discord.Role, price: int, description: str = None):
    """Thêm item mới vào shop"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Kiểm tra xem role đã tồn tại trong shop chưa
    for existing_key, existing_item in shop_data.items():
        if existing_item["role_id"] == role.id:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Role {role.mention} đã tồn tại trong shop với tên **{existing_item['name']}**!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # Tạo key mới (dựa trên tên role, chuyển thành chữ thường và thay thế khoảng trắng)
    new_key = role.name.lower().replace(" ", "_")
    
    # Đảm bảo key là duy nhất
    counter = 1
    original_key = new_key
    while new_key in shop_data:
        new_key = f"{original_key}_{counter}"
        counter += 1

    # Thêm item mới
    shop_data[new_key] = {
        "name": name,
        "role_id": role.id,
        "price": price,
        "description": description or "No description available"
    }
    
    save_json(SHOP_FILE, shop_data)

    embed = discord.Embed(
        title="✅ Đã thêm item vào shop",
        description=f"Đã thêm item mới vào shop với key: `{new_key}`",
        color=discord.Color.green()
    )
    embed.add_field(name="🆔 Key", value=new_key, inline=True)
    embed.add_field(name="🏷️ Tên", value=name, inline=True)
    embed.add_field(name="👤 Role", value=role.mention, inline=True)
    embed.add_field(name="💰 Giá", value=f"{price} <:lonelycoin:1421380256148750429>", inline=True)
    embed.add_field(name="📝 Mô tả", value=description or "Không có mô tả", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/shop-add name:{name} role:{role.id} price:{price}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/shop-add name:{name} role:{role.id} price:{price}", guild_name, "Slash Command")

@bot.tree.command(name="shop-edit", description="(Admin) Chỉnh sửa items trong shop")
async def shop_edit(interaction: discord.Interaction):
    """Hiển thị danh sách items trong shop để chỉnh sửa"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not shop_data:
        embed = discord.Embed(
            title="🛒 Quản lý Shop",
            description="Hiện chưa có item nào trong shop.\nSử dụng `/shop-add` để thêm item mới.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🛒 Quản lý Shop",
        description="Chọn một item trong dropdown bên dưới để chỉnh sửa hoặc xóa.",
        color=discord.Color.blue()
    )
    embed.add_field(name="📊 Tổng số items", value=len(shop_data), inline=True)
    
    await interaction.response.send_message(
        embed=embed, 
        view=ShopDropdownView(shop_data), 
        ephemeral=True
    )
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/shop-edit", guild_name, "Slash Command")
    await send_dm_notification(user, "/shop-edit", guild_name, "Slash Command")

@bot.tree.command(name="shop-remove", description="(Admin) Xóa item khỏi shop")
@app_commands.describe(
    role="Role của item cần xóa"
)
async def shop_remove(interaction: discord.Interaction, role: discord.Role):
    """Xóa item khỏi shop dựa trên role"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Tìm item có role_id trùng
    item_to_remove = None
    item_name = None
    
    for item_key, item_data in shop_data.items():
        if item_data["role_id"] == role.id:
            item_to_remove = item_key
            item_name = item_data["name"]
            break
    
    if not item_to_remove:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Không tìm thấy item nào với role {role.mention} trong shop!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Xóa item
    del shop_data[item_to_remove]
    save_json(SHOP_FILE, shop_data)
    
    embed = discord.Embed(
        title="✅ Đã xóa item khỏi shop",
        description=f"Đã xóa item **{item_name}** (key: `{item_to_remove}`) với role {role.mention}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/shop-remove role:{role.id}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/shop-remove role:{role.id}", guild_name, "Slash Command")
    
@bot.tree.command(name="setbox", description="(Admin) Set số Mystery Box cho user")
async def setbox(interaction: discord.Interaction, user: discord.User, amount: int):
    if not is_user_allowed(interaction.user.id):
        return await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)

    new_box = set_box(user.id, amount)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🔧 Đặt Box",
            description=f"Số Mystery Box của {user.mention} = {new_box}",
            color=discord.Color.blue()
        )
    )
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/setbox", guild_name, "Slash Command")
    await send_dm_notification(user, "/setbox", guild_name, "Slash Command")
    
# -------------------
# Ticket Button + View (tạo channel)
# -------------------
class TicketButton(discord.ui.Button):
    def __init__(self, setup):
        super().__init__(label=setup["label"], style=discord.ButtonStyle.green)
        self.setup = setup

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        cat_id = self.setup.get("category_id")
        category = guild.get_channel(cat_id) if cat_id else None

        if category is None or not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message(
                embed=discord.Embed(title="❌ Category không hợp lệ", description="Vui lòng kiểm tra category trong setup.", color=discord.Color.red()),
                ephemeral=True
            )

        safe_name = interaction.user.name.strip().replace(" ", "-")[:90]
        channel_name = f"ticket-{safe_name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        try:
            channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )
        except Exception as e:
            return await interaction.response.send_message(
                embed=discord.Embed(title="❌ Không thể tạo kênh", description=str(e), color=discord.Color.red()),
                ephemeral=True
            )

        add_ticket(channel.id, interaction.user.id)

        ticket_embed = discord.Embed(
            title="🎫 Ticket Mới",
            description=f"Xin chào {interaction.user.mention}, staff sẽ sớm hỗ trợ bạn.\nVui lòng mô tả vấn đề của bạn ở đây.",
            color=discord.Color.green()
        )
        await channel.send(embed=ticket_embed)

        role_pings = []
        for rid in self.setup.get("roles", []):
            r = guild.get_role(rid)
            if r:
                role_pings.append(r.mention)
        if role_pings:
            await channel.send(" ".join(role_pings))

        await channel.send("🔒 Nhấn nút dưới để đóng ticket:", view=CloseTicketView())

        await interaction.response.send_message(
            embed=discord.Embed(title="✅ Ticket đã được tạo", description=f"Ticket: {channel.mention}", color=discord.Color.green()),
            ephemeral=True
        )

        if LOG_CHANNEL_ID:
            lc = guild.get_channel(LOG_CHANNEL_ID)
            if lc:
                log_embed = discord.Embed(
                    title="🎫 Ticket Được Tạo",
                    description=f"Người tạo: {interaction.user.mention}\nLoại: **{self.setup['label']}**\nKênh: {channel.mention}",
                    color=discord.Color.green()
                )
                await lc.send(embed=log_embed)

class TicketView(discord.ui.View):
    def __init__(self, setups: List[dict]):
        super().__init__(timeout=None)
        for s in setups:
            self.add_item(TicketButton(s))
            
# -------------------
# Background check (mute if ticket inactive 6h)
# -------------------
@tasks.loop(minutes=5)
async def check_tickets():
    data = load_ticket_json(TICKET_DATA, {})
    now = datetime.datetime.utcnow()

    for channel_id, info in list(data.items()):
        try:
            created = datetime.datetime.fromisoformat(info["created_at"])
        except Exception:
            continue
        user_id = info["user_id"]
        active = info.get("active", False)

        if not active and (now - created).total_seconds() > 6 * 3600:
            for guild in bot.guilds:
                member = guild.get_member(int(user_id))
                if member:
                    try:
                        until = discord.utils.utcnow() + datetime.timedelta(days=1)
                        await member.timeout(until, reason="Spam ticket không có lý do")
                        if LOG_CHANNEL_ID:
                            log_channel = guild.get_channel(LOG_CHANNEL_ID)
                            if log_channel:
                                await log_channel.send(embed=discord.Embed(
                                    title="⚠️ Cảnh cáo",
                                    description=f"{member.mention} đã bị mute 1 ngày vì tạo ticket không có lý do!",
                                    color=discord.Color.red()
                                ))
                    except Exception as e:
                        print(f"Lỗi mute: {e}")
            del data[channel_id]
    save_ticket_json(TICKET_DATA, data)
    
# -------------------
# Dropdown + action views for /setup-list
# -------------------
class SetupDropdown(discord.ui.Select):
    def __init__(self, setups):
        options = []
        for s in setups:
            label = s.get("label", "No label")
            enabled = s.get("enabled", False)
            display = f"{label} ({'✅' if enabled else '❌'})"
            options.append(discord.SelectOption(label=display, value=s["id"]))
        super().__init__(placeholder="Chọn setup...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
        sid = self.values[0]
        setup = next((x for x in cfg["setups"] if x["id"] == sid), None)
        if not setup:
            return await interaction.response.send_message("❌ Setup không tồn tại.", ephemeral=True)

        roles_text = ', '.join([f'<@&{r}>' for r in setup.get("roles", [])]) if setup.get("roles") else "Không có"
        category_mention = f"<#{setup['category_id']}>" if setup.get("category_id") else "Không có"

        embed = discord.Embed(
            title=f"⚙️ Setup: {setup['label']}",
            description=f"**Roles:** {roles_text}\n**Category:** {category_mention}\n**Trạng thái:** {'✅ Enabled' if setup.get('enabled') else '❌ Disabled'}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=SetupActionView(setup["id"]), ephemeral=True)


class SetupDropdownView(discord.ui.View):
    def __init__(self, setups):
        super().__init__(timeout=120)
        self.add_item(SetupDropdown(setups))


class SetupActionView(discord.ui.View):
    def __init__(self, setup_id):
        super().__init__(timeout=120)
        self.setup_id = setup_id

    @discord.ui.button(label="✅ Enable", style=discord.ButtonStyle.green)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Chỉ admin.", ephemeral=True)
        cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
        found = False
        for s in cfg["setups"]:
            if s["id"] == self.setup_id:
                s["enabled"] = True
                found = True
            else:
                s["enabled"] = False
        if not found:
            return await interaction.response.send_message("❌ Setup không tồn tại.", ephemeral=True)
        save_ticket_json(CONFIG_FILE, cfg)
        await interaction.response.send_message("✅ Setup đã được bật (và tắt các setup khác).", ephemeral=True)

    @discord.ui.button(label="📝 Edit", style=discord.ButtonStyle.blurple)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Chỉ admin.", ephemeral=True)
        await interaction.response.send_modal(EditSetupModal(self.setup_id))

    @discord.ui.button(label="❌ Delete", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Chỉ admin.", ephemeral=True)
        cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
        cfg["setups"] = [s for s in cfg.get("setups", []) if s["id"] != self.setup_id]
        save_ticket_json(CONFIG_FILE, cfg)
        await interaction.response.send_message("🗑️ Setup đã bị xoá.", ephemeral=True)
        
# -------------------
# Modal để edit setup
# -------------------
class EditSetupModal(discord.ui.Modal, title="Chỉnh sửa Setup"):
    new_label = discord.ui.TextInput(label="Label", placeholder="Tên nút", required=True, max_length=100)
    new_roles = discord.ui.TextInput(label="Roles", placeholder="@role1 @role2 hoặc 111 222", required=False)
    new_category = discord.ui.TextInput(label="Category ID", placeholder="ID category", required=False)

    def __init__(self, setup_id):
        super().__init__()
        self.setup_id = setup_id

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ Chỉ admin.", ephemeral=True)

        cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
        setup = next((s for s in cfg["setups"] if s["id"] == self.setup_id), None)
        if not setup:
            return await interaction.response.send_message("❌ Setup không tồn tại.", ephemeral=True)

        setup["label"] = str(self.new_label.value).strip()
        setup["roles"] = parse_role_string(self.new_roles.value)
        try:
            if self.new_category.value:
                setup["category_id"] = int(self.new_category.value)
        except:
            setup["category_id"] = None

        save_ticket_json(CONFIG_FILE, cfg)
        await interaction.response.send_message("✅ Setup đã được chỉnh sửa.", ephemeral=True)
        
# -------------------
# /setup command (admin)
# -------------------
@bot.tree.command(name="setup", description="Tạo 1 setup button ticket (admin)")
@app_commands.describe(
    label="Tên nút (ví dụ: Hỗ Trợ)",
    roles="Danh sách role để ping (ví dụ: @Support @Mod hoặc 111111111111 2222222222)",
    category="Category chứa ticket"
)
async def setup_cmd(interaction: discord.Interaction, label: str, roles: str, category: discord.CategoryChannel):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
    rid_list = parse_role_string(roles)
    setup_id = str(uuid.uuid4())[:8]

    new_setup = {
        "id": setup_id,
        "label": label,
        "roles": rid_list,
        "category_id": category.id if category else None,
        "enabled": False
    }
    cfg.setdefault("setups", []).append(new_setup)
    save_ticket_json(CONFIG_FILE, cfg)

    await interaction.response.send_message(embed=discord.Embed(
        title="✅ Setup đã được tạo",
        description=f"ID: `{setup_id}`\nLabel: **{label}**\nRoles: {' '.join([f'<@&{r}>' for r in rid_list]) if rid_list else 'Không có'}\nCategory: {category.mention}",
        color=discord.Color.green()
    ), ephemeral=True)

    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/setup", guild_name, "Slash Command")
    await send_dm_notification(user, "/setup", guild_name, "Slash Command")
    
# -------------------
# /taoticket command
# -------------------
@bot.tree.command(name="ticket", description="Gửi menu ticket đã setup (chỉ hiện setup enabled)")
async def taoticket(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
    setups = [s for s in cfg.get("setups", []) if s.get("enabled")]
    if not setups:
        return await interaction.response.send_message(embed=discord.Embed(title="❌ Không có setup enabled", description="Bạn cần bật 1 setup bằng /setup-list", color=discord.Color.red()), ephemeral=True)

    embed = discord.Embed(title="🎫 Menu Ticket", description="Nhấn nút bên dưới để tạo ticket.", color=discord.Color.blurple())
    await interaction.channel.send(embed=embed, view=TicketView(setups))
    await interaction.response.send_message(embed=discord.Embed(title="✅ Menu ticket đã gửi", color=discord.Color.green()), ephemeral=True)

    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/ticket", guild_name, "Slash Command")
    await send_dm_notification(user, "/ticket", guild_name, "Slash Command")
    
# -------------------
# /setup-list command
# -------------------
@bot.tree.command(name="setup-list", description="Hiện danh sách setup ticket")
async def setup_list(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    cfg = load_ticket_json(CONFIG_FILE, {"setups": []})
    setups = cfg.get("setups", [])
    if not setups:
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="📋 Danh sách Setup",
                description="Hiện chưa có setup nào.\nDùng `/setup` để thêm mới.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    embed = discord.Embed(
        title="📋 Danh sách Setup",
        description="Chọn một setup trong dropdown bên dưới để quản lý.",
        color=discord.Color.blurple()
    )
    view = SetupDropdownView(setups)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/setup-list", guild_name, "Slash Command")
    await send_dm_notification(user, "/setup-list", guild_name, "Slash Command")
    
class ConfirmView(discord.ui.View):
    def __init__(self, member: discord.Member, tag_name: str, role_id: int):
        super().__init__()
        self.member = member
        self.tag_name = tag_name
        self.role_id = role_id

    @discord.ui.button(label="Có", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(self.member.guild.roles, id=self.role_id)
        if role and role in self.member.roles:
            # Lấy emoji của tag - CHỈ LẤY EMOJI, KHÔNG UNPACK
            emoji = extract_name_and_emoji_from_tag(self.tag_name)
            emoji_display = ""
            
            if emoji:
                if isinstance(emoji, discord.PartialEmoji):
                    emoji_display = str(emoji) + " "  # Custom emoji
                else:
                    emoji_display = emoji + " "  # Unicode emoji
            
            # Lấy nickname hiện tại (loại bỏ tag cũ nếu có)
            current_nick = self.member.display_name
            
            # Xóa tất cả tag cũ từ tag_data
            tag_data = load_json(TAG_FILE)
            for old_tag in tag_data.keys():
                old_emoji = extract_name_and_emoji_from_tag(old_tag)  # CHỈ LẤY EMOJI
                old_emoji_display = ""
                
                if old_emoji:
                    if isinstance(old_emoji, discord.PartialEmoji):
                        old_emoji_display = str(old_emoji) + " "
                    else:
                        old_emoji_display = old_emoji + " "
                
                # Xóa cả phần có emoji và không có emoji
                old_prefix_with_emoji = f"{old_emoji_display}[{old_tag}]"
                old_prefix_without_emoji = f"[{old_tag}]"
                
                if current_nick.startswith(old_prefix_with_emoji):
                    current_nick = current_nick.replace(old_prefix_with_emoji, "").strip()
                    break
                elif current_nick.startswith(old_prefix_without_emoji):
                    current_nick = current_nick.replace(old_prefix_without_emoji, "").strip()
                    break
            
            # Tạo nickname mới với tag và emoji
            new_nick = f"{emoji_display}[{self.tag_name}] {current_nick}"
            
            try:
                # Giới hạn độ dài nickname (Discord limit: 32 characters)
                if len(new_nick) > 32:
                    # Cắt bớt tên gốc để vừa với tag
                    max_original_len = 32 - len(f"{emoji_display}[{self.tag_name}] ") - 3  # -3 cho "..."
                    original_name = current_nick[:max_original_len] + "..."
                    new_nick = f"{emoji_display}[{self.tag_name}] {original_name}"
                
                await self.member.edit(nick=new_nick)
                await interaction.response.send_message(
                    f"✅ Đổi nickname thành **{new_nick}**",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ Bot không có quyền đổi nickname (có thể là owner hoặc role cao hơn bot)", 
                    ephemeral=True
                )
        else:
            await interaction.response.send_message("❌ Bạn không có role này!", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Hủy chọn", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Hủy chọn", ephemeral=True)
        self.stop()
        
class RoleSelect(discord.ui.Select):
    def __init__(self, member: discord.Member):
        self.member = member
        options = []

        # Load tag data từ file tag.json
        tag_data = load_json(TAG_FILE)
        if not tag_data:
            options.append(discord.SelectOption(
                label="Lỗi tải tag",
                value="error",
                description="Không thể tải dữ liệu tag"
            ))
        else:
            # Chỉ thêm tag mà member đang có role
            for tag_name, tag_info in tag_data.items():
                # Lấy role_id từ cả format cũ và mới
                role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
                role = discord.utils.get(member.guild.roles, id=role_id)
                
                if role and role in member.roles:
                    # CHỈ LẤY EMOJI (dùng hàm mới hoặc hàm đã sửa)
                    emoji = get_tag_emoji_for_dropdown(tag_name)
                    
                    option = discord.SelectOption(
                        label=tag_name,
                        value=tag_name,
                        description=f"Chọn {tag_name}",
                        emoji=emoji  # THÊM EMOJI VÀO DROPDOWN
                    )
                    
                    options.append(option)

        super().__init__(placeholder="Chọn tag...", min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        
        # Load lại tag data để lấy role_id
        tag_data = load_json(TAG_FILE)
        tag_info = tag_data.get(selected_tag)
        
        if not tag_info:
            await interaction.response.send_message("❌ Không tìm thấy tag!", ephemeral=True)
            return
        
        # Lấy role_id từ cả format cũ và mới
        role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
        
        if not role_id:
            await interaction.response.send_message("❌ Không tìm thấy role cho tag này!", ephemeral=True)
            return

        # Lấy emoji để hiển thị
        emoji = extract_name_and_emoji_from_tag(selected_tag)
        emoji_display = ""
        
        if emoji:
            if isinstance(emoji, discord.PartialEmoji):
                emoji_display = str(emoji) + " "
            else:
                emoji_display = emoji + " "

        embed = discord.Embed(
            title="Xác nhận",
            description=f"Bạn có muốn chọn tag {emoji_display}**{selected_tag}** không?",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=ConfirmView(self.member, selected_tag, role_id), ephemeral=True)
        
class RoleView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.add_item(RoleSelect(member))
        
@bot.tree.command(name="tag", description="Chọn tag để đổi nickname")
async def tag(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    guild = bot.get_guild(TARGET_GUILD_ID)
    member = guild.get_member(interaction.user.id)

    if not member:
        await interaction.response.send_message("❌ Không tìm thấy thành viên!", ephemeral=True)
        return

    # Load tag data từ file
    tag_data = load_json(TAG_FILE)
    if not tag_data:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không thể tải dữ liệu tag!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Kiểm tra xem user có bất kỳ role nào trong tag_data không
    has_any_role = False
    for role_id in tag_data.values():
        role = guild.get_role(role_id)
        if role and role in member.roles:
            has_any_role = True
            break
    
    if not has_any_role:
        embed = discord.Embed(
            title="❌ Không có tag",
            description="Bạn không có bất kỳ tag nào để chọn!\nHãy mua role trong shop để có tag.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="Chọn tag",
        description="Sử dụng dropdown bên dưới để chọn tag mà bạn có.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, view=RoleView(member), ephemeral=True)
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/tag", guild_name, "Slash Command")
    await send_dm_notification(user, "/tag", guild_name, "Slash Command")
    
@bot.tree.command(name="reset-tag", description="Xóa tag prefix khỏi nickname của bạn")
async def resettag(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    guild = bot.get_guild(TARGET_GUILD_ID)
    member = guild.get_member(interaction.user.id)

    if not member:
        await interaction.response.send_message("❌ Không tìm thấy thành viên!", ephemeral=True)
        return

    # Load tag data từ file
    tag_data = load_json(TAG_FILE)
    if not tag_data:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không thể tải dữ liệu tag!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # 🔹 Xoá tất cả tag và emoji từ nickname
    current_nick = member.display_name
    original_name = current_nick
    
    for tag_name in tag_data.keys():
        # Lấy emoji của tag
        emoji, _ = extract_name_and_emoji_from_tag(tag_name)
        emoji_display = ""
        
        if emoji:
            if isinstance(emoji, discord.PartialEmoji):
                emoji_display = str(emoji) + " "
            else:
                emoji_display = emoji + " "
        
        # Xóa cả phần có emoji và không có emoji
        prefix_with_emoji = f"{emoji_display}[{tag_name}]"
        prefix_without_emoji = f"[{tag_name}]"
        
        if current_nick.startswith(prefix_with_emoji):
            original_name = current_nick.replace(prefix_with_emoji, "").strip()
            break
        elif current_nick.startswith(prefix_without_emoji):
            original_name = current_nick.replace(prefix_without_emoji, "").strip()
            break

    # Nếu không thay đổi, có nghĩa là không có tag
    if original_name == current_nick:
        embed = discord.Embed(
            title="ℹ️ Thông báo",
            description="Nickname của bạn không có tag nào để xóa!",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Log
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, "/reset-tag", guild_name, "Slash Command")
        await send_dm_notification(user, "/reset-tag", guild_name, "Slash Command")
        return

    try:
        await member.edit(nick=original_name)
        embed = discord.Embed(
            title="✅ Đã xóa tag",
            description=f"Nickname của bạn đã được reset về:\n**{original_name}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Lỗi quyền",
            description="Bot không có quyền đổi nickname của bạn!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/reset-tag", guild_name, "Slash Command")
    await send_dm_notification(user, "/reset-tag", guild_name, "Slash Command")
    
class TagDropdown(discord.ui.Select):
    def __init__(self, tags):
        options = []
        for tag_name, tag_info in tags.items():
            # Lấy role_id từ cả format cũ và mới
            role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
            
            # Lấy emoji để hiển thị
            emoji = extract_name_and_emoji_from_tag(tag_name)
            
            label = tag_name
            if emoji:
                if isinstance(emoji, discord.PartialEmoji):
                    label = f"{emoji} {tag_name}"
                else:
                    label = f"{emoji} {tag_name}"
            
            options.append(discord.SelectOption(
                label=label[:25],  # Giới hạn độ dài
                value=tag_name,
                description=f"Role ID: {role_id}"
            ))
        
        super().__init__(placeholder="Chọn tag để quản lý...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        tag_data = load_json(TAG_FILE)
        tag_info = tag_data[selected_tag]
        
        # Lấy role_id từ cả format cũ và mới
        role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
        role = interaction.guild.get_role(role_id)
        
        # Lấy emoji để hiển thị
        emoji = extract_name_and_emoji_from_tag(selected_tag)
        emoji_display = str(emoji) if emoji else "Không có"
        
        embed = discord.Embed(
            title=f"🏷️ Thông tin tag: {selected_tag}",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Role", value=role.mention if role else "Không tìm thấy", inline=True)
        embed.add_field(name="🎨 Emoji", value=emoji_display, inline=True)
        embed.add_field(name="🆔 Role ID", value=role_id, inline=True)
        
        await interaction.response.send_message(
            embed=embed, 
            view=TagActionView(selected_tag), 
            ephemeral=True
        )

class TagDropdownView(discord.ui.View):
    def __init__(self, tags):
        super().__init__(timeout=120)
        self.add_item(TagDropdown(tags))

class TagActionView(discord.ui.View):
    def __init__(self, tag_name):
        super().__init__(timeout=120)
        self.tag_name = tag_name

    @discord.ui.button(label="✏️ Chỉnh sửa", style=discord.ButtonStyle.blurple)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditTagModal(self.tag_name))

    @discord.ui.button(label="🗑️ Xóa", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_user_allowed(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
            return
        
        tag_data = load_json(TAG_FILE)
        if self.tag_name in tag_data:
            del tag_data[self.tag_name]
            save_json(TAG_FILE, tag_data)
            
            embed = discord.Embed(
                title="✅ Đã xóa tag",
                description=f"Đã xóa tag **{self.tag_name}**",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Tag không tồn tại!", ephemeral=True)

class EditTagModal(discord.ui.Modal, title="Chỉnh sửa Tag"):
    new_name = discord.ui.TextInput(label="Tên tag mới", placeholder="Nhập tên tag mới", required=True)
    new_icon = discord.ui.TextInput(label="Icon mới", placeholder="Emoji unicode hoặc :name:id", required=False)

    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name
        # Pre-fill current values
        tag_data = load_json(TAG_FILE)
        if tag_name in tag_data:
            tag_info = tag_data[tag_name]
            self.new_name.default = tag_name
            
            # Pre-fill icon nếu có
            if isinstance(tag_info, dict) and tag_info.get("icon"):
                icon_data = tag_info["icon"]
                if icon_data["type"] == "custom":
                    self.new_icon.default = f":{icon_data['name']}:{icon_data['id']}"
                else:
                    self.new_icon.default = icon_data["emoji"]

    async def on_submit(self, interaction: discord.Interaction):
        if not is_user_allowed(interaction.user.id):
            await interaction.response.send_message("❌ Bạn không có quyền!", ephemeral=True)
            return

        tag_data = load_json(TAG_FILE)
        if self.tag_name not in tag_data:
            await interaction.response.send_message("❌ Tag không tồn tại!", ephemeral=True)
            return

        new_name = str(self.new_name.value).strip()
        new_icon = str(self.new_icon.value).strip() if self.new_icon.value else None

        # Kiểm tra tên mới không trùng
        if new_name != self.tag_name and new_name in tag_data:
            await interaction.response.send_message("❌ Tên tag đã tồn tại!", ephemeral=True)
            return

        # Lấy dữ liệu tag cũ
        old_tag_info = tag_data[self.tag_name]
        
        # Xử lý icon mới
        icon_data = None
        if new_icon:
            if new_icon.startswith('<:') and new_icon.endswith('>'):
                try:
                    emoji_parts = new_icon[2:-1].split(':')
                    if len(emoji_parts) == 2:
                        emoji_name, emoji_id = emoji_parts
                        icon_data = {"type": "custom", "name": emoji_name, "id": int(emoji_id)}
                except:
                    pass
            elif ':' in new_icon and not new_icon.startswith('<'):
                try:
                    emoji_parts = new_icon.split(':')
                    if len(emoji_parts) == 2:
                        emoji_name, emoji_id = emoji_parts
                        icon_data = {"type": "custom", "name": emoji_name, "id": int(emoji_id)}
                except:
                    pass
            else:
                icon_data = {"type": "unicode", "emoji": new_icon}

        # Tạo dữ liệu tag mới
        if isinstance(old_tag_info, int):
            # Format cũ -> chuyển sang format mới
            new_tag_info = {
                "role_id": old_tag_info,
                "icon": icon_data
            }
        else:
            # Format mới -> giữ nguyên role_id
            new_tag_info = {
                "role_id": old_tag_info.get("role_id"),
                "icon": icon_data
            }

        # Xóa tag cũ và thêm tag mới
        del tag_data[self.tag_name]
        tag_data[new_name] = new_tag_info
        save_json(TAG_FILE, tag_data)

        embed = discord.Embed(
            title="✅ Đã cập nhật tag",
            description=f"Đã cập nhật tag **{self.tag_name}** → **{new_name}**",
            color=discord.Color.green()
        )
        if icon_data:
            embed.add_field(name="🎨 Icon mới", value=new_icon, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="tag-list", description="Xem danh sách tag và quản lý")
async def tag_list(interaction: discord.Interaction):
    """Hiển thị danh sách tag với nút chỉnh sửa"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    tag_data = load_json(TAG_FILE)
    if not tag_data:
        embed = discord.Embed(
            title="🏷️ Danh sách Tag",
            description="Chưa có tag nào trong hệ thống.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🏷️ Danh sách Tag",
        description="Chọn một tag trong dropdown bên dưới để quản lý.",
        color=discord.Color.blue()
    )
    embed.add_field(name="📊 Tổng số tag", value=len(tag_data), inline=True)
    
    await interaction.response.send_message(
        embed=embed, 
        view=TagDropdownView(tag_data), 
        ephemeral=True
    )
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/tag-list", guild_name, "Slash Command")
    await send_dm_notification(user, "/tag-list", guild_name, "Slash Command")
    
# Slash Command - Bancmd: Cấm người dùng sử dụng bot
@bot.tree.command(name="bancmd", description="Cấm người dùng sử dụng bot")
@app_commands.describe(user_id="ID của người dùng cần cấm", reason="Lý do cấm")
async def bancmd(interaction: discord.Interaction, user_id: str, reason: str):
    if not is_user_allowed(interaction.user.id):
        await interaction.response.send_message(
            embed=discord.Embed(title="❌ Lỗi", description="Bạn không có quyền!", color=discord.Color.red()),
            ephemeral=True
        )
        return

    try:
        target_user_id = int(user_id)
        if target_user_id == interaction.user.id:
            await interaction.response.send_message(
                embed=discord.Embed(title="❌ Lỗi", description="Không thể tự cấm chính mình!", color=discord.Color.red()),
                ephemeral=True
            )
            return

        if target_user_id in ALLOWED_USERS:
            await interaction.response.send_message(
                embed=discord.Embed(title="❌ Lỗi", description="Không thể cấm admin khác!", color=discord.Color.red()),
                ephemeral=True
            )
            return

        if is_user_banned(target_user_id):
            await interaction.response.send_message(
                embed=discord.Embed(title="❌ Lỗi", description="User đã bị cấm trước đó!", color=discord.Color.red()),
                ephemeral=True
            )
            return

        # thêm vào danh sách cấm
        current_time = get_utc7_time().strftime("%H:%M:%S %d/%m/%Y")
        BANNED_USERS[target_user_id] = {
            "reason": reason,
            "banned_by": f"{interaction.user}",
            "banned_at": current_time
        }
        save_banned_users()  # 🔥 Lưu lại

        # trả lời ngay
        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Đã cấm",
                description=f"Đã cấm user `{user_id}`.\n**Lý do:** {reason}",
                color=discord.Color.green()
            ),
            ephemeral=True
        )

        # log + dm sau khi đã trả lời
        user = f"{interaction.user}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/bancmd userid:{user_id} reason:{reason}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/bancmd userid:{user_id} reason:{reason}", guild_name, "Slash Command")

    except ValueError:
        await interaction.response.send_message(
            embed=discord.Embed(title="❌ Lỗi", description="User ID không hợp lệ!", color=discord.Color.red()),
            ephemeral=True
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi không xác định",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

class GiveTagView(discord.ui.View):
    def __init__(self, user: discord.Member, tag_data: dict):
        super().__init__(timeout=60)
        self.add_item(GiveTagSelect(user, tag_data))
        
class GiveTagSelect(discord.ui.Select):
    def __init__(self, user: discord.Member, tag_data: dict):
        self.user = user
        self.tag_data = tag_data
        
        options = []
        
        # Thêm tất cả tag có sẵn
        for tag_name, tag_info in tag_data.items():
            # Lấy role_id từ cả format cũ và mới
            role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
            role = discord.utils.get(user.guild.roles, id=role_id)
            
            if role:
                # CHỈ LẤY EMOJI (không unpack)
                emoji = extract_name_and_emoji_from_tag(tag_name)
                
                option = discord.SelectOption(
                    label=tag_name,  # Dùng tên tag làm label
                    value=tag_name,
                    description=f"Give {tag_name} to {user.display_name}"
                )
                
                # Thêm emoji nếu có
                if emoji:
                    option.emoji = emoji
                
                options.append(option)
        
        super().__init__(
            placeholder="🎯 Chọn tag để give...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        tag_info = self.tag_data[selected_tag]
        
        # Lấy role_id từ cả format cũ và mới
        role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
        role = discord.utils.get(self.user.guild.roles, id=role_id)
        
        if not role:
            await interaction.response.send_message("❌ Role không tồn tại!", ephemeral=True)
            return
        
        # Kiểm tra xem user đã có role này chưa
        if role in self.user.roles:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"{self.user.mention} đã có role {role.mention}!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Thêm role cho user
            await self.user.add_roles(role)
            
            # Lấy emoji để hiển thị - CHỈ LẤY EMOJI
            emoji = extract_name_and_emoji_from_tag(selected_tag)
            emoji_display = ""
            
            if emoji:
                if isinstance(emoji, discord.PartialEmoji):
                    emoji_display = str(emoji) + " "
                else:
                    emoji_display = emoji + " "
            
            embed = discord.Embed(
                title="✅ Đã give tag",
                description=f"Đã give tag {emoji_display}**{selected_tag}** cho {self.user.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Lỗi quyền",
                description="Bot không có quyền thêm role cho user này!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoveUserTagSelect(discord.ui.Select):
    def __init__(self, user: discord.Member, tag_data: dict):
        self.user = user
        self.tag_data = tag_data
        
        options = []
        
        # Chỉ thêm tag mà user đang có
        for tag_name, tag_info in tag_data.items():
            # Lấy role_id từ cả format cũ và mới
            role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
            role = discord.utils.get(user.guild.roles, id=role_id)
            
            if role and role in user.roles:
                # CHỈ LẤY EMOJI (không unpack)
                emoji = extract_name_and_emoji_from_tag(tag_name)
                
                option = discord.SelectOption(
                    label=tag_name,  # Dùng tên tag làm label
                    value=tag_name,
                    description=f"Remove {tag_name} from {user.display_name}"
                )
                
                # Thêm emoji nếu có
                if emoji:
                    option.emoji = emoji
                
                options.append(option)
        
        super().__init__(
            placeholder="🎯 Chọn tag để remove...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        tag_info = self.tag_data[selected_tag]
        
        # Lấy role_id từ cả format cũ và mới
        role_id = tag_info if isinstance(tag_info, int) else tag_info.get("role_id")
        role = discord.utils.get(self.user.guild.roles, id=role_id)
        
        if not role:
            await interaction.response.send_message("❌ Role không tồn tại!", ephemeral=True)
            return
        
        # Kiểm tra xem user có role này không
        if role not in self.user.roles:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"{self.user.mention} không có role {role.mention}!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Xóa role khỏi user
            await self.user.remove_roles(role)
            
            # Lấy emoji để hiển thị - CHỈ LẤY EMOJI
            emoji = extract_name_and_emoji_from_tag(selected_tag)
            emoji_display = ""
            
            if emoji:
                if isinstance(emoji, discord.PartialEmoji):
                    emoji_display = str(emoji) + " "
                else:
                    emoji_display = emoji + " "
            
            embed = discord.Embed(
                title="✅ Đã remove tag",
                description=f"Đã remove tag {emoji_display}**{selected_tag}** khỏi {self.user.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Lỗi quyền",
                description="Bot không có quyền xóa role khỏi user này!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
class RemoveUserTagView(discord.ui.View):
    def __init__(self, user: discord.Member, tag_data: dict):
        super().__init__(timeout=60)
        self.add_item(RemoveUserTagSelect(user, tag_data))
        
@bot.tree.command(name="add-tag", description="Thêm tag mới vào hệ thống")
@app_commands.describe(
    role="Role để gắn với tag",
    name="Tên của tag (hiển thị trong dropdown)",
    icon="Emoji unicode hoặc custom emoji (ví dụ: 🐷, :vip:123456789)"
)
async def add_tag(interaction: discord.Interaction, role: discord.Role, name: str, icon: str = None):
    """Thêm tag mới vào file tag.json với icon tùy chọn"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Load tag data hiện tại
    tag_data = load_json(TAG_FILE)
    
    # Kiểm tra xem role đã tồn tại chưa - XỬ LÝ CẢ FORMAT CŨ VÀ MỚI
    for existing_tag, existing_data in tag_data.items():
        # FORMAT CŨ: existing_data là số (role_id)
        if isinstance(existing_data, int):
            if existing_data == role.id:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description=f"Role {role.mention} đã được gắn với tag **{existing_tag}**!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        # FORMAT MỚI: existing_data là dictionary
        elif isinstance(existing_data, dict):
            if existing_data.get("role_id") == role.id:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description=f"Role {role.mention} đã được gắn với tag **{existing_tag}**!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    
    # Kiểm tra xem tên tag đã tồn tại chưa
    if name in tag_data:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Tag **{name}** đã tồn tại!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Xử lý icon
    icon_data = None
    if icon:
        # Kiểm tra nếu là custom emoji (dạng <:name:id> hoặc :name:id)
        if icon.startswith('<:') and icon.endswith('>'):
            # Format: <:name:id>
            try:
                emoji_parts = icon[2:-1].split(':')
                if len(emoji_parts) == 2:
                    emoji_name, emoji_id = emoji_parts
                    icon_data = {
                        "type": "custom",
                        "name": emoji_name,
                        "id": int(emoji_id)
                    }
            except Exception as e:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="❌ Lỗi",
                        description=f"Custom emoji không hợp lệ: {e}",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
        elif ':' in icon and not icon.startswith('<'):
            # Format: :name:id
            try:
                emoji_parts = icon.split(':')
                if len(emoji_parts) == 2:
                    emoji_name, emoji_id = emoji_parts
                    icon_data = {
                        "type": "custom", 
                        "name": emoji_name,
                        "id": int(emoji_id)
                    }
            except Exception as e:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="❌ Lỗi",
                        description=f"Custom emoji không hợp lệ: {e}",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
        else:
            # Unicode emoji
            icon_data = {
                "type": "unicode",
                "emoji": icon
            }

    # Thêm tag mới với FORMAT MỚI
    tag_data[name] = {
        "role_id": role.id,
        "icon": icon_data
    }
    
    save_json(TAG_FILE, tag_data)
    
    # Tạo mô tả icon cho embed
    icon_description = "Không có icon"
    if icon_data:
        if icon_data["type"] == "custom":
            icon_description = f"Custom emoji: {icon_data['name']} (ID: {icon_data['id']})"
        else:
            icon_description = f"Unicode emoji: {icon_data['emoji']}"
    
    embed = discord.Embed(
        title="✅ Đã thêm tag",
        description=f"Đã thêm tag **{name}** với role {role.mention}",
        color=discord.Color.green()
    )
    embed.add_field(name="🎨 Icon", value=icon_description, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/add-tag role:{role.id} name:{name} icon:{icon}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/add-tag role:{role.id} name:{name} icon:{icon}", guild_name, "Slash Command")
    
def extract_name_and_emoji_from_tag(tag_name: str):
    """
    Tách emoji từ tag name - CHỈ TRẢ VỀ EMOJI
    """
    # Load tag data
    tag_data = load_json(TAG_FILE)
    
    if tag_name not in tag_data:
        return None
    
    tag_info = tag_data[tag_name]
    
    # FORMAT CŨ: tag_info là số (role_id)
    if isinstance(tag_info, int):
        return None
    
    # FORMAT MỚI: tag_info là dictionary
    # Kiểm tra xem có icon không
    if "icon" not in tag_info or not tag_info["icon"]:
        return None
    
    icon_data = tag_info["icon"]
    
    # Custom emoji
    if icon_data["type"] == "custom":
        try:
            return discord.PartialEmoji(name=icon_data["name"], id=icon_data["id"])
        except:
            return None
    # Unicode emoji
    elif icon_data["type"] == "unicode":
        return icon_data["emoji"]
    
    return None
    
@bot.tree.command(name="remove-tag", description="Xóa tag khỏi hệ thống")
@app_commands.describe(
    role="Role cần xóa khỏi tag system"
)
async def remove_tag(interaction: discord.Interaction, role: discord.Role):
    """Xóa tag khỏi file tag.json"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Load tag data hiện tại
    tag_data = load_json(TAG_FILE)
    
    # Tìm tag có role_id trùng
    tag_to_remove = None
    for tag_name, role_id in tag_data.items():
        if role_id == role.id:
            tag_to_remove = tag_name
            break
    
    if not tag_to_remove:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Role {role.mention} không có trong hệ thống tag!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Xóa tag
    del tag_data[tag_to_remove]
    save_json(TAG_FILE, tag_data)
    
    embed = discord.Embed(
        title="✅ Đã xóa tag",
        description=f"Đã xóa tag **{tag_to_remove}** với role {role.mention}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/remove-tag role:{role.id}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/remove-tag role:{role.id}", guild_name, "Slash Command")
    
@bot.tree.command(name="give-tag", description="Give tag cho user")
@app_commands.describe(
    user="User để give tag"
)
async def give_tag(interaction: discord.Interaction, user: discord.Member):
    """Give tag cho user thông qua dropdown"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Load tag data
    tag_data = load_json(TAG_FILE)
    if not tag_data:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không có tag nào trong hệ thống!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🎯 Give Tag",
        description=f"Chọn tag để give cho {user.mention}",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(
        embed=embed, 
        view=GiveTagView(user, tag_data), 
        ephemeral=True
    )
    
    # Log
    user_log = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user_log, f"/give-tag user:{user.id}", guild_name, "Slash Command")
    await send_dm_notification(user_log, f"/give-tag user:{user.id}", guild_name, "Slash Command")
    
@bot.tree.command(name="remove-user-tag", description="Remove tag khỏi user")
@app_commands.describe(
    user="User để remove tag"
)
async def remove_user_tag(interaction: discord.Interaction, user: discord.Member):
    """Remove tag khỏi user thông qua dropdown"""
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Load tag data
    tag_data = load_json(TAG_FILE)
    if not tag_data:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không có tag nào trong hệ thống!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Kiểm tra xem user có tag nào không
    has_any_tag = False
    for role_id in tag_data.values():
        role = discord.utils.get(user.guild.roles, id=role_id)
        if role and role in user.roles:
            has_any_tag = True
            break
    
    if not has_any_tag:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"{user.mention} không có tag nào để remove!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🎯 Remove User Tag",
        description=f"Chọn tag để remove khỏi {user.mention}",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(
        embed=embed, 
        view=RemoveUserTagView(user, tag_data), 
        ephemeral=True
    )
    
    # Log
    user_log = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user_log, f"/remove-user-tag user:{user.id}", guild_name, "Slash Command")
    await send_dm_notification(user_log, f"/remove-user-tag user:{user.id}", guild_name, "Slash Command")
    
@bot.tree.command(name="taixiu", description="Chơi Tài Xỉu")
@app_commands.describe(select="Chọn Tài hoặc Xỉu", amount="Số coin bạn muốn cược")
@app_commands.choices(select=[
    app_commands.Choice(name="Tài", value="tai"),
    app_commands.Choice(name="Xỉu", value="xiu")
])
async def taixiu(interaction: discord.Interaction, select: app_commands.Choice[str], amount: int):
    # Kiểm tra bị cấm
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    user_id = str(interaction.user.id)
    bal = get_balance(user_id)
    if bal < amount:
        await interaction.response.send_message(
            embed=simple_embed("❌ Không đủ tiền", f"Bạn chỉ có {bal}<:lonelycoin:1421380256148750429>", discord.Color.red()),
            ephemeral=True
        )
        return
    
    # Gửi tin nhắn ban đầu
    time_left = 40  # có thể chỉnh 40 nếu muốn
    content = (
        "<a:emoji_14:1421375592078639105> " * 3 +
        f"\n**Đang Tung Xúc Xắc...**\nThời Gian Còn Lại: **{time_left}s**"
    )
    await interaction.response.send_message(content=content)
    msg = await interaction.original_response()

    # Đếm ngược và update message
    while time_left > 0:
        await asyncio.sleep(1)   # ⏳ chỉnh interval update (3s cho an toàn)
        time_left -= 1
        if time_left < 0:
            time_left = 0
        content = (
            "<a:emoji_14:1421375592078639105> " * 3 +
            f"\n**Đang Tung Xúc Xắc...**\nThời Gian Còn Lại: **{time_left}s**"
        )
        await msg.edit(content=content)
    
    # Tung xúc xắc
    dice = [random.randint(1, 6) for _ in range(3)]
    total = sum(dice)
    result = "tai" if 11 <= total <= 17 else "xiu"

    # ✅ Xử lý kết quả
    win = (select.value == result)
    if win:
        add_balance(user_id, amount)
        outcome_text = f"🎉 Bạn thắng {amount}<:lonelycoin:1421380256148750429>!"
        color = discord.Color.green()
    else:
        remove_balance(user_id, amount)
        outcome_text = f"💀 Bạn thua {amount}<:lonelycoin:1421380256148750429>!"
        color = discord.Color.red()

    # 🔥 Lưu lịch sử
    add_taixiu_history(
        interaction.user.id,
        dice, total, result,
        win, amount
    )

    # Embed kết quả
    new_bal = get_balance(user_id)
    e = discord.Embed(title="🎲 Kết Quả Tài Xỉu", color=color)
    e.add_field(name="Xúc xắc", value=f"🎲 {dice[0]} • 🎲 {dice[1]} • 🎲 {dice[2]}", inline=False)
    e.add_field(name="Tổng", value=f"{total} → {result.upper()}", inline=False)
    e.add_field(name="Kết quả", value=outcome_text, inline=False)
    e.set_footer(text=f"Số dư: {new_bal}<:lonelycoin:1421380256148750429>")
    e.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)

    await msg.edit(content=None, embed=e)

    # LOG command
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/taixiu {select.value} {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/taixiu {select.value} {amount}", guild_name, "Slash Command")
    
@bot.tree.command(name="lichsutaixiu", description="Xem 5 trận gần nhất của bạn trong Tài Xỉu")
async def lichsutaixiu(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in taixiu_history or len(taixiu_history[user_id]) == 0:
        await interaction.response.send_message(
            embed=simple_embed("📜 Lịch Sử Tài Xỉu", "Bạn chưa chơi ván nào!", discord.Color.orange()),
            ephemeral=True
        )
        return

    embed = discord.Embed(title="📜 Lịch Sử Tài Xỉu (5 trận gần nhất)", color=discord.Color.blue())

    for rec in taixiu_history[user_id]:
        time = rec["time"]
        status, dice_str = rec["result"].split(",", 1)
        amount = rec["amount"]

        # Tách tiếp dice
        dice_part = dice_str.split("=")[0]     # "1,3,2"
        total_part = dice_str.split("=")[1]    # "6,Xiu"
        total, result = total_part.split(",")

        # Chuyển tiếng Việt
        vn_status = "Thắng" if status == "win" else "Thua"
        vn_result = "Tài" if result.lower() == "tai" else "Xỉu"

        embed.add_field(
            name=f"⏰ {time}",
            value=f"{vn_status} {amount}<:lonelycoin:1421380256148750429>\n🎲 {dice_part} = {total} → {vn_result}",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
@bot.tree.command(name="addcoin", description="(Admin) Thêm coin cho user")
async def addcoin(interaction: discord.Interaction, user_id: str, amount: int):
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    new_bal = add_balance(user_id, amount)  # HÀM ĐÃ ĐƯỢC SỬA
    await interaction.response.send_message(embed=simple_embed("✅ Đã Thêm Coin", f"Cộng {amount}<:lonelycoin:1421380256148750429> cho {user_id}\n💰 Số dư: {new_bal}<:lonelycoin:1421380256148750429>", discord.Color.green()))
    
    # LOG command
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/addcoin {user_id} {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/addcoin {user_id} {amount}", guild_name, "Slash Command")

@bot.tree.command(name="removecoin", description="(Admin) Trừ coin của user")
async def removecoin(interaction: discord.Interaction, user_id: str, amount: int):
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    new_bal = remove_balance(user_id, amount)  # HÀM ĐÃ ĐƯỢC SỬA
    await interaction.response.send_message(embed=simple_embed("⚠️ Đã Trừ Coin", f"Trừ {amount}<:lonelycoin:1421380256148750429> của {user_id}\n💰 Số dư: {new_bal}<:lonelycoin:1421380256148750429>", discord.Color.orange()))

    # LOG command
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/removecoin {user_id} {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/removecoin {user_id} {amount}", guild_name, "Slash Command")
    
@bot.tree.command(name="setcoin", description="(Admin) Set coin cho user")
async def setcoin(interaction: discord.Interaction, user_id: str, amount: int):
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    set_balance(user_id, amount)  # HÀM ĐÃ ĐƯỢC SỬA
    await interaction.response.send_message(embed=simple_embed("🔧 Đặt Coin", f"Số dư của {user_id} = {amount}<:lonelycoin:1421380256148750429>", discord.Color.blue()))
    
    # LOG command
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/setcoin {user_id} {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/setcoin {user_id} {amount}", guild_name, "Slash Command")
    
# Slash Command - Unbancmd: Gỡ cấm người dùng
@bot.tree.command(name="unbancmd", description="Gỡ cấm người dùng sử dụng bot")
@app_commands.describe(
    user_id="ID của người dùng cần gỡ cấm",
    reason="Lý do gỡ cấm"
)
async def unbancmd(interaction: discord.Interaction, user_id: str, reason: str):
    """Slash command gỡ cấm người dùng sử dụng bot"""
    # Kiểm tra quyền admin
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        # Chuyển đổi user_id sang integer
        target_user_id = int(user_id)
        
        # Kiểm tra xem user có bị cấm không
        if not is_user_banned(target_user_id):
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Người dùng này không bị cấm!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Xóa khỏi danh sách cấm + lưu file JSON
        del BANNED_USERS[target_user_id]
        save_banned_users()  # 🔥 thêm dòng này để persist sau restart
        
        # Thông báo thành công (⚡ trả lời trước)
        embed = discord.Embed(
            title="✅ Đã gỡ cấm người dùng",
            description=f"Đã gỡ cấm người dùng với ID {user_id}.\n**Lý do:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Sau khi trả lời xong mới log + gửi DM
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/unbancmd userid:{user_id} reason:{reason}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/unbancmd userid:{user_id} reason:{reason}", guild_name, "Slash Command")
        
    except ValueError:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi không xác định",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
# Slash Command - Bancmdlist: Hiển thị danh sách người dùng bị cấm
@bot.tree.command(name="bancmdlist", description="Hiển thị danh sách người dùng bị cấm sử dụng bot")
async def bancmdlist(interaction: discord.Interaction):
    """Slash command hiển thị danh sách người dùng bị cấm"""
    # Kiểm tra quyền admin
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    current_time = get_utc7_time()
    
    embed = discord.Embed(
        title="🔨 Danh sách người dùng bị cấm",
        description=get_banned_users_table(),
        color=discord.Color.orange(),
        timestamp=current_time
    )
    
    embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
    embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
    embed.set_thumbnail(url=ICON_URL)
    
    # ⚡ Phản hồi trước
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 📌 Log + gửi DM sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/bancmdlist", guild_name, "Slash Command")
    await send_dm_notification(user, "/bancmdlist", guild_name, "Slash Command")
    
# Slash Command - Addwhitelist: Thêm người dùng vào whitelist
@bot.tree.command(name="addwhitelist", description="Thêm người dùng vào danh sách được phép sử dụng bot")
@app_commands.describe(
    user_id="ID của người dùng cần thêm",
    display_name="Tên hiển thị của người dùng"
)
async def addwhitelist(interaction: discord.Interaction, user_id: str, display_name: str):
    """Slash command thêm người dùng vào whitelist"""
    # Kiểm tra quyền admin
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        # Chuyển đổi user_id sang integer
        target_user_id = int(user_id)
        
        # Kiểm tra xem user đã có trong whitelist chưa
        if target_user_id in ALLOWED_USERS:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Người dùng này đã có trong whitelist!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # ✅ Thêm vào whitelist và lưu JSON
        ALLOWED_USERS[target_user_id] = display_name
        save_whitelist()  # 🔥 lưu lại ngay vào whitelist.json
        
        # ⚡ Phản hồi thành công trước
        embed = discord.Embed(
            title="✅ Đã thêm vào whitelist",
            description=f"Đã thêm người dùng {display_name} (ID: {user_id}) vào whitelist.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # 📌 Sau khi phản hồi mới log + DM
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/addwhitelist userid:{user_id} name:{display_name}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/addwhitelist userid:{user_id} name:{display_name}", guild_name, "Slash Command")
        
    except ValueError:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi không xác định",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

# ====== ECONOMY COMMANDS ======
@bot.command()
async def balance(ctx):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    balance_amount = get_balance(ctx.author.id)
    embed = discord.Embed(title="💳 Số dư", description=f"{ctx.author.mention}, bạn có **{balance_amount}**<:lonelycoin:1421380256148750429>.", color=discord.Color.green())
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "!balance", guild_name, "Text Command")
    await send_dm_notification(user, "!balance", guild_name, "Text Command")

@bot.tree.command(name="balance", description="Xem số dư của bạn")
async def balance_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    balance_amount = get_balance(interaction.user.id)
    embed = discord.Embed(title="💳 Số dư", description=f"{interaction.user.mention}, bạn có **{balance_amount}**<:lonelycoin:1421380256148750429>.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/balance", guild_name, "Slash Command")
    await send_dm_notification(user, "/balance", guild_name, "Slash Command")

@bot.tree.command(name="daily", description="Nhận phần thưởng đăng nhập hằng ngày")
async def daily(interaction: discord.Interaction):
    user_id = str(interaction.user.id)  # ĐẢM BẢO CHUYỂN THÀNH STRING
    now = datetime.datetime.now()

    user_info = daily_data.get(user_id, {
        "last_claimed": None,
        "date": None,
        "time": None,
        "last_box": None
    })

    # check đã nhận xu hôm nay chưa
    if user_info["last_claimed"]:
        last_claimed = datetime.datetime.fromisoformat(user_info["last_claimed"])
        if last_claimed.date() == now.date():
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Hôm nay bạn đã nhận daily rồi!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # === Thưởng xu ===
    reward = 100  # số xu daily
    credits[user_id] = credits.get(user_id, 0) + reward

    # update daily info
    user_info["last_claimed"] = now.isoformat()
    user_info["date"] = now.strftime("%d/%m/%Y")
    user_info["time"] = now.strftime("%H:%M:%S")

    # === Embed kết quả ===
    embed = discord.Embed(
        title="🎁 Daily Reward",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Xu nhận được", value=f"+{reward} <:lonelycoin:1421380256148750429>\n(Tổng: {credits[user_id]} <:lonelycoin:1421380256148750429>)", inline=False)

    # === Thưởng Mystery Box (cách 7 ngày) ===
    got_box = False
    if user_info["last_box"]:
        last_box_date = datetime.datetime.fromisoformat(user_info["last_box"]).date()
    else:
        last_box_date = now.date() - datetime.timedelta(days=7)

    if (now.date() - last_box_date).days >= 7:
        box[user_id] = box.get(user_id, 0) + 1
        user_info["last_box"] = now.isoformat()
        got_box = True
        embed.add_field(
            name="📦 Mystery Box",
            value=f"+1 <:enderchest:1422102654766678116>\n(Tổng: {box[user_id]} <:enderchest:1422102654766678116>)",
            inline=False
        )
        

    if not got_box:
        embed.add_field(
            name="📦 Mystery Box",
            value=f"Bạn hiện có **{box.get(user_id, 0)}** <:enderchest:1422102654766678116>",
            inline=False
        )

    # lưu lại
    daily_data[user_id] = user_info
    save_json(DAILY_FILE, daily_data)
    save_json(DATA_FILE, credits)
    save_json(BOX_FILE, box)

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/daily", guild_name, "Slash Command")
    await send_dm_notification(user, "/daily", guild_name, "Slash Command")
    
@bot.command()
async def work(ctx):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    can_work_result, work_count = can_work(ctx.author.id)
    if not can_work_result:
        embed = discord.Embed(
            title="❌ Đã đạt giới hạn",
            description=f"Bạn đã work {work_count}/5 lần hôm nay!\n⏰ Chờ đến ngày mai để reset.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra cooldown 90 giây
    user_id = str(ctx.author.id)
    if user_id in work_data and "last_work" in work_data[user_id]:
        last_work = datetime.datetime.fromisoformat(work_data[user_id]["last_work"])
        cooldown = datetime.timedelta(seconds=90)
        if datetime.datetime.now() - last_work < cooldown:
            wait_seconds = int((cooldown - (datetime.datetime.now() - last_work)).total_seconds())
            embed = discord.Embed(
                title="⏳ Đang chờ cooldown",
                description=f"Vui lòng chờ {wait_seconds} giây nữa!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
    
    earn = random.randint(50, 200)
    add_balance(ctx.author.id, earn)
    update_work(ctx.author.id)
    
    embed = discord.Embed(
        title="💼 Làm việc",
        description=f"{ctx.author.mention} làm việc kiếm được **{earn}**<:lonelycoin:1421380256148750429>\n📊 Lần work: {work_count + 1}/5\n⏰ Thời gian: {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "!work", guild_name, "Text Command")
    await send_dm_notification(user, "!work", guild_name, "Text Command")

@bot.tree.command(name="work", description="Làm việc để kiếm credits")
async def work_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    can_work_result, work_count = can_work(interaction.user.id)
    if not can_work_result:
        embed = discord.Embed(
            title="❌ Đã đạt giới hạn",
            description=f"Bạn đã work {work_count}/5 lần hôm nay!\n⏰ Chờ đến ngày mai để reset.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Kiểm tra cooldown 90 giây
    user_id = str(interaction.user.id)
    if user_id in work_data and "last_work" in work_data[user_id]:
        last_work = datetime.datetime.fromisoformat(work_data[user_id]["last_work"])
        cooldown = datetime.timedelta(seconds=90)
        if datetime.datetime.now() - last_work < cooldown:
            wait_seconds = int((cooldown - (datetime.datetime.now() - last_work)).total_seconds())
            embed = discord.Embed(
                title="⏳ Đang chờ cooldown",
                description=f"Vui lòng chờ {wait_seconds} giây nữa!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    earn = random.randint(50, 200)
    add_balance(interaction.user.id, earn)
    update_work(interaction.user.id)
    
    embed = discord.Embed(
        title="💼 Làm việc",
        description=f"{interaction.user.mention} đã làm việc và kiếm được **{earn}**<:lonelycoin:1421380256148750429>\n📊 Lần work: {work_count + 1}/5\n⏰ Thời gian: {datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')}",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/work", guild_name, "Slash Command")
    await send_dm_notification(user, "/work", guild_name, "Slash Command")
    
@bot.command()
async def gamble(ctx, amount: int):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if amount <= 0:
        embed = discord.Embed(title="❌ Lỗi", description="Số <:lonelycoin:1421380256148750429> phải lớn hơn 0!", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    if get_balance(ctx.author.id) < amount:
        embed = discord.Embed(title="❌ Lỗi", description="Không đủ <:lonelycoin:1421380256148750429>!", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    if random.random() < 0.5:
        remove_balance(ctx.author.id, amount)
        embed = discord.Embed(title="💥 Thua", description=f"Thua **{amount}**<:lonelycoin:1421380256148750429>!", color=discord.Color.red())
    else:
        add_balance(ctx.author.id, amount)
        embed = discord.Embed(title="🎉 Thắng", description=f"Thắng **{amount}**<:lonelycoin:1421380256148750429>!", color=discord.Color.green())
    
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!gamble {amount}", guild_name, "Text Command")
    await send_dm_notification(user, f"!gamble {amount}", guild_name, "Text Command")

@bot.tree.command(name="gamble", description="Cược credits (tỉ lệ thắng 50%)")
async def gamble_slash(interaction: discord.Interaction, amount: int):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if amount <= 0:
        embed = discord.Embed(title="❌ Lỗi", description="Số credits phải lớn hơn 0!", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if get_balance(interaction.user.id) < amount:
        embed = discord.Embed(title="❌ Lỗi", description="Không đủ credits!", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if random.random() < 0.5:
        remove_balance(interaction.user.id, amount)
        embed = discord.Embed(title="💥 Thua", description=f"Thua **{amount}**<:lonelycoin:1421380256148750429>!", color=discord.Color.red())
    else:
        add_balance(interaction.user.id, amount)
        embed = discord.Embed(title="🎉 Thắng", description=f"Thắng **{amount}**<:lonelycoin:1421380256148750429>!", color=discord.Color.green())
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/gamble {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/gamble {amount}", guild_name, "Slash Command")

@bot.command()
async def guess(ctx, number: int):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if number < 1 or number > 10:
        embed = discord.Embed(title="❌ Lỗi", description="Chọn số từ 1 đến 10!", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    win = random.randint(1, 10)
    if number == win:
        add_balance(ctx.author.id, 200)
        embed = discord.Embed(title="🎯 Đúng!", description=f"Số đúng là {win}! Bạn nhận **200**<:lonelycoin:1421380256148750429>.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="❌ Sai!", description=f"Số đúng là {win}. Thử lại nhé!", color=discord.Color.red())
    
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!guess {number}", guild_name, "Text Command")
    await send_dm_notification(user, f"!guess {number}", guild_name, "Text Command")

@bot.tree.command(name="guess", description="Đoán số từ 1-10 để nhận 200 credits")
async def guess_slash(interaction: discord.Interaction, number: int):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if number < 1 or number > 10:
        embed = discord.Embed(title="❌ Lỗi", description="Chọn số từ 1 đến 10!", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    win = random.randint(1, 10)
    if number == win:
        add_balance(interaction.user.id, 200)
        embed = discord.Embed(title="🎯 Đúng!", description=f"Số đúng là {win}! Bạn nhận **200**<:lonelycoin:1421380256148750429>.", color=discord.Color.green())
    else:
        embed = discord.Embed(title="❌ Sai!", description=f"Số đúng là {win}. Thử lại nhé!", color=discord.Color.red())
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/guess {number}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/guess {number}", guild_name, "Slash Command")

@bot.command()
async def slot(ctx, amount: int):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if amount <= 0:
        embed = discord.Embed(title="❌ Lỗi", description="Số <:lonelycoin:1421380256148750429> phải lớn hơn 0!", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    if get_balance(ctx.author.id) < amount:
        embed = discord.Embed(title="❌ Lỗi", description="Không đủ <:lonelycoin:1421380256148750429>!", color=discord.Color.red())
        return await ctx.send(embed=embed)
    
    symbols = ["🍒", "🍋", "🍉", "⭐", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    
    embed = discord.Embed(title="🎰 Slot Machine", description=" | ".join(result), color=discord.Color.purple())
    
    if len(set(result)) == 1:
        add_balance(ctx.author.id, amount * 5)
        embed.add_field(name="🎰 JACKPOT!", value=f"Bạn nhận **{amount * 5}**<:lonelycoin:1421380256148750429>!", inline=False)
    elif len(set(result)) == 2:
        add_balance(ctx.author.id, amount * 2)
        embed.add_field(name="🎰 Trúng nhỏ!", value=f"Bạn nhận **{amount * 2}**<:lonelycoin:1421380256148750429>!", inline=False)
    else:
        remove_balance(ctx.author.id, amount)
        embed.add_field(name="🎰 Thua!", value=f"Mất **{amount}**<:lonelycoin:1421380256148750429>!", inline=False)
    
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!slot {amount}", guild_name, "Text Command")
    await send_dm_notification(user, f"!slot {amount}", guild_name, "Text Command")

@bot.tree.command(name="slot", description="Chơi slot machine với credits")
async def slot_slash(interaction: discord.Interaction, amount: int):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if amount <= 0:
        embed = discord.Embed(title="❌ Lỗi", description="Số <:lonelycoin:1421380256148750429> phải lớn hơn 0!", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    if get_balance(interaction.user.id) < amount:
        embed = discord.Embed(title="❌ Lỗi", description="Không đủ <:lonelycoin:1421380256148750429>!", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    symbols = ["🍒", "🍋", "🍉", "⭐", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    
    embed = discord.Embed(title="🎰 Slot Machine", description=" | ".join(result), color=discord.Color.purple())
    
    if len(set(result)) == 1:
        add_balance(interaction.user.id, amount * 5)
        embed.add_field(name="🎰 JACKPOT!", value=f"Bạn nhận **{amount * 5}**<:lonelycoin:1421380256148750429>!", inline=False)
    elif len(set(result)) == 2:
        add_balance(interaction.user.id, amount * 2)
        embed.add_field(name="🎰 Trúng nhỏ!", value=f"Bạn nhận **{amount * 2}**<:lonelycoin:1421380256148750429>!", inline=False)
    else:
        remove_balance(interaction.user.id, amount)
        embed.add_field(name="🎰 Thua!", value=f"Mất **{amount}**<:lonelycoin:1421380256148750429>!", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/slot {amount}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/slot {amount}", guild_name, "Slash Command")

# ====== SHOP SYSTEM ======
@bot.command()
async def shop(ctx):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(title="🏪 Cửa Hàng", color=discord.Color.blue())
    
    for role_id, item in shop_data.items():
        embed.add_field(
            name=f"🛒 {item['name']} - {item['price']}<:lonelycoin:1421380256148750429>",
            value=f"{item['description']}",
            inline=False
        )
    
    embed.set_footer(text="Sử dụng /buy để mua items")
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "!shop", guild_name, "Text Command")
    await send_dm_notification(user, "!shop", guild_name, "Text Command")

class ScriptDropdown(discord.ui.Select):
    def __init__(self, script_data):
        options = []
        for key, item in script_data.items():
            options.append(
                discord.SelectOption(
                    label=item["name"],
                    value=key
                )
            )

        super().__init__(
            placeholder="📜 Chọn script để xem...",
            custom_id="script_dropdown",
            min_values=1,
            max_values=1,
            options=options
        )
        self.script_data = script_data

    async def callback(self, interaction: discord.Interaction):
        script_key = self.values[0]
        script = self.script_data[script_key]

        # ✅ Chỉnh sửa tin nhắn thành code block text, không dùng embed
        content = f"{script['loader']}"
        await interaction.response.edit_message(content=content, embed=None, view=None)


class ScriptView(discord.ui.View):
    def __init__(self, script_data):
        super().__init__(timeout=60)
        self.add_item(ScriptDropdown(script_data))


@bot.tree.command(name="script", description="Xem danh sách script")
async def script_slash(interaction: discord.Interaction):
    file_path = os.path.join(DATA_DIR, "listscript.json")
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Lỗi",
                description=f"Không đọc được file `listscript.json`\n```{e}```",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    embed = discord.Embed(
        title="📜 Script List",
        description="Chọn script bạn muốn từ menu bên dưới:",
        color=discord.Color.blue()
    )
    view = ScriptView(script_data)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
       
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/script", guild_name, "Slash Command")
    await send_dm_notification(user, "/script", guild_name, "Slash Command")

@bot.tree.command(name="shop", description="Xem cửa hàng")
async def shop_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(title="🏪 Cửa Hàng", color=discord.Color.blue())
    
    for role_id, item in shop_data.items():
        embed.add_field(
            name=f"🛒 {item['name']} - {item['price']}<:lonelycoin:1421380256148750429>",
            value=f"{item['description']}",
            inline=False
        )
    
    embed.set_footer(text="Sử dụng /buy để mua items")
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/shop", guild_name, "Slash Command")
    await send_dm_notification(user, "/shop", guild_name, "Slash Command")

def extract_name_and_emoji(item_name: str):
    """
    Tách emoji custom + tên role từ item['name']
    VD: "<:vip:1421359862780264489> VIP Role"
    """
    match = re.match(r"<:(\w+):(\d+)> ?(.*)", item_name)
    if match:
        emoji_name, emoji_id, label = match.groups()
        return discord.PartialEmoji(name=emoji_name, id=int(emoji_id)), label
    return None, item_name


class BuyDropdown(discord.ui.Select):
    def __init__(self, shop_data):
        options = []
        for key, item in shop_data.items():
            emoji, label = extract_name_and_emoji(item["name"])
            options.append(
                discord.SelectOption(
                    label=label,
                    description=f"{item['price']} coins",
                    value=key,
                    emoji=emoji
                )
            )

        super().__init__(
            placeholder="🛒 Chọn item muốn mua...",
            min_values=1, max_values=1,
            options=options
        )
        self.shop_data = shop_data

    async def callback(self, interaction: discord.Interaction):
        item_key = self.values[0]
        item = self.shop_data[item_key]

        embed = discord.Embed(
            title="🛒 Xác nhận mua hàng",
            description=f"Bạn có muốn mua **{item['name']}** với giá **{item['price']}<:lonelycoin:1421380256148750429> không**?",
            color=discord.Color.blue()
        )
        view = ConfirmBuyView(item_key, item)
        await interaction.response.edit_message(embed=embed, view=view)


class ConfirmBuyView(discord.ui.View):
    def __init__(self, item_key, item):
        super().__init__(timeout=60)
        self.item_key = item_key
        self.item = item

    @discord.ui.button(label="Mua", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if is_user_banned(interaction.user.id):
            embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if get_balance(interaction.user.id) < self.item["price"]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Không đủ coins",
                    description="Bạn không có đủ <:lonelycoin:1421380256148750429> để mua!",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

        role = interaction.guild.get_role(self.item["role_id"])
        if not role:
            return await interaction.response.send_message(
                embed=discord.Embed(title="❌ Lỗi", description="Role không tồn tại!", color=discord.Color.red()),
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                embed=discord.Embed(title="❌ Lỗi", description="Bạn đã có vật phẩm này rồi!", color=discord.Color.red()),
                ephemeral=True
            )

        # ✅ Trừ coin + add role
        remove_balance(interaction.user.id, self.item["price"])
        await interaction.user.add_roles(role)

        await interaction.response.edit_message(
            embed=discord.Embed(
                title="✅ Mua thành công",
                description=f"Bạn đã mua **{self.item['name']}** với giá <:lonelycoin:1421380256148750429>!",
                color=discord.Color.green()
            ),
            view=None
        )

        # 🔥 Log giao dịch
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/buy", guild_name, "Slash Command")
        await send_dm_notification(user, f"/buy", guild_name, "Slash Command")

    @discord.ui.button(label="Đóng", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ Đã huỷ",
                description="Bạn đã huỷ giao dịch.",
                color=discord.Color.red()
            ),
            view=None
        )


class BuyView(discord.ui.View):
    def __init__(self, shop_data):
        super().__init__(timeout=60)
        self.add_item(BuyDropdown(shop_data))


@bot.tree.command(name="buy", description="Mua item từ cửa hàng")
async def buy_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        return await interaction.response.send_message(
            embed=discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot!", color=discord.Color.red()),
            ephemeral=True
        )

    embed = discord.Embed(
        title="🏪 Cửa hàng",
        description="Chọn item bạn muốn mua từ menu bên dưới:",
        color=discord.Color.blue()
    )
    view = BuyView(shop_data)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/buy {item.value}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/buy ({item.value})", guild_name, "Slash Command")

# ====== LEVEL COMMANDS ======
@bot.command()
async def rank(ctx, member: discord.Member = None):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    member = member or ctx.author
    user_data = levels.get(str(member.id), {"xp": 0, "level": 1})
    
    embed = discord.Embed(title="🏆 Rank", color=discord.Color.purple())
    embed.add_field(name="👤 User", value=member.mention, inline=True)
    embed.add_field(name="📊 Level", value=user_data['level'], inline=True)
    embed.add_field(name="⭐ XP", value=user_data['xp'], inline=True)
    
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!rank {member.name}", guild_name, "Text Command")
    await send_dm_notification(user, f"!rank {member.name}", guild_name, "Text Command")

@bot.tree.command(name="rank", description="Xem level và XP của bạn hoặc thành viên khác")
async def rank_slash(interaction: discord.Interaction, member: discord.Member = None):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    member = member or interaction.user
    user_data = levels.get(str(member.id), {"xp": 0, "level": 1})
    
    embed = discord.Embed(title="🏆 Rank", color=discord.Color.purple())
    embed.add_field(name="👤 User", value=member.mention, inline=True)
    embed.add_field(name="📊 Level", value=user_data['level'], inline=True)
    embed.add_field(name="⭐ XP", value=user_data['xp'], inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/rank", guild_name, "Slash Command")
    await send_dm_notification(user, "/rank", guild_name, "Slash Command")

@bot.command()
async def leaderboard(ctx, type: str = "coins"):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if type == "coins":
        top = sorted(credits.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = discord.Embed(title="🏅 Top 10 Coins", color=discord.Color.gold())
        for i, (uid, amt) in enumerate(top, 1):
            user = ctx.guild.get_member(int(uid))
            name = user.display_name if user else f"User {uid}"
            embed.add_field(name=f"{i}. {name}", value=f"{amt} <:lonelycoin:1421380256148750429>", inline=False)
    elif type == "level":
        top = sorted(levels.items(), key=lambda x: x[1].get("level", 1), reverse=True)[:10]
        embed = discord.Embed(title="🏅 Top 10 Levels", color=discord.Color.gold())
        for i, (uid, info) in enumerate(top, 1):
            user = ctx.guild.get_member(int(uid))
            name = user.display_name if user else f"User {uid}"
            embed.add_field(name=f"{i}. {name}", value=f"Level {info.get('level', 1)}", inline=False)
    else:
        embed = discord.Embed(title="❌ Lỗi", description="Loại leaderboard không hợp lệ! Dùng 'credits' hoặc 'level'", color=discord.Color.red())
    
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!leaderboard {type}", guild_name, "Text Command")
    await send_dm_notification(user, f"!leaderboard {type}", guild_name, "Text Command")

@bot.tree.command(name="leaderboard", description="Xem bảng xếp hạng coins hoặc level")
@app_commands.describe(type="Chọn loại bảng xếp hạng")
@app_commands.choices(type=[
    app_commands.Choice(name="Coins", value="coins"),
    app_commands.Choice(name="Level", value="level")
])
async def leaderboard_slash(interaction: discord.Interaction, type: app_commands.Choice[str]):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Dùng value từ dropdown
    type = type.value  

    if type == "coins":
        top = sorted(credits.items(), key=lambda x: x[1], reverse=True)[:10]
        embed = discord.Embed(title="🏅 Top 10 Coins", color=discord.Color.gold())
        for i, (uid, amt) in enumerate(top, 1):
            try:
                user = await bot.fetch_user(int(uid))
                name = user.name
            except:
                name = f"User {uid}"
            embed.add_field(name=f"{i}. {name}", value=f"{amt} <:lonelycoin:1421380256148750429>", inline=False)

    elif type == "level":
        top = sorted(levels.items(), key=lambda x: x[1].get("level", 1), reverse=True)[:10]
        embed = discord.Embed(title="🏅 Top 10 Levels", color=discord.Color.gold())
        for i, (uid, info) in enumerate(top, 1):
            try:
                user = await bot.fetch_user(int(uid))
                name = user.name
            except:
                name = f"User {uid}"
            embed.add_field(name=f"{i}. {name}", value=f"Level {info.get('level', 1)}", inline=False)

    else:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Loại leaderboard không hợp lệ!",
            color=discord.Color.red()
        )

    await interaction.response.send_message(embed=embed, ephemeral=False)

    # Log
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, f"/leaderboard {type}", guild_name, "Slash Command")
    await send_dm_notification(user, f"/leaderboard {type}", guild_name, "Slash Command")
    
# ====== UTILITY COMMANDS ======
@bot.command()
async def serverinfo(ctx):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    guild = ctx.guild
    embed = discord.Embed(title=f"🏠 Thông tin server: {guild.name}", color=0x00ff00)
    embed.add_field(name="👥 Thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="👑 Chủ server", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 Tạo ngày", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "!serverinfo", guild_name, "Text Command")
    await send_dm_notification(user, "!serverinfo", guild_name, "Text Command")

@bot.tree.command(name="serverinfo", description="Xem thông tin server")
async def serverinfo_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    guild = interaction.guild
    embed = discord.Embed(title=f"🏠 Thông tin server: {guild.name}", color=0x00ff00)
    embed.add_field(name="👥 Thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="👑 Chủ server", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 Tạo ngày", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/serverinfo", guild_name, "Slash Command")
    await send_dm_notification(user, "/serverinfo", guild_name, "Slash Command")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 Thông tin user: {member.name}", color=0x00ff00)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📅 Tham gia server", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, f"!userinfo {member.name}", guild_name, "Text Command")
    await send_dm_notification(user, f"!userinfo {member.name}", guild_name, "Text Command")

@bot.tree.command(name="userinfo", description="Xem thông tin user")
async def userinfo_slash(interaction: discord.Interaction, member: discord.Member = None):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 Thông tin user: {member.name}", color=0x00ff00)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📅 Tham gia server", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/userinfo", guild_name, "Slash Command")
    await send_dm_notification(user, "/userinfo", guild_name, "Slash Command")

@bot.command()
async def premium(ctx):
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(title="💎 Premium", description=f"{ctx.author.mention}, bạn đang dùng bản Free.", color=0xffd700)
    embed.add_field(name="Tính năng Premium", value="• Không giới hạn music\n• Priority support\n• Custom commands", inline=False)
    await ctx.send(embed=embed)
    
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "!premium", guild_name, "Text Command")
    await send_dm_notification(user, "!premium", guild_name, "Text Command")

@bot.tree.command(name="premium", description="Thông tin về gói Premium")
async def premium_slash(interaction: discord.Interaction):
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(title="💎 Premium", description=f"{interaction.user.mention}, bạn đang dùng bản Free.", color=0xffd700)
    embed.add_field(name="Tính năng Premium", value="• Không giới hạn music\n• Priority support\n• Custom commands", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/premium", guild_name, "Slash Command")
    await send_dm_notification(user, "/premium", guild_name, "Slash Command")

# Slash Command - Removewhitelist: Xóa người dùng khỏi whitelist
@bot.tree.command(name="removewhitelist", description="Xóa người dùng khỏi danh sách được phép sử dụng bot")
@app_commands.describe(
    user_id="ID của người dùng cần xóa"
)
async def removewhitelist(interaction: discord.Interaction, user_id: str):
    """Slash command xóa người dùng khỏi whitelist"""
    # Kiểm tra quyền admin
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        # Chuyển đổi user_id sang integer
        target_user_id = int(user_id)
        
        # Kiểm tra xem user có trong whitelist không
        if target_user_id not in ALLOWED_USERS:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Người dùng này không có trong whitelist!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Xóa khỏi whitelist + lưu lại JSON
        removed_user = ALLOWED_USERS.pop(target_user_id)
        save_whitelist()  # 🔥 lưu whitelist.json ngay sau khi xoá
        
        # ⚡ Trả lời thành công trước
        embed = discord.Embed(
            title="✅ Đã xóa khỏi whitelist",
            description=f"Đã xóa người dùng {removed_user} (ID: {user_id}) khỏi whitelist.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # 📌 Sau khi phản hồi, mới log + DM
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/removewhitelist userid:{user_id}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/removewhitelist userid:{user_id}", guild_name, "Slash Command")
        
    except ValueError:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi không xác định",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
# Slash Command - Premium Commands (Admin only)
@bot.tree.command(name="premium_command", description="Hiển thị các lệnh premium chỉ dành cho admin")
async def premium_command(interaction: discord.Interaction):
    """Slash command hiển thị các lệnh premium"""
    # Kiểm tra quyền
    if not is_user_allowed(interaction.user.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    current_time = get_utc7_time()
    embed = discord.Embed(
        title="Premium Commands",
        description="List of available premium command",
        color=0x00ffaa,
        timestamp=current_time
    )
    embed.set_author(name="Lonely Hub Bot", icon_url=ICON_URL)

    embed.add_field(
        name="**?nukeall**",
        value="Nuke the server with ping everyone\n\n**Requirements:** Bot must have permission to create, delete channels, rename servers and ping everyone",
        inline=False
    )
    embed.add_field(
        name="**?raidall**",
        value="Raid all channel with ping everyone and message.\n\n**Requirements:** Bot must have permission to ping everyone.",
        inline=False
    )
    embed.add_field(name="**?spampingall**", value="Spam ping everyone all channels", inline=False)
    embed.add_field(
        name="**?banalluser**",
        value="Ban all user with ultra-speed\n\n**Requirements:** The bot needs to have the highest role in the server.",
        inline=False
    )
    embed.add_field(
        name="**?purge [quantity]**",
        value="Xóa số lượng tin nhắn được chỉ định\n\n**Requirements:** Bot must have permission to manage messages.",
        inline=False
    )
    embed.add_field(
        name="**?purgeallwebhook**",
        value="Xóa tất cả webhook trong server\n\n**Requirements:** Bot must have permission to manage webhooks.",
        inline=False
    )

    embed.set_footer(text="Lonely Hub Bot", icon_url=FOOTER_ICON_URL)
    embed.set_thumbnail(url=ICON_URL)

    # ⚡ trả lời ngay trước (ephemeral để chỉ người gọi thấy)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 📌 log + gửi DM chạy sau khi đã phản hồi
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/premium_command", guild_name, "Slash Command")
    await send_dm_notification(user, "/premium_command", guild_name, "Slash Command")
# Slash Command - Help
class HelpView(discord.ui.View):
    def __init__(self, pages, author_id):
        super().__init__(timeout=120)
        self.pages = pages
        self.current = 0
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Bạn không được phép thao tác.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="⏮️ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current - 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="⏭️ Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = (self.current + 1) % len(self.pages)
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.red)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        self.stop()
            
# Slash Command - Ping
@bot.tree.command(name="ping", description="Kiểm tra độ trễ của bot")
async def ping(interaction: discord.Interaction):
    """Slash command ping"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    latency = round(bot.latency * 1000)
    current_time = get_utc7_time()
    
    # ⚡ Phản hồi trước
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**\n⏰ Thời gian: **{current_time.strftime('%H:%M:%S %d/%m/%Y')}** (UTC+7)",
        color=discord.Color.green(),
        timestamp=current_time
    )
    embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
    embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 📌 Sau khi phản hồi, mới log + DM
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/ping", guild_name, "Slash Command")
    await send_dm_notification(user, "/ping", guild_name, "Slash Command")
    
# Lenh Info
@bot.tree.command(name="info", description="Xem thông tin về bot")
async def info(interaction: discord.Interaction):
    """Slash command info"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    current_time = get_utc7_time()
    
    # ⚡ Phản hồi trước
    embed = discord.Embed(
        title="🤖 Bot Information",
        description="Bot logging system với UTC+7",
        color=discord.Color.blue(),
        timestamp=current_time
    )
    embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
    embed.add_field(name="🕐 Múi giờ", value="UTC+7", inline=True)
    embed.add_field(name="📊 Số server", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="⚡ Độ trễ", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="📝 Logging", value="Text commands & Slash commands", inline=False)
    embed.add_field(name="📨 DM Notification", value=f"Gửi đến {len(ALLOWED_USERS)} user", inline=True)
    embed.add_field(name="👥 User được phép spam", value=str(len(ALLOWED_USERS)), inline=True)
    embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
    embed.set_thumbnail(url=ICON_URL)
    
    await interaction.response.send_message(embed=embed)

    # 📌 Sau khi phản hồi, mới log + DM
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/info", guild_name, "Slash Command")
    await send_dm_notification(user, "/info", guild_name, "Slash Command")
    
# Slash Command - Whitelist: Hiển thị danh sách user được phép
@bot.tree.command(name="whitelist", description="Xem danh sách user whitelist")
async def whitelist(interaction: discord.Interaction):
    """Slash command hiển thị danh sách user whitelist"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # LOG TRƯỚC KHI PHẢN HỒI
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    log_command(user, "/whitelist", guild_name, "Slash Command")

    # Gửi DM thông báo với Embed
    await send_dm_notification(user, "/whitelist", guild_name, "Slash Command")

    current_time = get_utc7_time()

    # 🔥 Đọc trực tiếp whitelist từ JSON
    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        data = {}
        print(f"[ERROR] Không thể đọc {WHITELIST_FILE}: {e}")

    if not data:
        desc = "⚠️ Hiện chưa có user nào trong whitelist."
    else:
        desc = "```\nDanh sách user whitelist:\n"
        desc += "-" * 21 + "\n"
        for uid, name in data.items():
            desc += f"Tên: {name}\n"
            desc += f"ID : {uid}\n"
            desc += "-" * 21 + "\n"
        desc += f"Tổng số: {len(data)} user được phép sử dụng lệnh premium\n```"

    embed = discord.Embed(
        title="👥 Danh sách User Whitelist",
        description=desc,
        color=discord.Color.purple(),
        timestamp=current_time
    )
    embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
    embed.set_footer(
        text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}",
        icon_url=FOOTER_ICON_URL
    )
    embed.set_thumbnail(url=ICON_URL)

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
# Slash Command - Ghostping
@bot.tree.command(name="ghostping", description="Ghost ping người dùng")
@app_commands.describe(
    user_id="ID của người dùng cần ghost ping",
    delay="Thời gian delay giữa các lần ping (giây), tối thiểu 0.1",
    quantity="Số lượng ping, mặc định là 5, tối đa 50"
)
async def ghostping(interaction: discord.Interaction, user_id: str, delay: float = 0.5, quantity: int = 5):
    """Slash command ghost ping"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if interaction.guild and interaction.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Phản hồi trước để tránh lỗi Unknown interaction
    await interaction.response.send_message(
        embed=discord.Embed(
            title="⏳ Đang xử lý...",
            description=f"Đang chuẩn bị ghost ping {quantity} lần với delay {delay}s...",
            color=discord.Color.orange()
        ),
        ephemeral=True
    )
    
    try:
        target_user_id = int(user_id)
        target_user = await bot.fetch_user(target_user_id)
        
        sent_count = 0
        for i in range(quantity):
            try:
                ping_message = await interaction.channel.send(f"{target_user.mention}")
                await asyncio.sleep(0.3)
                await ping_message.delete()
                sent_count += 1
                
                if i < quantity - 1:
                    await asyncio.sleep(delay)
                    
            except discord.Forbidden:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Lỗi",
                        description="Bot không có quyền xóa tin nhắn!",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            except Exception as e:
                print(f"[ERROR] Lỗi khi ghost ping: {e}")
        
        # Thông báo thành công
        await interaction.followup.send(
            embed=discord.Embed(
                title="✅ Hoàn thành",
                description=f"Đã thực hiện {sent_count}/{quantity} lần ghost ping đến {target_user.mention}",
                color=discord.Color.green()
            ),
            ephemeral=True
        )
        
        # 🔥 LOG SAU KHI HOÀN THÀNH
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/ghostping userid:{user_id} delay:{delay} quantity:{quantity}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/ghostping userid:{user_id} delay:{delay} quantity:{quantity}", guild_name, "Slash Command")
        
    except ValueError:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description="User ID không hợp lệ!",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    except discord.NotFound:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description="Không tìm thấy user!",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
       
@bot.tree.command(name="ghostpingv2", description="Ghost ping người dùng (ko cần invite)")
@app_commands.describe(
    user_id="ID của người dùng cần ghost ping",
    delay="Thời gian delay giữa các lần ping (giây), tối thiểu 0.1",
    quantity="Số lượng ping, mặc định là 5, tối đa 50"
)
async def ghostpingv2(interaction: discord.Interaction, user_id: str, delay: float = 0.5, quantity: int = 5):
    """Slash command ghost ping"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if interaction.guild and interaction.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Defer để dùng followup.send
    await interaction.response.defer(ephemeral=True)
    
    try:
        target_user_id = int(user_id)
        target_user = await bot.fetch_user(target_user_id)
        
        sent_count = 0
        for i in range(quantity):
            try:
                # Gửi ping bằng followup.send
                ping_message = await interaction.followup.send(f"{target_user.mention}")
                await asyncio.sleep(0.3)
                
                # Xóa tin nhắn ping
                await ping_message.delete()
                sent_count += 1
                
                if i < quantity - 1:
                    await asyncio.sleep(delay)
                    
            except discord.Forbidden:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Lỗi",
                        description="Bot không có quyền xóa tin nhắn!",
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
                return
            except Exception as e:
                print(f"[ERROR] Lỗi khi ghost ping: {e}")
        
        # Thông báo thành công
        await interaction.followup.send(
            embed=discord.Embed(
                title="✅ Hoàn thành",
                description=f"Đã thực hiện {sent_count}/{quantity} lần ghost ping đến {target_user.mention}",
                color=discord.Color.green()
            ),
            ephemeral=True
        )
        
        # 🔥 LOG SAU KHI HOÀN THÀNH
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/ghostpingv2 userid:{user_id} delay:{delay} quantity:{quantity}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/ghostpingv2 userid:{user_id} delay:{delay} quantity:{quantity}", guild_name, "Slash Command")
        
    except ValueError:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description="User ID không hợp lệ!",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    except discord.NotFound:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description="Không tìm thấy user!",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(
            embed=discord.Embed(
                title="❌ Lỗi",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
        
# Slash Command - DMS
@bot.tree.command(name="dms", description="Gửi tin nhắn DM đến người dùng")
@app_commands.describe(
    user_id="ID của người dùng cần gửi tin nhắn",
    message="Nội dung tin nhắn cần gửi"
)
async def dms(interaction: discord.Interaction, user_id: str, message: str):
    """Slash command gửi DM"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    try:
        target_user_id = int(user_id)
        target_user = await bot.fetch_user(target_user_id)

        try:
            await target_user.send(f"{message}")
            embed = discord.Embed(
                title="✅ Đã gửi tin nhắn",
                description=f"Đã gửi tin nhắn đến {target_user.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Không thể gửi tin nhắn",
                description=f"Không thể gửi tin nhắn đến {target_user.mention}\n\n**Lý do:** User đã chặn DM hoặc bot không có quyền gửi tin nhắn",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

        # 🔥 LOG SAU KHI THỰC HIỆN
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/dms userid:{user_id} message:{message}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/dms userid:{user_id} message:{message}", guild_name, "Slash Command")

    except ValueError:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except discord.NotFound:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không tìm thấy người dùng với ID này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Lỗi không xác định",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

# Spam V1
@bot.tree.command(name="spam", description="spam tin nhắn ở kênh (hoặc dms)")
@app_commands.describe(
    message="Nội dung tin nhắn cần gửi",
    quantity="Số lượng tin nhắn (tối đa 1000)",
    user_id="ID của người dùng cần gửi (để trống nếu gửi ở channel hiện tại)"
)
async def spam(interaction: discord.Interaction, message: str, quantity: int, user_id: str = None):
    """Slash command spam"""
    
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    # Kiểm tra guild bị hạn chế
    if interaction.guild and interaction.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # FIX: Xử lý user_id rỗng
    if user_id is not None and user_id.strip() == "":
        user_id = None
    
    # Kiểm tra giới hạn số lượng
    if quantity > 1000:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Số lượng tin nhắn tối đa là 1000!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if quantity <= 0:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Số lượng tin nhắn phải lớn hơn 0!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Phản hồi ban đầu
    embed = discord.Embed(
        title="⏳ Đang xử lý...",
        description=f"Đang gửi {quantity} tin nhắn...",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

    try:
        sent_count = 0
        
        # Nếu có user_id, gửi tin nhắn cho user
        if user_id:
            try:
                target_user = await bot.fetch_user(int(user_id))
                for i in range(quantity):
                    try:
                        await target_user.send(f"{message}")
                        sent_count += 1
                    except Exception as e:
                        print(f"Lỗi gửi tin nhắn cho user: {e}")
                
                # LOG SAU KHI HOÀN THÀNH - GIỮ NGUYÊN NỘI DUNG NHƯ CŨ
                user = f"{interaction.user.name}#{interaction.user.discriminator}"
                guild_name = interaction.guild.name if interaction.guild else "Direct Message"
                
                # FIX: Chỉ lấy thông tin target_user.name an toàn, không dùng mention trong log
                target_display = f"userid:{user_id}"
                
                # Ghi log command - GIỮ NGUYÊN FORMAT
                log_content = f"/spam message:{message} quantity:{quantity}"
                log_message = log_command(user, log_content, guild_name, "Slash Command")
                await send_dm_notification(user, log_content, guild_name, "Slash Command")
                
                # Thông báo thành công - ở đây vẫn dùng mention vì là embed cho user
                embed = discord.Embed(
                    title="✅ Hoàn thành",
                    description=f"Đã gửi {sent_count}/{quantity} tin nhắn đến {target_user.mention}",
                    color=discord.Color.green()
                )
                await interaction.edit_original_response(embed=embed)
                
            except ValueError:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="User ID không hợp lệ!",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Không tìm thấy user!",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Không thể gửi tin nhắn cho user này!",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed)
        
        # Nếu không có user_id, gửi ở channel hiện tại
        else:
            for i in range(quantity):
                try:
                    await interaction.channel.send(f"{message}")
                    sent_count += 1
                    await asyncio.sleep(0.5)  # Delay 0.5 giây giữa các tin nhắn
                except Exception as e:
                    print(f"Lỗi gửi tin nhắn: {e}")
            
            # LOG SAU KHI HOÀN THÀNH - GIỮ NGUYÊN NỘI DUNG NHƯ CŨ
            user = f"{interaction.user.name}#{interaction.user.discriminator}"
            guild_name = interaction.guild.name if interaction.guild else "Direct Message"
            
            # Ghi log command - GIỮ NGUYÊN FORMAT
            log_content = f"/spam message:{message} quantity:{quantity} (sent: {sent_count}/{quantity})"
            log_message = log_command(user, log_content, guild_name, "Slash Command")
            await send_dm_notification(user, log_content, guild_name, "Slash Command")
            
            # Thông báo thành công
            embed = discord.Embed(
                title="✅ Hoàn thành",
                description=f"Đã gửi {sent_count}/{quantity} tin nhắn trong channel này",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed)
    
    except Exception as e:
        # LOG LỖI - GIỮ NGUYÊN NỘI DUNG NHƯ CŨ
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        
        # FIX: Xử lý target_display an toàn cho log lỗi
        target_display = f"userid:{user_id}" if user_id else ""
        log_content = f"/spam message:{message} quantity:{quantity} {target_display} (ERROR: {str(e)})"
        
        log_message = log_command(user, log_content, guild_name, "Slash Command")
        await send_dm_notification(user, log_content, guild_name, "Slash Command")
        
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.edit_original_response(embed=embed)
        
# Spam
class SpamButton(discord.ui.View):
    def __init__(self, message, user_id=None):
        super().__init__()
        self.message = message
        self.user_id = user_id

    @discord.ui.button(label="Spam", style=discord.ButtonStyle.red, emoji="💥")
    async def spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Defer để có thể dùng followup.send
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Spam qua DM nếu có user_id
            if self.user_id:
                try:
                    target_user_id = int(self.user_id)
                    target_user = await bot.fetch_user(target_user_id)
                    
                    # Spam 5 tin nhắn qua DM
                    for _ in range(5):
                        await target_user.send(f"{self.message}")
                    
                    # Thông báo thành công
                    await interaction.followup.send(
                        f"✅ Đã spam 5 tin nhắn đến {target_user.mention}",
                        ephemeral=True
                    )
                    
                except Exception as e:
                    await interaction.followup.send(
                        f"❌ Lỗi khi spam DM: {str(e)}",
                        ephemeral=True
                    )
                    return
            
            # Spam trong channel hiện tại bằng followup.send
            else:
                # Spam 5 tin nhắn trong channel
                for _ in range(5):
                    await interaction.followup.send(f"{self.message}")
                
                # Thông báo thành công
                await interaction.followup.send(
                    "✅ Đã spam 5 tin nhắn vào kênh",
                    ephemeral=True
                )

            # Log hành động
            user = f"{interaction.user.name}#{interaction.user.discriminator}"
            guild_name = interaction.guild.name if interaction.guild else "Direct Message"
            log_command(user, f"/spamv2 message:{self.message} userid:{self.user_id}", guild_name, "Slash Command")
            await send_dm_notification(user, f"/spamv2 message:{self.message} userid:{self.user_id}", guild_name, "Slash Command")

        except Exception as e:
            await interaction.followup.send(
                f"❌ Lỗi khi spam: {str(e)}",
                ephemeral=True
            )

@bot.tree.command(name="time", description="Xem thời gian hiện tại (UTC+7 - Việt Nam)")
async def time_command(interaction: discord.Interaction):
    current_time = get_utc7_time()

    embed = discord.Embed(
        title="🕐 Thời gian hiện tại",
        description=f"**UTC+7 (Việt Nam)**\n```{current_time.strftime('%H:%M:%S %d/%m/%Y')}```",
        color=discord.Color.gold(),
        timestamp=current_time
    )

    embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
    embed.set_footer(
        text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}",
        icon_url=FOOTER_ICON_URL
    )
    embed.set_thumbnail(url=ICON_URL)

    await interaction.response.send_message(embed=embed, ephemeral=True)
    
# --- Slash command ---
@bot.tree.command(name="help", description="Hiển thị tất cả lệnh có sẵn trong bot")
async def slash_help(interaction: discord.Interaction):
    user = f"{interaction.user.name}#{interaction.user.discriminator}"
    is_admin = is_user_allowed(interaction.user.id)  # kiểm tra có phải admin/whitelist không

    pages = build_help_pages(interaction.user.id, user, is_admin)
    view = HelpView(pages, interaction.user.id)

    await interaction.response.send_message(embed=pages[0], view=view, ephemeral=True)
    # 📌 Sau khi trả lời thì log + DM
    log_command(user, "/help", guild_name, "Slash Command")
    await send_dm_notification(user, "/help", guild_name, "Slash Command")

@bot.tree.command(name="spamv2", description="Spam tin nhắn ở kênh (hoặc DMs,ko cần invite)")
@app_commands.describe(
    message="Nội dung tin nhắn cần gửi",
    user_id="ID của người dùng cần gửi (để trống nếu gửi ở channel hiện tại)"
)
async def spamv2(interaction: discord.Interaction, message: str, user_id: str = None):
    """Slash command spam - Với nút Spam cố định 5 tin nhắn"""
    # Kiểm tra user banned
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    # Kiểm tra guild bị hạn chế
    if interaction.guild and interaction.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Tạo view với nút Spam
    view = SpamButton(message, user_id)
    
    # Embed thông báo (bỏ field "Đích đến")
    embed = discord.Embed(
        title="💥 SPAM TEXT",
        description=f"**Nội dung:** {message}",
        color=discord.Color.red()
    )
    embed.add_field(name="📊 Số lượng", value="5 tin nhắn", inline=True)
    embed.add_field(name="👤 Người yêu cầu", value=interaction.user.mention, inline=True)
    
    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )
    
# LỆNH /say
@bot.tree.command(name="say", description="Làm bot gửi tin nhắn")
@app_commands.describe(
    message="Nội dung tin nhắn cần gửi",
    channel="Kênh để gửi tin nhắn (để trống nếu gửi ở kênh hiện tại)"
)
async def say(interaction: discord.Interaction, message: str, channel: discord.TextChannel = None):
    """Slash command /say - Gửi tin nhắn thay mặt bot"""
    
    # Kiểm tra user bị cấm
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    # Xác định kênh đích
    target_channel = channel or interaction.channel

    try:
        # Phản hồi trước (defer để có thời gian xử lý)
        await interaction.response.defer(ephemeral=True)
        
        # Gửi tin nhắn
        await target_channel.send(message)
        
        # LOG SAU KHI PHẢN HỒI  
        user = f"{interaction.user.name}#{interaction.user.discriminator}"  
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"  
        log_message = log_command(user, f"/say message:{message}", guild_name, "Slash Command")  
        
        # Gửi DM thông báo với Embed  
        await send_dm_notification(user, f"/say message:{message}", guild_name, "Slash Command")  
        
        # Gửi embed xác nhận
        embed = discord.Embed(  
            title="✅ Tin nhắn đã được gửi",  
            description=f"Đã gửi tin nhắn đến {target_channel.mention}",  
            color=discord.Color.green()  
        )  
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except discord.Forbidden:  
        embed = discord.Embed(  
            title="❌ Lỗi",  
            description=f"Bot không có quyền gửi tin nhắn trong {target_channel.mention}!",  
            color=discord.Color.red()  
        )  
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:  
        embed = discord.Embed(  
            title="❌ Lỗi",  
            description=f"Đã xảy ra lỗi: {str(e)}",  
            color=discord.Color.red()  
        )  
        await interaction.followup.send(embed=embed, ephemeral=True)

#Say V2
@bot.tree.command(name="sayv2", description="Làm bot gửi tin nhắn vào channel hiện tại (Ko cần invite)")
@app_commands.describe(
    message="Nội dung tin nhắn cần gửi"
)
async def sayv2(interaction: discord.Interaction, message: str):
    """Slash command /say - Gửi 1 tin nhắn (dùng followup.send)"""
    
    # Kiểm tra user bị cấm
    if is_user_banned(interaction.user.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        # Gửi tin nhắn ngay lập tức bằng followup.send (KHÔNG defer)
        await interaction.response.send_message(
            "🔄 Đang gửi tin nhắn...", 
            ephemeral=True
        )
        
        # Gửi tin nhắn thật bằng followup.send (không ephemeral)
        await interaction.followup.send(message)

        # Log hành động
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_command(user, f"/sayv2 message:{message}", guild_name, "Slash Command")
        await send_dm_notification(user, f"/sayv2 message:{message}", guild_name, "Slash Command")

    except Exception as e:
        await interaction.followup.send(
            f"❌ Lỗi khi gửi tin nhắn: {str(e)}",
            ephemeral=True
        )
        
@bot.tree.command(name="invite", description="Lấy link mời bot vào server")
async def invite(interaction: discord.Interaction):
    try:
        # Kiểm tra user bị cấm
        if is_user_banned(interaction.user.id):
            embed = discord.Embed(
                title="❌ Bị cấm",
                description="Bạn đã bị cấm sử dụng bot này!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log hành động bị cấm
            user = f"{interaction.user.name}#{interaction.user.discriminator}"
            guild_name = interaction.guild.name if interaction.guild else "Direct Message"
            log_message = log_command(user, "/invite", guild_name, "BLOCKED - Banned User")
            return

        await interaction.response.defer(ephemeral=True)

        # Tạo embed
        embed = discord.Embed(
            title="🎉 Mời bot vào server của bạn!",
            description="Nhấn vào link bên dưới để thêm bot vào server",
            color=0x00ff00
        )
        
        # Tạo invite link với các quyền cơ bản
        invite_url = discord.utils.oauth_url(
            bot.user.id,
            permissions=discord.Permissions(
                send_messages=True,
                read_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True,
                use_application_commands=True
            )
        )
        
        embed.add_field(
            name="🔗 Link mời",
            value=f"[Invite Link(User Install)]({invite_url})\n[Invite Bot To Server](https://discord.com/oauth2/authorize?client_id=1410958593041104957&permissions=8&integration_type=0&scope=bot+applications.commands)",
            inline=False
        )
        
        embed.add_field(
            name="📋 Quyền được cấp",
            value="• Admintranistor\n• Slash commands",
            inline=False
        )
        
        if bot.user.avatar:
            embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text="Cảm ơn bạn đã sử dụng bot!")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # LOG SAU KHI PHẢN HỒI THÀNH CÔNG
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_message = log_command(user, "/invite", guild_name, "Slash Command")

    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bot không có quyền gửi tin nhắn!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log lỗi Forbidden
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_message = log_command(user, "/invite", guild_name, "ERROR - Forbidden")
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log lỗi tổng quát
        user = f"{interaction.user.name}#{interaction.user.discriminator}"
        guild_name = interaction.guild.name if interaction.guild else "Direct Message"
        log_message = log_command(user, f"/invite - ERROR: {str(e)}", guild_name, "ERROR - Exception")
                                                                    
# ==================== CÁC LỆNH MỚI TÍCH HỢP ====================

@bot.command()
async def nukeall(ctx):
    """Raid server với kick bot trước"""
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(title="❌ Bị cấm", description="Bạn đã bị cấm sử dụng bot này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(title="❌ Lỗi", description="Bạn không có quyền sử dụng lệnh này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(title="❌ Lỗi", description="Lệnh này không được phép sử dụng trong server này!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    
    # LOG
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_command(user, "?nukeall", guild_name, "Text Command")
    await send_dm_notification(user, "?nukeall", guild_name, "Text Command")
    
    try:
        if not ctx.guild.me.guild_permissions.administrator:
            await ctx.send("❌ Bot cần quyền Administrator!")
            return
        
        try:
            await ctx.message.delete()
        except:
            pass
        
        # BƯỚC 1: KICK TẤT CẢ BOT
        kick_embed = discord.Embed(
            title="🔄 Đang xử lý...",
            description="**Đang kick tất cả bot...**\n\n*Disclaimer: Đây chỉ là mục đích học tập Python*",
            color=discord.Color.orange()
        )
        kick_embed.set_footer(text="Lonely Hub - Educational Purpose Only")
        status_msg = await ctx.send(embed=kick_embed)
        
        kicked_bots = 0
        if ctx.guild.me.guild_permissions.kick_members:
            for member in ctx.guild.members:
                if member.bot and member != ctx.guild.me:  # Không kick chính mình
                    try:
                        await member.kick(reason="NukeAll Command - Educational Purpose")
                        kicked_bots += 1
                        await asyncio.sleep(0.5)
                    except:
                        continue
        
        # BƯỚC 2: TIẾP TỤC NUKE NHƯ CŨ
        await status_msg.edit(embed=discord.Embed(
            title="💥 Bắt đầu Nuke...",
            description=f"Đã kick {kicked_bots} bot\n**Bắt đầu nuke server...**",
            color=discord.Color.red()
        ))
        
        await asyncio.sleep(2)
        await status_msg.delete()
        
        # GỌI HÀM NUKE CŨ
        await raid_server(ctx.guild)
        
    except Exception as e:
        log(f"Error In Nuke Command: {e}")

async def raid_server(guild):
    """Function To Raid (giữ nguyên nội dung chat như cũ)"""
    try:
        log(f"Starting Raid: {guild.name}")
        
        try:
            await guild.edit(name="Raidded By Lonely Hub")
            log("Rename Server Succesfuly!")
        except Exception as e:
            log(f"Error When Rename Server: {e}")
        
        log("Deleting Channel...")
        channel_count = 0
        for channel in list(guild.channels):
            try:
                await channel.delete()
                channel_count += 1
            except Exception as e:
                log(f"Error When Delete Channel: {channel.name}: {e}")
        log(f"Deleted {channel_count} Channel Succesfuly")
        
        log("Creating Channel and send messages...")
        # GIỮ NGUYÊN NỘI DUNG CHAT NHƯ CŨ
        message_content = """@everyone
# Your Server Got Raided By Lonely Hub
# Join Server And Dms Owner To Invite Bot
# Invite: https://discord.gg/2anc7nHw6b"""
        
        msg_count = 0
        channel_create_tasks = []
        
        for i in range(100):
            channel_create_tasks.append(guild.create_text_channel(f"⊹‧₊˚꒰💀꒱・ʀᴀɪᴅᴅᴇᴅ ʙʏ ʟᴏɴᴇʟʏ ʜᴜʙ"))
        
        new_channels = await asyncio.gather(*channel_create_tasks, return_exceptions=True)
        
        successful_channels = []
        for i, channel in enumerate(new_channels):
            if isinstance(channel, discord.TextChannel):
                successful_channels.append(channel)
                log(f"Channel Created {i+1}")
            else:
                log(f"Error When Create Channel {i+1}: {channel}")
        
        log(f"Created {len(successful_channels)} channel Succesfuly")
        
        message_tasks = []
        for channel in successful_channels:
            for i in range(50):
                message_tasks.append(channel.send(message_content))
        
        message_results = await asyncio.gather(*message_tasks, return_exceptions=True)
        
        for result in message_results:
            if not isinstance(result, Exception):
                msg_count += 1
        
        log(f"Succesfully Send {msg_count} Messages")
        log("Raid Completed!")
        
    except Exception as e:
        log(f"Raid Error:: {e}")
        
# Lệnh ?raidall - Spam tất cả kênh với tin nhắn
@bot.command()
async def raidall(ctx):
    """Spam tất cả kênh với tin nhắn"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra quyền
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # LOG TRƯỚC KHI XỬ LÝ
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_message = log_command(user, "?raidall", guild_name, "Text Command")
    
    # Gửi DM thông báo với Embed
    await send_dm_notification(user, "?raidall", guild_name, "Text Command")
    
    try:
        message_content = """# Your Server Got Raided By Lonely Hub
# Join Server And Dms Owner To Invite Bot
# Invite: https://discord.gg/2anc7nHw6b"""
        
        msg_count = 0
        status_msg = await ctx.send("Starting raid all channels...")
        
        # Gửi tin nhắn đến tất cả các kênh
        for channel in ctx.guild.text_channels:
            try:
                if channel.permissions_for(ctx.guild.me).send_messages:
                    await channel.send(message_content)
                    msg_count += 1
                    await asyncio.sleep(0)  # Không delay
            except Exception as e:
                print(f"Lỗi gửi tin nhắn đến {channel.name}: {e}")
        
        await status_msg.delete()
        
        # Thông báo thành công
        embed = discord.Embed(
            title="✅ Hoàn thành",
            description=f"Đã gửi {msg_count} tin nhắn đến tất cả kênh",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Lệnh ?spampingall - Spam ping everyone tất cả kênh
@bot.command()
async def spampingall(ctx):
    """Spam ping everyone tất cả kênh"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra quyền
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # LOG TRƯỚC KHI XỬ LÝ
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_message = log_command(user, "?spampingall", guild_name, "Text Command")
    
    # Gửi DM thông báo với Embed
    await send_dm_notification(user, "?spampingall", guild_name, "Text Command")
    
    try:
        message_content = "@everyone"
        
        msg_count = 0
        status_msg = await ctx.send("Starting spam ping all channels...")
        
        # Gửi tin nhắn đến tất cả các kênh
        for channel in ctx.guild.text_channels:
            try:
                if channel.permissions_for(ctx.guild.me).send_messages and channel.permissions_for(ctx.guild.me).mention_everyone:
                    await channel.send(message_content)
                    msg_count += 1
                    await asyncio.sleep(0)  # Không delay
            except Exception as e:
                print(f"Lỗi gửi tin nhắn đến {channel.name}: {e}")
        
        await status_msg.delete()
        
        # Thông báo thành công
        embed = discord.Embed(
            title="✅ Hoàn thành",
            description=f"Đã gửi {msg_count} tin nhắn ping đến tất cả kênh",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Lệnh ?banalluser - Ban tất cả user trong server
@bot.command()
async def banalluser(ctx):
    """Ban tất cả user trong server"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra quyền
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # LOG TRƯỚC KHI XỬ LÝ
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_message = log_command(user, "?banalluser", guild_name, "Text Command")
    
    # Gửi DM thông báo với Embed
    await send_dm_notification(user, "?banalluser", guild_name, "Text Command")
    
    try:
        if not ctx.guild.me.guild_permissions.ban_members:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bot không có quyền ban members!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        status_msg = await ctx.send("Starting ban all users...")
        banned_count = 0
        
        # Ban tất cả user
        for member in ctx.guild.members:
            try:
                if member != ctx.guild.me and member != ctx.author:
                    await member.ban(reason="Raided by Lonely Hub")
                    banned_count += 1
                    await asyncio.sleep(0)  # Không delay
            except Exception as e:
                print(f"Lỗi ban user {member.name}: {e}")
        
        await status_msg.delete()
        
        # Thông báo thành công
        embed = discord.Embed(
            title="✅ Hoàn thành",
            description=f"Đã ban {banned_count} user",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Lệnh ?purge - Xóa tin nhắn
@bot.command()
async def purge(ctx, quantity: int):
    """Xóa số lượng tin nhắn được chỉ định"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra quyền
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # LOG TRƯỚC KHI XỬ LÝ
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_message = log_command(user, f"?purge {quantity}", guild_name, "Text Command")
    
    # Gửi DM thông báo với Embed
    await send_dm_notification(user, f"?purge {quantity}", guild_name, "Text Command")
    
    try:
        if not ctx.guild.me.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bot không có quyền quản lý tin nhắn!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if quantity <= 0:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Số lượng tin nhắn phải lớn hơn 0!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Xóa tin nhắn
        deleted = await ctx.channel.purge(limit=quantity + 1)  # +1 để xóa cả tin nhắn lệnh
        
        # Thông báo thành công
        embed = discord.Embed(
            title="✅ Hoàn thành",
            description=f"Đã xóa {len(deleted) - 1} tin nhắn",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Lệnh ?purgeallwebhook - Xóa tất cả webhook
@bot.command()
async def purgeallwebhook(ctx):
    """Xóa tất cả webhook trong server"""
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(ctx.author.id):
        embed = discord.Embed(
            title="❌ Bị cấm",
            description="Bạn đã bị cấm sử dụng bot này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra quyền
    if not is_user_allowed(ctx.author.id):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Kiểm tra nếu đang ở guild bị cấm
    if ctx.guild and ctx.guild.id == RESTRICTED_GUILD_ID:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Lệnh này không được phép sử dụng trong server này!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # LOG TRƯỚC KHI XỬ LÝ
    user = f"{ctx.author.name}#{ctx.author.discriminator}"
    guild_name = ctx.guild.name if ctx.guild else "Direct Message"
    log_message = log_command(user, "?purgeallwebhook", guild_name, "Text Command")
    
    # Gửi DM thông báo với Embed
    await send_dm_notification(user, "?purgeallwebhook", guild_name, "Text Command")
    
    try:
        if not ctx.guild.me.guild_permissions.manage_webhooks:
            embed = discord.Embed(
                title="❌ Lỗi",
                description="Bot không có quyền quản lý webhooks!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        status_msg = await ctx.send("Deleting all webhooks...")
        deleted_count = 0
        
        # Xóa tất cả webhook
        for channel in ctx.guild.text_channels:
            try:
                webhooks = await channel.webhooks()
                for webhook in webhooks:
                    await webhook.delete()
                    deleted_count += 1
            except Exception as e:
                print(f"Lỗi xóa webhook trong {channel.name}: {e}")
        
        await status_msg.delete()
        
        # Thông báo thành công
        embed = discord.Embed(
            title="✅ Hoàn thành",
            description=f"Đã xóa {deleted_count} webhook",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ==================== TEXT COMMAND HANDLER ====================

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn từ bot
    if message.author == bot.user:
        return
    
    # Kiểm tra xem user có bị cấm không
    if is_user_banned(message.author.id):
        # Chỉ phản hồi nếu là lệnh
        if message.content.startswith(('!', '?', '.')):
            embed = discord.Embed(
                title="❌ Bị cấm",
                description="Bạn đã bị cấm sử dụng bot này!",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=False)
        return
    
    # Xử lý các lệnh text command
    if message.content.startswith(('!', '?', '.')):
        # Tách lệnh và tham số
        content = message.content[1:]  # Bỏ ký tự prefix đầu tiên
        parts = content.split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # LOG TRƯỚC KHI XỬ LÝ
        user = f"{message.author.name}#{message.author.discriminator}"
        guild_name = message.guild.name if message.guild else "Direct Message"
        log_message = log_command(user, message.content, guild_name, "Text Command")
        
        # Gửi DM thông báo với Embed
        await send_dm_notification(user, message.content, guild_name, "Text Command")
        
        # Xử lý các lệnh text command
        if command == "ping":
            latency = round(bot.latency * 1000)
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Độ trễ: **{latency}ms**\n⏰ Thời gian: **{current_time.strftime('%H:%M:%S %d/%m/%Y')}** (UTC+7)",
                color=discord.Color.green(),
                timestamp=current_time
            )
            embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
            embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)    
            
        elif command == "help":
            pages = build_help_pages(message.author.id, f"{message.author}")
            view = HelpView(pages, message.author.id)
            await message.reply(embed=pages[0], view=view, mention_author=False)

        elif command == "info":
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="🤖 Bot Information",
                description="Bot logging system với UTC+7",
                color=discord.Color.blue(),
                timestamp=current_time
            )
            
            embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
            embed.add_field(name="🕐 Múi giờ", value="UTC+7", inline=True)
            embed.add_field(name="📊 Số server", value=str(len(bot.guilds)), inline=True)
            embed.add_field(name="⚡ Độ trễ", value=f"{round(bot.latency * 1000)}ms", inline=True)
            embed.add_field(name="📝 Logging", value="Text commands & Slash commands", inline=False)
            embed.add_field(name="📨 DM Notification", value=f"Gửi đến {len(ALLOWED_USERS)} user", inline=True)
            embed.add_field(name="👥 User được phép spam", value=str(len(ALLOWED_USERS)), inline=True)
            embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
            embed.set_thumbnail(url=ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)
        
        elif command == "time":
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="🕐 Thời gian hiện tại",
                description=f"**UTC+7 (Việt Nam)**\n```{current_time.strftime('%H:%M:%S %d/%m/%Y')}```",
                color=discord.Color.gold(),
                timestamp=current_time
            )
            
            embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
            embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
            embed.set_thumbnail(url=ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)
        
        elif command == "whitelist":
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="👥 Danh sách User được phép",
                description=get_allowed_users_table(),
                color=discord.Color.purple(),
                timestamp=current_time
            )
            
            embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
            embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
            embed.set_thumbnail(url=ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)
        
        elif command == "premium_command":
            # Kiểm tra quyền
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
                
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="Premium Commands",
                description="List of available premium command",
                color=0x00ffaa,
                timestamp=current_time
            )
            
            # Set author với icon
            embed.set_author(
                name="Lonely Hub Bot",
                icon_url=ICON_URL
            )
            
            # Thêm các lệnh premium
            embed.add_field(
                name="**?nukeall**",
                value=(
                    "Nuke the server with ping everyone\n\n"
                    "**Requirements:** Bot must have permission to create, delete channels, rename servers and ping everyone"
                ),
                inline=False
            )
            
            embed.add_field(
                name="**?raidall**",
                value=(
                    "Raid all channel with ping everyone and message.\n\n"
                    "**Requirements:** Bot must have permission to ping everyone."
                ),
                inline=False
            )
            
            embed.add_field(
                name="**?spampingall**",
                value="Spam ping everyone all channels",
                inline=False
            )
            
            embed.add_field(
                name="**?banalluser**",
                value=(
                    "Ban all user with ultra-speed\n\n"
                    "**Requirements:** The bot needs to have the highest role in the server."
                ),
                inline=False
            )
            
            embed.add_field(
                name="**?purge [quantity]**",
                value=(
                    "Xóa số lượng tin nhắn được chỉ định\n\n"
                    "**Requirements:** Bot must have permission to manage messages."
                ),
                inline=False
            )
            
            embed.add_field(
                name="**?purgeallwebhook**",
                value=(
                    "Xóa tất cả webhook trong server\n\n"
                    "**Requirements:** Bot must have permission to manage webhooks."
                ),
                inline=False
            )
            
            # Set footer với icon
            embed.set_footer(
                text="Lonely Hub Bot",
                icon_url=FOOTER_ICON_URL
            )
            
            # Set thumbnail
            embed.set_thumbnail(url=ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)
        
        elif command == "ghostping":
            # Kiểm tra quyền
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra nếu đang ở guild bị cấm
            if message.guild and message.guild.id == RESTRICTED_GUILD_ID:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Lệnh này không được phép sử dụng trong server này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 1:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!ghostping <user_id> [delay] [quantity]`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            user_id = args[0]
            delay = 0.5
            quantity = 5
            
            # Xử lý tham số tùy chọn
            if len(args) >= 2:
                try:
                    delay = float(args[1])
                except ValueError:
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Delay phải là số!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
            
            if len(args) >= 3:
                try:
                    quantity = int(args[2])
                except ValueError:
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Quantity phải là số nguyên!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
            
            # Kiểm tra giới hạn delay
            if delay < 0.1:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Delay tối thiểu là 0.1 giây!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra giới hạn số lượng
            if quantity > 50:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Số lượng ping tối đa là 50!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            if quantity <= 0:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Số lượng ping phải lớn hơn 0!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Phản hồi ban đầu
            embed = discord.Embed(
                title="⏳ Đang xử lý...",
                description=f"Đang chuẩn bị ghost ping {quantity} lần với delay {delay}s...",
                color=discord.Color.orange()
            )
            processing_msg = await message.reply(embed=embed, mention_author=False)
            
            try:
                # Chuyển đổi user_id sang integer
                target_user_id = int(user_id)
                
                # Lấy thông tin user
                target_user = await bot.fetch_user(target_user_id)
                
                # Thực hiện ghost ping
                sent_count = 0
                for i in range(quantity):
                    try:
                        # Gửi tin nhắn ping
                        ping_message = await message.channel.send(f"{target_user.mention}")
                        await asyncio.sleep(0.5)  # Đợi 0.5 giây
                        
                        # Xóa tin nhắn
                        await ping_message.delete()
                        sent_count += 1
                        
                        # Đợi delay (trừ đi 0.5 giây đã đợi)
                        remaining_delay = max(0, delay - 0.5)
                        if i < quantity - 1 and remaining_delay > 0:  # Không đợi sau lần ping cuối
                            await asyncio.sleep(remaining_delay)
                            
                    except discord.Forbidden:
                        embed = discord.Embed(
                            title="❌ Lỗi",
                            description="Bot không có quyền xóa tin nhắn!",
                            color=discord.Color.red()
                        )
                        await processing_msg.edit(embed=embed)
                        return
                    except Exception as e:
                        print(f"Lỗi khi ghost ping: {e}")
                
                # Thông báo thành công
                embed = discord.Embed(
                    title="✅ Hoàn thành",
                    description=f"Đã thực hiện {sent_count}/{quantity} lần ghost ping đến {target_user.mention}",
                    color=discord.Color.green()
                )
                await processing_msg.edit(embed=embed)
                
            except ValueError:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="User ID không hợp lệ!",
                    color=discord.Color.red()
                )
                await processing_msg.edit(embed=embed)
            except discord.NotFound:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Không tìm thấy user!",
                    color=discord.Color.red()
                )
                await processing_msg.edit(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await processing_msg.edit(embed=embed)
        
        elif command == "dms":
            # Kiểm tra quyền
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 2:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!dms <user_id> <message>`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            user_id = args[0]
            dm_message = " ".join(args[1:])
            
            try:
                # Chuyển đổi user_id sang integer
                target_user_id = int(user_id)
                
                # Lấy thông tin user
                target_user = await bot.fetch_user(target_user_id)
                
                # Thử gửi tin nhắn
                try:
                    await target_user.send(f"{dm_message}")
                    
                    # Thông báo thành công
                    embed = discord.Embed(
                        title="✅ Đã gửi tin nhắn",
                        description=f"Đã gửi tin nhắn đến {target_user.mention}",
                        color=discord.Color.green()
                        )
                    await message.reply(embed=embed, mention_author=False)
                    
                except discord.Forbidden:
                    # Nếu không gửi được, gửi thông báo lỗi cho người dùng
                    error_embed = discord.Embed(
                        title="❌ Không thể gửi tin nhắn",
                        description=f"Không thể gửi tin nhắn đến {target_user.mention}\n\n**Lý do:** User đã chặn DM hoặc bot không có quyền gửi tin nhắn",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=error_embed, mention_author=False)
                    
                except Exception as e:
                    # Xử lý các lỗi khác
                    error_embed = discord.Embed(
                        title="❌ Lỗi khi gửi tin nhắn",
                        description=f"Đã xảy ra lỗi: {str(e)}",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=error_embed, mention_author=False)
                    
            except ValueError:
                # User ID không hợp lệ
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                
            except discord.NotFound:
                # Không tìm thấy user
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Không tìm thấy người dùng với ID này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                
            except Exception as e:
                # Lỗi khác
                error_embed = discord.Embed(
                    title="❌ Lỗi không xác định",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await message.reply(embed=error_embed, mention_author=False)
        
        elif command == "spam":
            # Kiểm tra quyền sử dụng lệnh
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra nếu đang ở guild bị cấm
            if message.guild and message.guild.id == RESTRICTED_GUILD_ID:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Lệnh này không được phép sử dụng trong server này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 2:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!spam <message> <quantity> [user_id]`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            spam_message = args[0]
            
            try:
                quantity = int(args[1])
            except ValueError:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Quantity phải là số nguyên!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            user_id = args[2] if len(args) >= 3 else None
            
            # Kiểm tra giới hạn số lượng
            if quantity > 1000:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Số lượng tin nhắn tối đa là 1000!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            if quantity <= 0:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Số lượng tin nhắn phải lớn hơn 0!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Phản hồi ban đầu
            embed = discord.Embed(
                title="⏳ Đang xử lý...",
                description=f"Đang gửi {quantity} tin nhắn...",
                color=discord.Color.orange()
            )
            processing_msg = await message.reply(embed=embed, mention_author=False)
            
            try:
                sent_count = 0
                
                # Nếu có user_id, gửi tin nhắn cho user
                if user_id:
                    try:
                        target_user = await bot.fetch_user(int(user_id))
                        for i in range(quantity):
                            try:
                                await target_user.send(f"{spam_message}")
                                sent_count += 1
                                await asyncio.sleep(0.5)  # Delay 0.5 giây giữa các tin nhắn
                            except Exception as e:
                                print(f"Lỗi gửi tin nhắn cho user: {e}")
                        
                        # Thông báo thành công
                        embed = discord.Embed(
                            title="✅ Hoàn thành",
                            description=f"Đã gửi {quantity} tin nhắn đến {target_user.mention}",
                            color=discord.Color.green()
                        )
                        await processing_msg.edit(embed=embed)
                        
                    except ValueError:
                        embed = discord.Embed(
                            title="❌ Lỗi",
                            description="User ID không hợp lệ!",
                            color=discord.Color.red()
                        )
                        await processing_msg.edit(embed=embed)
                    except discord.NotFound:
                        embed = discord.Embed(
                            title="❌ Lỗi",
                            description="Không tìm thấy user!",
                            color=discord.Color.red()
                        )
                        await processing_msg.edit(embed=embed)
                    except discord.Forbidden:
                        embed = discord.Embed(
                            title="❌ Lỗi",
                            description="Không thể gửi tin nhắn cho user này!",
                            color=discord.Color.red()
                        )
                        await processing_msg.edit(embed=embed)
                
                # Nếu không có user_id, gửi ở channel hiện tại
                else:
                    for i in range(quantity):
                        try:
                            await message.channel.send(f"{spam_message}")
                            sent_count += 1
                            await asyncio.sleep(0.5)  # Delay 0.5 giây giữa các tin nhắn
                        except Exception as e:
                            print(f"Lỗi gửi tin nhắn: {e}")
                    
                    # Thông báo thành công
                    embed = discord.Embed(
                        title="✅ Hoàn thành",
                        description=f"Đã gửi {quantity} tin nhắn vào kênh",
                        color=discord.Color.green()
                    )
                    await processing_msg.edit(embed=embed)
                    
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await processing_msg.edit(embed=embed)
        
        elif command == "say":
            # Kiểm tra quyền
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 1:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!say <message>`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            say_message = " ".join(args)
            
            try:
                # Gửi tin nhắn
                await message.channel.send(say_message)
                
                # Xóa tin nhắn lệnh của user
                try:
                    await message.delete()
                except:
                    pass  # Không xóa được cũng không sao
                
            except discord.Forbidden:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bot không có quyền gửi tin nhắn trong kênh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)

        # Xử lý lệnh ?bancmd
        elif command == "bancmd":
            # Kiểm tra quyền admin
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 2:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!bancmd <user_id> <reason>`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            user_id = args[0]
            reason = " ".join(args[1:])
            
            try:
                # Chuyển đổi user_id sang integer
                target_user_id = int(user_id)
                
                # Kiểm tra xem có tự cấm chính mình không
                if target_user_id == message.author.id:
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Bạn không thể tự cấm chính mình!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
                
                # Kiểm tra xem có cấm admin khác không
                if target_user_id in ALLOWED_USERS:
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Bạn không thể cấm một admin khác!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
                
                # Kiểm tra xem user đã bị cấm chưa
                if is_user_banned(target_user_id):
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Người dùng này đã bị cấm trước đó!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
                
                # Lấy thời gian hiện tại
                current_time = get_utc7_time()
                time_str = current_time.strftime("%H:%M:%S %d/%m/%Y")
                
                # Thêm vào danh sách cấm
                BANNED_USERS[target_user_id] = {
                    "reason": reason,
                    "banned_by": f"{message.author.name}#{message.author.discriminator}",
                    "banned_at": time_str
                }
                
                # LOG
                user = f"{message.author.name}#{message.author.discriminator}"
                guild_name = message.guild.name if message.guild else "Direct Message"
                log_message = log_command(user, f"?bancmd userid:{user_id} reason:{reason}", guild_name, "Text Command")
                
                # Gửi DM thông báo với Embed
                await send_dm_notification(user, f"?bancmd userid:{user_id} reason:{reason}", guild_name, "Text Command")
                
                # Thông báo thành công
                embed = discord.Embed(
                    title="✅ Đã cấm người dùng",
                    description=f"Đã cấm người dùng với ID {user_id} sử dụng bot.\n**Lý do:** {reason}",
                    color=discord.Color.green()
                )
                await message.reply(embed=embed, mention_author=False)
                
            except ValueError:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ Lỗi không xác định",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await message.reply(embed=error_embed, mention_author=False)

        # Xử lý lệnh ?unbancmd
        elif command == "unbancmd":
            # Kiểm tra quyền admin
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Kiểm tra tham số
            if len(args) < 2:
                embed = discord.Embed(
                    title="❌ Thiếu tham số",
                    description="Cú pháp: `!unbancmd <user_id> <reason>`",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            user_id = args[0]
            reason = " ".join(args[1:])
            
            try:
                # Chuyển đổi user_id sang integer
                target_user_id = int(user_id)
                
                # Kiểm tra xem user có bị cấm không
                if not is_user_banned(target_user_id):
                    embed = discord.Embed(
                        title="❌ Lỗi",
                        description="Người dùng này không bị cấm!",
                        color=discord.Color.red()
                    )
                    await message.reply(embed=embed, mention_author=False)
                    return
                
                # Xóa khỏi danh sách cấm
                del BANNED_USERS[target_user_id]
                
                # LOG
                user = f"{message.author.name}#{message.author.discriminator}"
                guild_name = message.guild.name if message.guild else "Direct Message"
                log_message = log_command(user, f"?unbancmd userid:{user_id} reason:{reason}", guild_name, "Text Command")
                
                # Gửi DM thông báo với Embed
                await send_dm_notification(user, f"?unbancmd userid:{user_id} reason:{reason}", guild_name, "Text Command")
                
                # Thông báo thành công
                embed = discord.Embed(
                    title="✅ Đã gỡ cấm người dùng",
                    description=f"Đã gỡ cấm người dùng với ID {user_id}.\n**Lý do:** {reason}",
                    color=discord.Color.green()
                )
                await message.reply(embed=embed, mention_author=False)
                
            except ValueError:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="User ID không hợp lệ! Vui lòng nhập ID đúng định dạng số.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ Lỗi không xác định",
                    description=f"Đã xảy ra lỗi: {str(e)}",
                    color=discord.Color.red()
                )
                await message.reply(embed=error_embed, mention_author=False)

        # Xử lý lệnh ?bancmdlist
        elif command == "bancmdlist":
            # Kiểm tra quyền admin
            if not is_user_allowed(message.author.id):
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="Bạn không có quyền sử dụng lệnh này!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=False)
                return
            
            # LOG
            user = f"{message.author.name}#{message.author.discriminator}"
            guild_name = message.guild.name if message.guild else "Direct Message"
            log_message = log_command(user, "?bancmdlist", guild_name, "Text Command")
            
            # Gửi DM thông báo với Embed
            await send_dm_notification(user, "?bancmdlist", guild_name, "Text Command")
            
            current_time = get_utc7_time()
            
            embed = discord.Embed(
                title="🔨 Danh sách người dùng bị cấm",
                description=get_banned_users_table(),
                color=discord.Color.orange(),
                timestamp=current_time
            )
            
            embed.set_author(name="Lonely Hub", icon_url=ICON_URL)
            embed.set_footer(text=f"Lonely Hub | {current_time.strftime('%H:%M:%S %d/%m/%Y')}", icon_url=FOOTER_ICON_URL)
            embed.set_thumbnail(url=ICON_URL)
            
            await message.reply(embed=embed, mention_author=False)
        
        else:
            # Lệnh không xác định
            embed = discord.Embed(
                title="❌ Lệnh không tồn tại",
                description="Sử dụng `!help` để xem danh sách lệnh",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=False)
    
    # Xử lý auto response
    elif any(keyword in message.content.lower() for keyword in ["client", "executor", "executors"]):
        embed = discord.Embed(
            title="🤖 Danh sách Client",
            description=(
                "> # Android\n"
                "• [Delta X](https://deltaexploits.gg/delta-executor-android)\n"
                "• [Code X](https://codex.lol/android)\n"
                "• [Arceus X Global](https://spdmteam.com/index?os=android)\n"
                "• [Arceus X VNG](https://spdmteam.com/index?os=android_vng)\n"
                "• [Krnl](https://krnl.cat/downloads)\n"
                "• [Ronix VNG](https://ronixstudios.com/#/download?platform=vietnam)\n"
                "• [Ronix](https://ronixstudios.com/#/download?platform=android)\n"
                "> # IOS\n"
                "• [Delta X](https://deltaexploits.gg/delta-executor-ios)\n"
                "• [Krnl](https://krnl.cat/downloads)\n"
                "• [Arceus X](https://spdmteam.com/index?os=ios)\n"
                "• [Code X](https://codex.lol/ios)\n"
                "> # Mac OS\n"
                "• [Ronix](https://ronixstudios.com/#/download?platform=macos)\n"
                "> # Windows\n"
                "• [Volcano](https://volcano.wtf)\n"
                "• [Velocity](https://discord.gg/velocityide)\n"
                "• [Swift](https://getswift.vip)\n"
                "Các client vng như delta thì sẽ cập nhật sau tại kênh client nhé!"
            ),
            color=discord.Color.blue()
        )
        await message.reply(embed=embed, mention_author=False)
    
    elif "luật" in message.content.lower():
        embed = discord.Embed(
            title="⚖️ Luật Server",
            description=(
                "**Để xem luật server, vui lòng:**\n"
                "1. Vào kênh <#1409785046075965460>\n"
                "2. Đọc kỹ các điều khoản và quy định\n"
                "3. Tuân thủ luật để tránh bị ban\n\n"
                "**📌 Lưu ý quan trọng:**\n"
                "• Không spam, flood chat\n"
                "• Không gây war, toxic\n"
                "• Tôn trọng lẫn nhau và admin"
                "• Không quảng cáo shop,server khác khi chưa được phép"
            ),
            color=discord.Color.gold()
        )
        await message.reply(embed=embed, mention_author=False)
    
    elif any(keyword in message.content.lower() for keyword in ["máy ảo", "cách nhận máy ảo"]):
        embed = discord.Embed(
            title="🖥️ Nhận Máy Ảo",
            description=(
                "**Để nhận máy ảo, vui lòng:**\n"
                "1. Vào kênh <#1409792064438403154>\n"
                "Có 2 bot để bạn nhận máy ảo là hanami và king\n\n"
                "Hanami thì bạn nhập lệnh `/gethcoin` vượt link nhận coin rồi thì nhập lệnh "
                "`/getredfinger` hoặc máy ảo mà bạn muốn nhận\n\n"
                "King thì bạn nhập `/nhiemvu` hoặc `!nv` vượt link nhận điểm r nhận máy ảo thôi "
                "bạn có thể nhập `/account` để xem King còn lại bao nhiêu máy ảo\n"
                "3. Enjoy:)\n\n"
                "**📋 Yêu cầu:**\n"
                "• Không lạm dụng bot\n"
                "• Đã đọc và đồng ý với luật server\n"
                "• Chỉ dùng bot tại kênh bot\n\n"
            ),
            color=discord.Color.green()
        )
        await message.reply(embed=embed, mention_author=False)
    
    # Tiếp tục xử lý các lệnh khác
    await bot.process_commands(message)


# Chạy bot (THÊM TOKEN CỦA BẠN VÀO ĐÂY)
if __name__ == "__main__":
    
    token = BotToken

    while True:
        if not token:
            token = input(Fore.CYAN + "[Info] " + Fore.WHITE + "Vui lòng nhập token bot Discord: " + Style.RESET_ALL).strip()
        
        try:
            print(Fore.CYAN + "[Info] " + Fore.WHITE + "Đang khởi động bot..." + Style.RESET_ALL)
            bot.run(token)
            break  # nếu chạy thành công thì thoát loop
        except Exception as e:
            print(Fore.RED + f"[Error] Lỗi khi khởi động bot: {e}" + Style.RESET_ALL)
            print(Fore.YELLOW + "[Debug] Token không hợp lệ hoặc có lỗi. Vui lòng nhập lại." + Style.RESET_ALL)
            token = None  # reset token để yêu cầu nhập lại