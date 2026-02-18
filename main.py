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
        description="Ниже указаны все доступные команды и их назначение.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📝 /register",
        value="Регистрация в системе.\n"
              "Используется игроками для создания профиля и привязки ника из Brofist.io.\n"
              "Без регистрации пользоваться экономикой нельзя.",
        inline=False
    )

    embed.add_field(
        name="🔄 /rename",
        value="Смена игрового ника.\n"
              "Доступно только зарегистрированным пользователям.\n"
              "Нельзя выбрать уже занятый ник.",
        inline=False
    )

    embed.add_field(
        name="💰 /balance",
        value="Показывает ваш профиль и баланс валюты.\n"
              "Доступно только зарегистрированным игрокам.",
        inline=False
    )

    embed.add_field(
        name="🏆 /top",
        value="Отображает топ самых богатых игроков сервера.\n"
              "Доступно зарегистрированным пользователям.",
        inline=False
    )

    embed.add_field(
        name="💸 /give",
        value="Начисление валюты игроку.\n"
              "⚠ Доступно только владельцу бота.",
        inline=False
    )

    embed.add_field(
        name="🗺️ /add",
        value="Начисление валюты с текстом 'карта одобрена'.\n"
              "⚠ Доступно только владельцу бота.",
        inline=False
    )

    embed.add_field(
        name="➖ /remove",
        value="Списание валюты у игрока.\n"
              "⚠ Доступно только владельцу бота.",
        inline=False
    )

    embed.set_footer(text="Экономическая система Brotherhood • Brofist.io")

    await interaction.response.send_message(embed=embed)

# ================= REGISTER =================
@tree.command(name="register", description="Зарегистрироваться в системе")
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

    embed = discord.Embed(
        title="✅ Регистрация успешна!",
        description=f"Вы зарегистрированы под ником **{nickname}**.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ================= RENAME =================
@tree.command(name="rename", description="Изменить игровой ник")
@app_commands.describe(new_nickname="Новый никнейм")
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

    embed = discord.Embed(
        title="🔄 Ник изменён",
        description=f"**{old}** ➜ **{new_nickname}**",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

# ================= BALANCE =================
@tree.command(name="balance", description="Посмотреть баланс")
async def balance(interaction: discord.Interaction):

    user_id = str(interaction.user.id)

    if not is_registered(user_id):
        await interaction.response.send_message("❌ Сначала используйте `/register`.", ephemeral=True)
        return

    amount = balances.get(user_id, 0)
    emoji = get_emoji(interaction.guild)
    nickname = nicknames[user_id]

    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    position = next((i+1 for i, v in enumerate(sorted_balances) if v[0] == user_id), "—")

    embed = discord.Embed(
        title="💰 Профиль игрока",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(name="🎮 Ник", value=nickname, inline=False)
    embed.add_field(name="💎 Баланс", value=f"{amount} {emoji}", inline=True)
    embed.add_field(name="🏆 Место в топе", value=f"#{position}", inline=True)
    embed.add_field(name="🆔 Discord ID", value=interaction.user.id, inline=False)

    embed.set_footer(text="Экономическая система Brotherhood")

    await interaction.response.send_message(embed=embed)

# ================= GIVE =================
@tree.command(name="give", description="Начислить валюту")
@app_commands.describe(member="Кому", amount="Сколько")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    user_id = str(member.id)
    balances[user_id] += amount
    save_data()

    emoji = get_emoji(interaction.guild)
    nickname = nicknames[user_id]

    embed = discord.Embed(
        title="💸 Начисление средств",
        description=f"Игрок **{nickname}** получил **{amount}** {emoji}.\n\n💰 Проверить баланс можно командой `/balance`.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

# ================= ADD =================
@tree.command(name="add", description="Начислить валюту (карта одобрена)")
@app_commands.describe(member="Кому", amount="Сколько")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    user_id = str(member.id)
    balances[user_id] += amount
    save_data()

    emoji = get_emoji(interaction.guild)
    nickname = nicknames[user_id]

    embed = discord.Embed(
        title="🗺️ Карта одобрена!",
        description=f"🎉 Поздравляем, **{nickname}**!\n\nВаша карта была успешно одобрена.\nНа баланс зачислено **{amount}** {emoji}.\n\n💰 Просмотреть баланс можно командой `/balance`.",
        color=discord.Color.green()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# ================= REMOVE =================
@tree.command(name="remove", description="Списать валюту")
@app_commands.describe(member="У кого", amount="Сколько")
async def remove(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    user_id = str(member.id)

    if balances[user_id] < amount:
        await interaction.response.send_message("⚠ Недостаточно средств.", ephemeral=True)
        return

    balances[user_id] -= amount
    save_data()

    emoji = get_emoji(interaction.guild)

    embed = discord.Embed(
        title="➖ Списание",
        description=f"С пользователя {member.mention} списано **{amount}** {emoji}.",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)

# ================= TOP =================
@tree.command(name="top", description="Топ богатейших игроков")
async def top(interaction: discord.Interaction):

    if not balances:
        await interaction.response.send_message("📉 Пока нет данных.")
        return

    emoji = get_emoji(interaction.guild)
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    description = "🏆 **Рейтинг самых богатых игроков:**\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for index, (user_id, amount) in enumerate(sorted_balances[:10], start=1):
        nickname = nicknames.get(user_id, "Unknown")
        medal = medals[index-1] if index <= 3 else "🔹"
        description += f"{medal} **{index}. {nickname}** — `{amount}` {emoji}\n"

    description += "\n💰 Просмотреть баланс можно командой `/balance`."

    embed = discord.Embed(
        title="🏆 Топ игроков",
        description=description,
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
