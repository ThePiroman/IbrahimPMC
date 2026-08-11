import discord
import os
import math
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("BOT_KEY")

class Client(discord.Client):

    def __init__(self, *, intents, **options):

        self.symbol = "*"

        self.commands = ("enter", "quit", "assign", "kick", "check", "loadout")

        self.queue = []

        self.queue_max = 4

        self.anger_reaction_chance = 5

        self.debug = True

        super().__init__(intents=intents, **options)

    async def on_queue_enter(self, message, user, initializer = None):
        if not self.debug:
            if user in self.queue:
                print(f"{user} failed to enter queue, reason: in queue already")
                return

        self.queue.append(user)

        if len(self.queue) == self.queue_max:
            queue_users_str = ""

            for queue_user in self.queue:
                queue_users_str = queue_users_str + f"@{queue_user} "

            self.queue = []

            print(f"{queue_users_str}game is up, clearing the queue")

            # await message.channel.send()
        else:
            print(f"{user} added on the queue by {initializer or "himself"}, {len(self.queue)}/{self.queue_max}")
        # await message.channel.send()

    async def on_queue_leave(self, message, user, initializer = None):
        if not user in self.queue:
            print(f"{user} failed to leave queue, reason: not in queue")
            return

        self.queue.remove(user)

        print(f"{user} left the queue ({initializer or "himself"}), {len(self.queue)}/{self.queue_max}")



    async def on_ready(self):
        print(self.commands)
        print(f'logged on as {self.user}')

    async def on_message(self, message):

        if message.content.strip().lower() == self.symbol + self.commands[0]:
            await self.on_queue_enter(message, message.author)
        elif message.content.strip().lower() == self.symbol + self.commands[1]:
            await self.on_queue_leave(message, message.author)

        message_array = message.content.split()

        if len(message_array) == 2:

            command, dude = message_array[0], message_array[1]

            if command.strip().lower() == self.symbol + self.commands[2]:

                server_member = message.guild.get_member(int(dude[2:-1]))

                if server_member: # there is probably a better alternative to this
                    await self.on_queue_enter(message, server_member, message.author)

            if command.strip().lower() == self.symbol + self.commands[3]:

                server_member = message.guild.get_member(int(dude[2:-1]))

                if server_member:
                    await self.on_queue_leave(message, server_member, message.author)

    
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True


client = Client(intents=intents)
client.run(key)