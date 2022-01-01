from asyncio import sleep
from glob import glob
from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.ext.commands import Bot as BotBase
from datetime import datetime
from discord.ext.commands import CommandNotFound

from ..db import db

PREFIX = "."
OWNER_IDS = [313751695819538432]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False  
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler =  AsyncIOScheduler()
        
        db.autosave(self.scheduler)
        super().__init__(command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("setup complete")
    
    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        channel = self.get_channel(920321834321342560)
        await channel.send("Notificação cronometrada!")


    async def on_connect(self):
        print("bot connected")
        
    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs ):
        if err == "on_command_error":
            await args[0].send("Algo deu errado")
        
        channel = self.get_channel(920321834321342560)
        await channel.send("Ocorreu um erro!")
        raise
    
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            # await ctx.send("Comando errado")
            pass

        elif hasattr(exc, "original"):
            raise exc.original

        else:
            raise exc

    
    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(920321834321342554)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(second=15))
            # self.scheduler.start()

            channel = self.get_channel(920321834321342560)
            await channel.send("Online agora!")

            # embed = Embed(title="Online Agora!", description="Lif agora Online!", 
            #             colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another Field", "This Field is next to the other one", True),
            #           ("A non-inline field" , "This field will appear on it's own row", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Will", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer!")
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)

            # await channel.send(embed=embed)
            # await channel.send(file=File("./data/images/profile.png"))
            
            print("bot ready!")


        else:
            print("bot reconnected")
    
    async def on_message(self, message):
        pass

bot = Bot()
    
