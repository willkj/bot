from asyncio import sleep
from glob import glob
from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from datetime import datetime
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)

from ..db import db

PREFIX = "."
OWNER_IDS = [313751695819538432]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


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
    
    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)
        
        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send('Im not ready to receive commands. Please wait a few seconds.')


    async def rules_reminder(self):
        await self.stdout.send("Notificação cronometrada!")


    async def on_connect(self):
        print("bot connected")
        
    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs ):
        if err == "on_command_error":
            await args[0].send("Algo deu errado")
        
        await self.stdout.send("Ocorreu um erro!")
        raise
    
    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        
        elif isinstance(exc, BadArgument):
            pass
            
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")

        elif isinstance(exc.original, HTTPException):
            await ctx.send("Unable to send message.")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("i do not have permission to do that.")
        else:
            raise exc.original

    
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(920321834321342554)
            self.stdout = self.get_channel(920321834321342560)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=15))
            # self.scheduler.start()


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
            
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Online agora!")
            self.ready = True
            print("bot ready!")


        else:
            print("bot reconnected")
    
    async def on_message(self, message):
        # if message.author.bot and message.author != message.guild.me:
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
    
