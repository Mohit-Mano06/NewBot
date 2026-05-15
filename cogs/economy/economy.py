import discord
from discord.ext import commands
import database
from datetime import datetime, timezone

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="balance", aliases=["bal"], description="Check your current balance.")
    async def balance(self, ctx, user: discord.Member = None):
        target = user or ctx.author
        data = await database.get_balance(str(target.id))
        
        embed = discord.Embed(
            title=f"💳 {target.display_name}'s Balance",
            color=discord.Color.gold(),
            description=f"**Balance:** {data['balance']} Credits"
        )
        if data['last_daily']:
            try:
                dt = datetime.fromisoformat(data['last_daily'])
                embed.set_footer(text=f"Last Daily: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except Exception:
                pass
                
        await ctx.send(embed=embed)

    @commands.command(name="daily", description="Claim your daily free Credits.")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        data = await database.get_balance(user_id)
        
        # Check cooldown
        if data['last_daily']:
            try:
                last_dt = datetime.fromisoformat(data['last_daily'])
                now = datetime.now(timezone.utc)
                delta = now - last_dt
                if delta.days < 1:
                    hours_left = 24 - (delta.seconds // 3600)
                    await ctx.send(f"⌛ You already claimed your daily! Try again in **{hours_left} hours**.")
                    return
            except Exception:
                pass

        amount = 5000  # Give 5000 free Credits
        
        success = await database.update_balance(user_id, amount, "daily", "Claimed daily reward")
        if success:
            await database.update_last_daily(user_id)
            await ctx.send(f"🎉 You successfully claimed **{amount} Credits**! Come back tomorrow for more.")
        else:
            await ctx.send("❌ Failed to claim daily. Supabase connection error.")

    @commands.command(name="transfer", aliases=["send"], description="Transfer Credits to another user.")
    async def transfer(self, ctx, user: discord.Member, amount: int):
        if amount < 1000:
            await ctx.send("❌ The minimum transfer amount is **1000 Credits**.")
            return
            
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot transfer Credits to yourself.")
            return

        if user.bot:
            await ctx.send("❌ You cannot transfer Credits to a bot.")
            return

        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)
        
        sender_data = await database.get_balance(sender_id)
        if sender_data['balance'] < amount:
            await ctx.send(f"❌ You don't have enough Credits! Your balance is **{sender_data['balance']} Credits**.")
            return
            
        # Execute transfer
        success_deduct = await database.update_balance(sender_id, -amount, "transfer_out", f"Transferred to {user.id}")
        if success_deduct:
            success_add = await database.update_balance(receiver_id, amount, "transfer_in", f"Received from {ctx.author.id}")
            if success_add:
                await ctx.send(f"💸 Successfully transferred **{amount} Credits** to {user.mention}!")
            else:
                # Refund if possible
                await database.update_balance(sender_id, amount, "refund", "Transfer failed midway")
                await ctx.send("❌ Transfer failed. Your credits were refunded.")
        else:
            await ctx.send("❌ Transfer failed due to a database error.")

async def setup(bot):
    await bot.add_cog(Economy(bot))
