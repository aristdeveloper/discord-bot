import discord
from discord import app_commands
import json
import os

TOKEN = os.getenv("TOKEN")
OWNER_ID = 1466843004458238166

intents = discord.Intents.default()
intents.members = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

DATA_FILE = "database.json"

# ===== Загрузка базы =====
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"balances": {}, "nicknames": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
balances = data["balances"]
nicknames = data["nicknames"]

# ===== Проверки =====
def is_registered(user_id):
    return str(user_id) in nicknames

def get_emoji(guild):
    emoji = discord.utils.get(guild.emojis, name="brotherhoodcoin")
    return str(emoji) if emoji else "🪙"

# ===== Синхронизация =====
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Бот запущен как {bot.user}")

# ================= INFO =================
@tree.command(name="info", description="Информация о командах бота")
async def info(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📖 Информация о системе Brotherhood",
        description="Ниже указаны все доступные команды.",
        color=discord.Color.blurple()
    )

    embed.add_field(name="📝 /register", value="Регистрация в системе.", inline=False)
    embed.add_field(name="🔄 /rename", value="Смена своего ника.", inline=False)
    embed.add_field(name="💰 /balance", value="Посмотреть баланс.", inline=False)
    embed.add_field(name="🏆 /top", value="Топ богатейших игроков.", inline=False)
    embed.add_field(name="💸 /give", value="(Owner) Начислить валюту.", inline=False)
    embed.add_field(name="🗺️ /add", value="(Owner) Начислить валюту (карта).", inline=False)
    embed.add_field(name="➖ /remove", value="(Owner) Списать валюту.", inline=False)
    embed.add_field(name="🛠️ /changenickname", value="(Owner) Изменить ник любому игроку.", inline=False)

    await interaction.response.send_message(embed=embed)

# ================= REGISTER =================
@tree.command(name="register", description="Зарегистрироваться")
@app_commands.describe(nickname="Ваш ник в Brofist.io")
async def register(interaction: discord.Interaction, nickname: str):

    user_id = str(interaction.user.id)

    if is_registered(user_id):
        await interaction.response.send_message("❌ Вы уже зарегистрированы.", ephemeral=True)
        return

    if nickname.lower() in [n.lower() for n in nicknames.values()]:
        await interaction.response.send_message("❌ Этот ник уже занят.", ephemeral=True)
        return

    nicknames[user_id] = nickname
    balances[user_id] = 0
    save_data()

    await interaction.response.send_message(
        f"✅ Вы зарегистрированы под ником **{nickname}**."
    )

# ================= RENAME =================
@tree.command(name="rename", description="Изменить свой ник")
@app_commands.describe(new_nickname="Новый ник")
async def rename(interaction: discord.Interaction, new_nickname: str):

    user_id = str(interaction.user.id)

    if not is_registered(user_id):
        await interaction.response.send_message("❌ Сначала используйте `/register`.", ephemeral=True)
        return

    if new_nickname.lower() in [n.lower() for n in nicknames.values()]:
        await interaction.response.send_message("❌ Этот ник уже занят.", ephemeral=True)
        return

    old = nicknames[user_id]
    nicknames[user_id] = new_nickname
    save_data()

    await interaction.response.send_message(
        f"🔄 Ник изменён: **{old}** ➜ **{new_nickname}**"
    )

# ================= CHANGE NICKNAME (OWNER ONLY) =================
@tree.command(name="changenickname", description="(Owner) Изменить ник игрока")
@app_commands.describe(member="Кому изменить ник", new_nickname="Новый ник")
async def changenickname(interaction: discord.Interaction, member: discord.Member, new_nickname: str):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Эта команда доступна только владельцу.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    if new_nickname.lower() in [n.lower() for n in nicknames.values()]:
        await interaction.response.send_message("❌ Этот ник уже занят.", ephemeral=True)
        return

    user_id = str(member.id)
    old_nick = nicknames[user_id]
    nicknames[user_id] = new_nickname
    save_data()

    await interaction.response.send_message(
        f"🛠️ Ник пользователя {member.mention} изменён:\n"
        f"**{old_nick}** ➜ **{new_nickname}**",
        ephemeral=True
    )

# ================= BALANCE =================
@tree.command(name="balance", description="Посмотреть баланс")
async def balance(interaction: discord.Interaction):

    user_id = str(interaction.user.id)

    if not is_registered(user_id):
        await interaction.response.send_message("❌ Сначала используйте `/register`.", ephemeral=True)
        return

    amount = balances.get(user_id, 0)
    nickname = nicknames[user_id]
    emoji = get_emoji(interaction.guild)

    embed = discord.Embed(title="💰 Профиль", color=discord.Color.gold())
    embed.add_field(name="🎮 Ник", value=nickname, inline=False)
    embed.add_field(name="💎 Баланс", value=f"{amount} {emoji}", inline=False)

    await interaction.response.send_message(embed=embed)

# ================= GIVE =================
@tree.command(name="give", description="(Owner) Начислить валюту")
@app_commands.describe(member="Кому", amount="Сколько")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Только владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    balances[str(member.id)] += amount
    save_data()

    await interaction.response.send_message(
        f"💸 {member.mention} получил {amount} {get_emoji(interaction.guild)}"
    )

# ================= ADD =================
@tree.command(name="add", description="(Owner) Карта одобрена")
@app_commands.describe(member="Кому", amount="Сколько")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Только владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    balances[str(member.id)] += amount
    save_data()

    embed = discord.Embed(
        title="🗺️ Карта одобрена!",
        description=f"{member.mention} получил **{amount}** {get_emoji(interaction.guild)}",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ================= REMOVE =================
@tree.command(name="remove", description="(Owner) Списать валюту")
@app_commands.describe(member="У кого", amount="Сколько")
async def remove(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Только владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    if balances[str(member.id)] < amount:
        await interaction.response.send_message("⚠ Недостаточно средств.", ephemeral=True)
        return

    balances[str(member.id)] -= amount
    save_data()

    await interaction.response.send_message(
        f"➖ У {member.mention} списано {amount} {get_emoji(interaction.guild)}"
    )

# ================= TOP =================
@tree.command(name="top", description="Топ игроков")
async def top(interaction: discord.Interaction):

    if not balances:
        await interaction.response.send_message("📉 Нет данных.")
        return

    emoji = get_emoji(interaction.guild)
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    text = ""
    for i, (user_id, amount) in enumerate(sorted_balances[:10], start=1):
        nickname = nicknames.get(user_id, "Unknown")
        text += f"{i}. {nickname} — {amount} {emoji}\n"

    embed = discord.Embed(title="🏆 Топ игроков", description=text, color=discord.Color.purple())
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
