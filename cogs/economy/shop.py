import discord
from discord.ext import commands
import database

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shop", description="Browse the shop for items.")
    async def shop(self, ctx):
        items = await database.get_shop_items()
        
        if not items:
            await ctx.send("🛍️ The shop is currently empty.")
            return

        embed = discord.Embed(title="🛒 Shop", color=discord.Color.green(), description="Here are the available items:")
        for item in items:
            embed.add_field(
                name=f"{item['name']} (ID: {item['id']})",
                value=f"**Price**: {item['price']} Credits\n**Type**: {item['type'].capitalize()}\n{item.get('description', '')}",
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name="buy", description="Buy an item from the shop by ID.")
    async def buy(self, ctx, item_id: int):
        user_id = str(ctx.author.id)
        
        items = await database.get_shop_items()
        target_item = next((i for i in items if i['id'] == item_id), None)
        
        if not target_item:
            await ctx.send(f"❌ Item with ID **{item_id}** not found.")
            return
            
        price = target_item['price']
        user_data = await database.get_balance(user_id)
        
        if user_data['balance'] < price:
            await ctx.send(f"❌ You don't have enough Credits! This item costs **{price} Credits**, but you only have **{user_data['balance']}**.")
            return
            
        # Deduct balance
        success_deduct = await database.update_balance(user_id, -price, "buy", f"Bought item {item_id}")
        if success_deduct:
            # Add to inventory
            success_add = await database.add_item_to_inventory(user_id, item_id, 1)
            if success_add:
                await ctx.send(f"🎉 Successfully purchased **{target_item['name']}**!")
            else:
                # Refund
                await database.update_balance(user_id, price, "refund", "Inventory error")
                await ctx.send("❌ Failed to add item to your inventory. Your credits were refunded.")
        else:
            await ctx.send("❌ Database error during purchase.")

    @commands.command(name="inventory", aliases=["inv"], description="View your owned items.")
    async def inventory(self, ctx):
        user_id = str(ctx.author.id)
        inv = await database.get_inventory(user_id)
        
        if not inv:
            await ctx.send("🎒 Your inventory is empty.")
            return
            
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.blue())
        for row in inv:
            # Supabase join returns shop_items as a dict if properly configured
            item_data = row.get('shop_items', {})
            item_name = item_data.get('name', 'Unknown Item (ID ' + str(row.get('item_id')) + ')')
            item_type = item_data.get('type', 'Unknown Type')
            qty = row['quantity']
            
            embed.add_field(
                name=f"{item_name} (x{qty})",
                value=f"Type: {item_type.capitalize()}",
                inline=True
            )
            
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Shop(bot))
