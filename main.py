import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")

OWNER_ID = 1466843004458238166
EMOJI = "<:brotherhoodcoin:1473782095884320804>"

intents = discord.Intents.default()
intents.message_content = True

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

# ====== ID ======
@bot.command()
async def myid(ctx):
    await ctx.send(f"🆔 Твой ID: `{ctx.author.id}`")

# ====== БАЛАНС ======
@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    amount = balances.get(user_id, 0)

    embed = discord.Embed(
        title="💰 Баланс",
        description=f"У тебя **{amount}** {EMOJI}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Запросил: {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

# ====== ADD ======
@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    embed = discord.Embed(
        title="✅ Начисление",
        description=f"{member.mention} получил **{amount}** {EMOJI}",
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

# ====== REMOVE ======
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    current_balance = balances.get(user_id, 0)

    if current_balance < amount:
        await ctx.send("⚠️ У пользователя недостаточно средств.")
        return

    balances[user_id] = current_balance - amount
    save_balances(balances)

    embed = discord.Embed(
        title="➖ Списание",
        description=f"У {member.mention} списано **{amount}** {EMOJI}",
        color=discord.Color.red()
    )

    await ctx.send(embed=embed)

# ====== TOP ======
@bot.command()
async def top(ctx):
    if not balances:
        await ctx.send("📉 Пока никто не имеет коинов.")
        return

    sorted_balances = sorted(balances.items(), key=lambda x: x[1], reverse=True)

    description = ""
    for index, (user_id, amount) in enumerate(sorted_balances[:10], start=1):
        member = ctx.guild.get_member(int(user_id))
        if member:
            description += f"**{index}.** {member.mention} — `{amount}` {EMOJI}\n"

    embed = discord.Embed(
        title="🏆 Топ богатейших",
        description=description,
        color=discord.Color.purple()
    )

    await ctx.send(embed=embed)

bot.run(TOKEN)
