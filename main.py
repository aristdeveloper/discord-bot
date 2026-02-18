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

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
balances = data["balances"]
nicknames = data["nicknames"]

# ===== Проверка регистрации =====
def is_registered(user_id):
    return str(user_id) in nicknames

def get_emoji(guild):
    emoji = discord.utils.get(guild.emojis, name="brotherhoodcoin")
    return str(emoji) if emoji else "🪙"

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Бот запущен как {bot.user}")

# ===== REGISTER =====
@tree.command(name="register", description="Зарегистрироваться в системе")
@app_commands.describe(nickname="Ваш никнейм в Brofist.io")
async def register(interaction: discord.Interaction, nickname: str):

    user_id = str(interaction.user.id)

    if is_registered(user_id):
        await interaction.response.send_message("❌ Вы уже зарегистрированы.", ephemeral=True)
        return

    if nickname.lower() in [n.lower() for n in nicknames.values()]:
        await interaction.response.send_message("❌ Этот ник уже занят.", ephemeral=True)
        return

    nicknames[user_id] = nickname
    balances[user_id] = balances.get(user_id, 0)

    save_data(data)

    embed = discord.Embed(
        title="✅ Регистрация успешна!",
        description=f"Вы зарегистрированы под ником **{nickname}**.\n\nТеперь вы можете пользоваться системой экономики.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ===== RENAME =====
@tree.command(name="rename", description="Изменить игровой ник")
@app_commands.describe(new_nickname="Новый никнейм")
async def rename(interaction: discord.Interaction, new_nickname: str):

    user_id = str(interaction.user.id)

    if not is_registered(user_id):
        await interaction.response.send_message("❌ Сначала зарегистрируйтесь через `/register`.", ephemeral=True)
        return

    if new_nickname.lower() in [n.lower() for n in nicknames.values()]:
        await interaction.response.send_message("❌ Этот ник уже занят.", ephemeral=True)
        return

    old_nick = nicknames[user_id]
    nicknames[user_id] = new_nickname

    save_data(data)

    embed = discord.Embed(
        title="🔄 Ник изменён",
        description=f"Ваш ник изменён с **{old_nick}** на **{new_nickname}**.",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

# ===== BALANCE =====
@tree.command(name="balance", description="Посмотреть баланс")
async def balance(interaction: discord.Interaction):

    user_id = str(interaction.user.id)

    if not is_registered(user_id):
        await interaction.response.send_message("❌ Сначала зарегистрируйтесь через `/register`.", ephemeral=True)
        return

    amount = balances.get(user_id, 0)
    emoji = get_emoji(interaction.guild)
    nickname = nicknames[user_id]

    embed = discord.Embed(
        title="💰 Профиль игрока",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.add_field(name="🎮 Игровой ник", value=nickname, inline=False)
    embed.add_field(name="📊 Баланс", value=f"{amount} {emoji}", inline=True)
    embed.add_field(name="🆔 Discord ID", value=interaction.user.id, inline=True)

    embed.set_footer(text="Экономическая система Brotherhood")

    await interaction.response.send_message(embed=embed)

# ===== GIVE =====
@tree.command(name="give", description="Начислить валюту")
@app_commands.describe(member="Кому выдать", amount="Сколько выдать")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец бота.", ephemeral=True)
        return

    if not is_registered(member.id):
        await interaction.response.send_message("❌ Пользователь не зарегистрирован.", ephemeral=True)
        return

    user_id = str(member.id)
    balances[user_id] += amount
    save_data(data)

    emoji = get_emoji(interaction.guild)
    nickname = nicknames[user_id]

    embed = discord.Embed(
        title="💸 Начисление средств",
        description=(
            f"Игрок **{nickname}** получил **{amount}** {emoji}.\n\n"
            f"💰 Проверить баланс можно командой `/balance`."
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
