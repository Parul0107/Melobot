from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "alive 👑"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
import os
import discord
from discord import app_commands
import requests
import random
import re
import asyncio
import time

# =========================
# 🔑 PUT NEW KEYS HERE
# =========================
DISCORD_TOKEN = "MTQ4ODc3NjM3NDMwMTg4NDQxNw.G6kQrE.8D0Apu9czBtdo8Qolw9LO7eu_niVHRbpOf9U_4"
OPENROUTER_API_KEY = "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"

# =========================
# 👑 OPTIONAL: YOUR USER ID
# =========================
QUEEN_USER_ID = None

# =========================
# ⚙️ DISCORD SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# =========================
# ⏱️ COOLDOWN
# =========================
cooldown = {}
COOLDOWN_TIME = 6

# =========================
# 🎭 MOODS
# =========================
GREETING_MOODS = [
    "playful",
    "teasing",
    "warm",
    "chaotic-fun",
    "slightly savage",
    "cute",
    "bubbly"
]

# =========================
# 🧠 GREETING DETECTOR
# =========================
def is_greeting(message: str) -> bool:
    msg = message.lower().strip()

    msg = re.sub(r"[^\w\s]", "", msg)
    msg = re.sub(r"\s+", " ", msg).strip()

    if len(msg.split()) > 6:
        return False

    greeting_patterns = [
        r"^hi+$",
        r"^he+y+$",
        r"^hel+o+$",
        r"^hel+lo+$",
        r"^yo+$",
        r"^sup+$",
        r"^wass?up+$",
        r"^hola+$",
        r"^namaste+$",
        r"^good morning+$",
        r"^good evening+$",
        r"^good night+$",
        r"^gm+$",
        r"^gn+$",
    ]

    for pattern in greeting_patterns:
        if re.match(pattern, msg):
            return True

    words = msg.split()
    if len(words) <= 3:
        common_words = {
            "hi", "hii", "hiii", "hiiii",
            "hey", "heyy", "heyyy",
            "hello", "helloo", "hellooo", "helo",
            "yo", "yoo", "sup", "wassup", "hola", "namaste",
            "gm", "gn"
        }
        if any(word in common_words for word in words):
            return True

    return False

# =========================
# 🌐 LANGUAGE DETECTION
# =========================
def detect_language_style(text):
    text_lower = text.lower()

    hindi_words = [
        "kya", "hai", "nahi", "kyu", "kaise", "haan", "bhai",
        "acha", "theek", "tu", "tum", "mai", "mera", "teri",
        "chal", "kar", "raha", "rahi", "kyun", "abhi"
    ]

    if re.search(r'[\u0900-\u097F]', text):
        return "hindi"

    hindi_score = sum(1 for word in hindi_words if word in text_lower)

    if hindi_score >= 2:
        return "hinglish"

    return "english"

# =========================
# 🤖 AI CORE
# =========================
def ai_reply(user_text: str, mode: str, author_name: str = "user") -> str:
    lang = detect_language_style(user_text)

    if mode == "greeting":
        system_prompt = f"""
You are MeloBot.
Avoid mentioning mood
Reply like a fun cute Discord human in 1-2 lines, use emoticons.
Detected language: {lang}
"""
    elif mode == "normal":
        system_prompt = f"""
You are MeloBot.
Be witty, cute, natural, reply in 1-2 lines.
Detected language: {lang}
"""
    elif mode == "roast_message":
        system_prompt = f"""
Roast the message badly.
Be witty, sarcastic, cool, funny, offensive, savage,  reply in 1-2 lines, use emoticons.
Detected language: {lang}
"""
    elif mode == "praise_message":
        system_prompt = f"""
Praise the message.
Be witty, sweet, cool, lovely, intellectual, reply in 1-2 line, use emoticons.
Detected language: {lang}
"""
    elif mode == "roast_user":
        system_prompt = f"""
Roast the user badly.
Be witty, personal, contexual, savage, brutal, reply in 1-2 lines, use emoticons.
Detected language: {lang}
"""
    else:
        system_prompt = "Reply naturally."

    data = {
        "model": "openrouter/auto",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        print("RAW RESPONSE:", response.text)

        if response.status_code != 200:
            return random.choice([
                "dimag hang ho gaya 😭",
                "system soch raha hai 💭",
                "glitch ho gaya 😵‍💫",
            ])

        json_data = response.json()

        if "choices" not in json_data or len(json_data["choices"]) == 0:
            return "kuch gadbad hai 😭"

        content = json_data["choices"][0]["message"]["content"].strip()

        content = re.sub(r"#\w+", "", content)
        content = content.replace("#", "")
        content = re.sub(r"\bhashtag[s]?\b", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\s+", " ", content).strip()

        return content[:500]

    except Exception as e:
        print("ERROR:", e)
        return random.choice([
            "system hil gaya 😭",
            "brain band ho gaya 💀",
            "retry kar 😵‍💫",
        ])

# =========================
# 👑 SPECIAL TREATMENT
# =========================
def queenify_reply(reply: str, user_id: int) -> str:
    if QUEEN_USER_ID is not None and user_id == QUEEN_USER_ID:
        return "👑 " + reply
    return reply

# =========================
# 🚀 READY
# =========================
@client.event
async def on_ready():
    await tree.sync()
    print(f"{client.user} is online!")

# =========================
# 💬 MESSAGE HANDLER
# =========================
@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    msg = message.content.strip()
    msg_lower = msg.lower()
    user_id = message.author.id
    now = time.time()

    greeting = is_greeting(msg)
    mention_trigger = client.user.mentioned_in(message)
    name_trigger = "melo" in msg_lower

    if greeting or mention_trigger or name_trigger:
        if user_id in cooldown and now - cooldown[user_id] < COOLDOWN_TIME:
            return

        cooldown[user_id] = now

        mode = "greeting" if greeting else "normal"
        mood = random.choice(GREETING_MOODS)

        ai_input = f"[mood={mood}] {msg}"

        async with message.channel.typing():
            await asyncio.sleep(random.uniform(0.6, 1.4))

            reply = ai_reply(ai_input, mode=mode, author_name=message.author.display_name)
            reply = queenify_reply(reply, user_id)

            await message.reply(reply, mention_author=False)

# =========================
# 🔥 CONTEXT MENU
# =========================
@tree.context_menu(name="🔥 Roast this message")
async def roast_message(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer()
    result = ai_reply(message.content, "roast_message")
    await interaction.followup.send(result)

@tree.context_menu(name="✨ Praise this message")
async def praise_message(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer()
    result = ai_reply(message.content, "praise_message")
    await interaction.followup.send(result)

# =========================
# 💀 SLASH COMMAND
# =========================
@tree.command(name="roast", description="Roast a user")
@app_commands.describe(user="User to roast")
async def roast_user(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.defer()
    result = ai_reply(user.display_name, "roast_user")
    await interaction.followup.send(f"{user.mention} {result}")

# =========================
# ▶️ RUN
# =========================
keep_alive()
client.run(DISCORD_TOKEN)
