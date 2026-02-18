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

DATA_FILE = "balances.json"

def load_balances():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_balances(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

balances = load_balances()

def get_emoji(guild):
    emoji = discord.utils.get(guild.emojis, name="brotherhoodcoin")
    return str(emoji) if emoji else "🪙"

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Slash-команды синхронизированы. Бот запущен как {bot.user}")

# ===== /balance =====
@tree.command(name="balance", description="Посмотреть свой баланс")
async def balance(interaction: discord.Interaction):
    user = interaction.user
    user_id = str(user.id)
    amount = balances.get(user_id, 0)
    emoji = get_emoji(interaction.guild)

    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    position = next((i+1 for i, v in enumerate(sorted_balances) if v[0] == user_id), "—")

    embed = discord.Embed(
        title="💰 Личный профиль и баланс",
        color=discord.Color.gold()
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(name="👤 Пользователь", value=user.mention, inline=False)
    embed.add_field(name="🆔 ID", value=user.id, inline=True)
    embed.add_field(name="📊 Баланс", value=f"{amount} {emoji}", inline=True)
    embed.add_field(name="🏆 Место в топе", value=f"#{position}", inline=True)

    if hasattr(user, "joined_at") and user.joined_at:
        embed.add_field(
            name="📅 На сервере с",
            value=user.joined_at.strftime("%d.%m.%Y"),
            inline=False
        )

    embed.set_footer(text="Экономическая система Brotherhood")

    await interaction.response.send_message(embed=embed)

# ===== /give =====
@tree.command(name="give", description="Начислить валюту (простое начисление)")
@app_commands.describe(member="Кому выдать", amount="Сколько выдать")
async def give(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец бота.", ephemeral=True)
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    emoji = get_emoji(interaction.guild)

    embed = discord.Embed(
        title="💸 Начисление средств",
        description=(
            f"{member.mention}, вам начислено **{amount}** {emoji}.\n\n"
            f"💰 Просмотреть баланс можно командой `/balance`."
        ),
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)

# ===== /add =====
@tree.command(name="add", description="Начислить валюту (карта одобрена)")
@app_commands.describe(member="Кому выдать", amount="Сколько выдать")
async def add(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец бота.", ephemeral=True)
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    emoji = get_emoji(interaction.guild)

    embed = discord.Embed(
        title="🗺️ Карта одобрена!",
        description=(
            f"🎉 Поздравляем, {member.mention}!\n\n"
            f"Ваша заявка была успешно одобрена.\n"
            f"На ваш баланс зачислено **{amount}** {emoji}.\n\n"
            f"💰 Просмотреть баланс можно командой `/balance`."
        ),
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# ===== /remove =====
@tree.command(name="remove", description="Списать валюту")
@app_commands.describe(member="У кого списать", amount="Сколько списать")
async def remove(interaction: discord.Interaction, member: discord.Member, amount: int):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Ты не владелец бота.", ephemeral=True)
        return

    user_id = str(member.id)
    current_balance = balances.get(user_id, 0)

    if current_balance < amount:
        await interaction.response.send_message("⚠️ Недостаточно средств.", ephemeral=True)
        return

    balances[user_id] = current_balance - amount
    save_balances(balances)

    emoji = get_emoji(interaction.guild)

    embed = discord.Embed(
        title="➖ Списание",
        description=f"У {member.mention} списано **{amount}** {emoji}.",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)

# ===== /top =====
@tree.command(name="top", description="Посмотреть топ богатейших")
async def top(interaction: discord.Interaction):
    if not balances:
        await interaction.response.send_message("📉 Пока никто не имеет коинов.")
        return

    emoji = get_emoji(interaction.guild)
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    description = "🏆 **Рейтинг самых обеспеченных участников сервера:**\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for index, (user_id, amount) in enumerate(sorted_balances[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        medal = medals[index-1] if index <= 3 else "🔹"
        description += f"{medal} **{index}. {user.name}** — `{amount}` {emoji}\n"

    description += "\n💰 Просмотреть баланс можно командой `/balance`."

    embed = discord.Embed(
        title="🏆 Топ богатейших",
        description=description,
        color=discord.Color.purple()
    )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
