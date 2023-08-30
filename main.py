import nextcord
from nextcord.ext import commands
import wavelinkcord as wavelink

intents = nextcord.Intents.all()
client = nextcord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=nextcord.Game(name="/help,/play,/stop"))
    bot.loop.create_task(on_node())
    


async def on_node():
    node =  wavelink.Node(uri="lavalink.devamop.in", password="DevamOP")
    await  wavelink.NodePool.connect(client=bot, nodes=[node])
    wavelink.Player.autoplay = True

@bot.slash_command(name='help', description='Display available commands')
async def help_command(ctx):
    embed = nextcord.Embed(title="Available Commands")
    embed.add_field(name="/play", value="plays the music you put in", inline=False)
    embed.add_field(name="/skip", value="skips the music you play", inline=False)
    embed.add_field(name="/pause", value="pauses the music you play", inline=False)
    embed.add_field(name="/resume", value="resumes the music you paused", inline=False)

    await ctx.send(embed=embed)

@bot.slash_command(name='play', description='Plays the music you tell it to play!')
async def play(interaction: nextcord.Interaction, search: str):
    query: list[wavelink.YouTubeMusicTrack] = await wavelink.YouTubeMusicTrack.search(search)
    query: wavelink.GenericTrack = query[0]
    print(query)
 
    destination = interaction.user.voice.channel

    if not interaction.guild.voice_client:
        vc = await destination.connect(cls= wavelink.Player)
    else:
        vc = interaction.guild.voice_client
    if vc.queue.is_empty and not vc.is_playing():
        await vc.play(query)
        await interaction.response.send_message(f"Now Playing {vc.current.title}")
    else:
        await vc.queue.put_wait(query)
        await interaction.response.send_message(f"Now Playing {vc.current.title}")

@bot.slash_command(name='skip', description='Skips the currently playing track')
async def skip(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    await vc.stop()
    await interaction.response.send_message("Song was Skipped!")

@bot.slash_command(name='pause', description='Pauses the current track')
async def pause(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    if vc.is_playing():
        await vc.pause()
    else:
        await interaction.response.send_message("Song is already Paused!")

@bot.slash_command(name='resume', description='Resumes the track which was paused')
async def resume(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    if vc.is_playing():
        await interaction.response.send_message("Song is already Resumed!")
    else:
        await interaction.response.send_message("Song is Resumed!")
        await vc.resume()

@bot.slash_command(name='disconnect', description='Disconnects the bot from channel')
async def disconnect(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    await vc.disconnect()        
    await interaction.response.send_message("Bot Disconnected")

@bot.slash_command(name='queue', description='Displays the songs which are queued')
async def queue(interaction: nextcord.Interaction):
    vc = interaction.guild.voice_client
    if not vc.queue.is_empty:
        song_counter = 0
        songs = []
        queue = vc.queue.copy()
        embed = nextcord.Embed(title="Music Queue")
        for song in queue:
            song_counter += 1
            songs.append(song)
            embed.add_field(name=f"[{song_counter}] Duration {song.duration}", value=f"{song.title}", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Queue is Empty!")

bot.run("MTEyNzYzMjQzMzE5NDQ4Nzg0OQ.Gj2Z2P.C1yKix4URjL91CqK06hDJedjBD1XZQp3b2eky0")
