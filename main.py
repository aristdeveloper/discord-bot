import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")

OWNER_ID = 1466843004458238166  # ТВОЙ НАСТОЯЩИЙ ID

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

@bot.command()
async def myid(ctx):
    await ctx.send(f"Твой ID: `{ctx.author.id}`")

@bot.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    amount = balances.get(user_id, 0)
    await ctx.send(f"💰 Ваш баланс: {amount} {EMOJI}")

@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Ты не владелец бота.")
        return

    user_id = str(member.id)
    balances[user_id] = balances.get(user_id, 0) + amount
    save_balances(balances)

    await ctx.send(f"✅ {member.mention} получил {amount} {EMOJI}")

bot.run(TOKEN)
