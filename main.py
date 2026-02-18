import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")
OWNER_ID = 1466843004458238166  # ТВОЙ ID

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

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

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

def get_emoji(guild):
    emoji = discord.utils.get(guild.emojis, name="brotherhoodcoin")
    return str(emoji) if emoji else "🪙"

# ===== ID =====
@bot.command()
async def myid(ctx):
    await ctx.send(f"🆔 Твой ID: `{ctx.author.id}`")

# ===== BALANCE =====
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    amount = balances.get(user_id, 0)
    emoji = get_emoji(ctx.guild)

    embed = discord.Embed(
        title="💰 Баланс",
        description=f"У тебя **{amount}** {emoji}",
        color=discord.Color.gold()
    )

    await ctx.send(embed=embed)

# ===== GIVE (простое начисление) =====
@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    emoji = get_emoji(ctx.guild)

    embed = discord.Embed(
        title="💸 Начисление средств",
        description=f"{member.mention}, вам начислено **{amount}** {emoji}.",
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

# ===== ADD (карта одобрена) =====
@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    emoji = get_emoji(ctx.guild)

    embed = discord.Embed(
        title="💳 Карта одобрена!",
        description=(
            f"🎉 Поздравляем, {member.mention}!\n\n"
            f"Ваша заявка была успешно одобрена.\n"
            f"На ваш баланс зачислено **{amount}** {emoji}.\n\n"
            f"💰 Проверить баланс: `!balance`"
        ),
        color=discord.Color.green()
    )

    embed.set_footer(text="Финансовая система Brotherhood")

    await ctx.send(embed=embed)

# ===== REMOVE =====
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    current_balance = balances.get(user_id, 0)

    if current_balance < amount:
        await ctx.send("⚠️ Недостаточно средств.")
        return

    balances[user_id] = current_balance - amount
    save_balances(balances)

    emoji = get_emoji(ctx.guild)

    embed = discord.Embed(
        title="➖ Списание",
        description=f"У {member.mention} списано **{amount}** {emoji}.",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

# ===== TOP =====
@bot.command()
async def top(ctx):
    if not balances:
        await ctx.send("📉 Пока никто не имеет коинов.")
        return

    emoji = get_emoji(ctx.guild)
    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    description = ""
    for index, (user_id, amount) in enumerate(sorted_balances[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        description += f"**{index}.** {user.name} — `{amount}` {emoji}\n"

    embed = discord.Embed(
        title="🏆 Топ богатейших",
        description=description,
        color=discord.Color.purple()
    )

    await ctx.send(embed=embed)

bot.run(TOKEN)
        
