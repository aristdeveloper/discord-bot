import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")

OWNER_ID = 1473777685044924640  # твой ID

COIN_EMOJI = "<:brotherhoodcoin:1473782095884320804>"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# создаём файл если его нет
if not os.path.exists("balance.json"):
    with open("balance.json", "w") as f:
        json.dump({}, f)

def load_balance():
    with open("balance.json", "r") as f:
        return json.load(f)

def save_balance(data):
    with open("balance.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.command()
async def add(ctx, member: discord.Member, amount: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ У тебя нет прав для начисления коинов.")
        return

    if amount <= 0:
        await ctx.send("❌ Количество должно быть больше 0.")
        return

    data = load_balance()
    user_id = str(member.id)

    if user_id not in data:
        data[user_id] = 0

    data[user_id] += amount
    save_balance(data)

    await ctx.send(
        f"🎉 Поздравляю, ваша карта была принята!\n"
        f"На ваш баланс начислено {amount} {COIN_EMOJI}\n"
        f"💰 Текущий баланс: {data[user_id]} {COIN_EMOJI}"
    )

@bot.command()
async def balance(ctx):
    data = load_balance()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = 0

    await ctx.send(
        f"💰 Ваш баланс: {data[user_id]} {COIN_EMOJI}"
    )

bot.run(TOKEN)
