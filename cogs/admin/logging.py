# Mapping: {Guild_ID: Log_Channel_ID}
LOG_CHANNELS = {
    1470000357332484164: 1471834447124107498,  # Dev Server (Replace first ID with actual Dev Guild ID)
    1091572652335960114: 1471850287781253249  # Pvt Server (Replace with actual Pvt Guild ID and Log Channel ID)
}

async def send_log(bot, guild, embed):
    channel_id = LOG_CHANNELS.get(guild.id)
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)
