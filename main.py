import discord
import os
import random
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("BOT_KEY")

class Client(discord.Client):

    def __init__(self, *, intents, **options):

        self.symbol = "%"

        self.commands = ("enter", "quit", "assign", "kick", "check", "loadout", "wipe", "help")

        self.queue = []

        self.queue_max = 4

        self.anger_reaction_words = ["blacklist", "DA", "conviction", "Blacklist", "Conviction", "BL"]

        self.anger_reaction_chance = 10

        self.queue_afk_time = 10

        self.should_cancel_assign = False # lazy af variable for cancelling assigns in situations like assigning 3 people to 2/4 queue

        self.upcoming_participants = 0

        self.should_calc = True

        self.should_ping = True

        self.calc_buffer = 0

        self.responses_db_ping = [
            "i'm here",
            "listening",
            "yes?",
            "what do you need",
            "qq",
            "hello"
        ]

        self.responses_db = [
            "very interesting",
            "cool",
            "tl;dr",
            "uhuh",
            "that's bullshit",
            "you should chill you know",
            "very nice",
            "reminds me of.. actually never mind",
            "i hate shadownet",
            "just like the time i was working on warehouse",
            "leave the highly lethal pox-filled storage containers alone...",
            "shotgun my beloved",
            "i'm going to refill my gasmask",
            "larping hard rn"
        ]

        self.responses = self.responses_db

        self.recent_responses = []

        self.debug = True

        super().__init__(intents=intents, **options)

    def perform_response_choice(self, pool, uses_bans = True):


        mess = random.choice(pool)

        if uses_bans:

            self.recent_responses.insert(1, mess)

            pool.remove(mess)

            for i in range(len(self.recent_responses)):
                print(self.recent_responses)
                
                h = random.randint(len(self.recent_responses) - 2, len(self.recent_responses))

                print(i, h)

                if i >= h:
                    pool.insert(1, self.recent_responses[i])
                    self.recent_responses.pop(i)

        return mess
        



    def get_queue_count(self):
        return f"{len(self.queue)}/{self.queue_max}"

    def get_queue_users(self, mode = "format"):
        queue_users_str = ""
        add = ""
        
        for queue_user in self.queue:
            if mode == "format":
                add = f"<@{queue_user.id}> "
            elif mode == "display_name":
                add = f"{queue_user.display_name} "
            elif mode == "username":
                add = f"{queue_user} "

            queue_users_str = queue_users_str + add

        return queue_users_str


    async def on_queue_enter(self, message, user, initializer = None, add_ping = True):
        if not self.debug:
            if user in self.queue:
                message.channel.send(f"{user.display_name} failed to enter queue, reason: in queue already")
                print(f"{user} failed to enter queue, reason: in queue already")
                return

        if user == self.user:
            await message.channel.send(f"{user.display_name} failed to enter queue, reason: i retired a long time ago bro")
            print(f"{user} failed to enter queue, reason: it's me")
            return

        self.queue.append(user)

        if len(self.queue) == self.queue_max:

            await message.channel.send(f"{self.get_queue_users()}game is up!")

            self.queue = []

            print(f"{self.get_queue_users("username")}game is up, clearing the queue")

            if self.calc_buffer > self.queue_max:
                self.should_cancel_assign = True
            

        else:
            print(f"{user} added on the queue by {initializer or "himself"}, {self.get_queue_count()}")

            add_message = f"{user.display_name} added to the queue, {self.get_queue_count()}"

            if add_ping:
                add_message = add_message + " @here"

            await message.channel.send(add_message)
 

    async def on_queue_leave(self, message, user, initializer = None):
        if user == self.user:
            print(f"{user} failed to leave queue, reason: it's me")
            await message.channel.send(f"{user.display_name} failed to leave queue, reason: i'm not even in the queue lmao")
            return
        
        if not user in self.queue:
            print(f"{user} failed to leave queue, reason: not in queue")
            await message.channel.send(f"{user.display_name} failed to leave queue, reason: not in queue")
            return
        

        self.queue.remove(user)

        await message.channel.send(f"{user.display_name} removed from queue, {self.get_queue_count()}")

        print(f"{user} left the queue ({initializer or "himself"}), {self.get_queue_count()}")

    async def on_queue_check(self, message):

        if len(self.queue) == 0:
            await message.channel.send("current queue is empty")
            return

        queue_users = self.get_queue_users("display_name")

        await message.channel.send(f"current queue is: {queue_users}{self.get_queue_count()}")

    async def on_queue_clear(self, message):
    
        self.queue = []

        await message.channel.send(f"wiped the queue, {self.get_queue_count()}")

        print(f"queue wiped by {message.author}")

    async def on_random_loadout(self, message):
        spy_gadgets = ["Optical Camo Suit", "Spy Bullet", "Sticky Camera", "Alarm Snare", "Smoke Grenade", "Flash Grenade", "Chaff Grenade", "Heartbeat Sensor"]
        merc_gadgets = ["Frag Grenade", "Backpack", "Cam. Net.", "Mine", "Spy Tracker", "Gasmask", "Taser", "Flare"]
        reaction = ["nice", "very good", "interesting", "cool", "splendid", "amazing", "awesome", "super"]

        spy_s = "Spy gadgets: "
        merc_s = "Merc gadgets: "

        for i in range(4):
            gadget = random.choice(spy_gadgets)
            spy_s = spy_s + gadget

            if not i == 3: spy_s = spy_s + ", "


            spy_gadgets.remove(gadget)

        for i in range(4):
            gadget = random.choice(merc_gadgets)
            merc_s = merc_s + gadget

            if not i == 3: merc_s = merc_s + ", "

            merc_gadgets.remove(gadget)

        await message.channel.send(f"{spy_s}\n{merc_s}\n..{random.choice(reaction)}")


    async def on_ready(self):
        print(self.commands)
        print(f'logged on as {self.user}')

    async def on_message(self, message):

        if message.author == self.user:
            return

        if message.content.strip().lower() == self.symbol + self.commands[0]: # potentially could be replaced with dictionary that has command name and it's function but whatever
            await self.on_queue_enter(message, message.author)
        elif message.content.strip().lower() == self.symbol + self.commands[1]:
            await self.on_queue_leave(message, message.author)
        elif message.content.strip().lower() == self.symbol + self.commands[4]:
            await self.on_queue_check(message)
        elif message.content.strip().lower() == self.symbol + self.commands[5]:
            await self.on_random_loadout(message)
        elif message.content.strip().lower() == self.symbol + self.commands[6]:
            await self.on_queue_clear(message)
        elif message.content.strip().lower() == self.symbol + self.commands[7]:
            await message.channel.send(f"as you've realized by now my prefix is {self.symbol}\n" \
            f"{self.symbol}enter/{self.symbol}quit - join or leave the queue\n" \
            f"{self.symbol}assign @user/{self.symbol}kick @user - add or remove someone from queue\n"
            f"{self.symbol}check - get info on current queue\n" \
            f"{self.symbol}wipe - clear the current queue, a.k.a. remove every participant from it\n"
            f"{self.symbol}loadout - i'll think of a random loadout for both spy and merc team\n" \
            f"{self.symbol}help - shows this message, as you can see\n" \
            "you could try and mention me for some chit-chat but i'm not very talkative and prefer just doing my job instead")

        message_array = message.content.split()

        for i in self.anger_reaction_words:

            if i in message_array:

                chance = random.randint(1, 100)

                if chance <= self.anger_reaction_chance:

                    print("forbidden word detected...")
                    await message.add_reaction("😡")
                    break

        if len(message_array) >= 2:

            command = message_array[0]

            if command.strip().lower()[1:] in self.commands:

                for i in range(1, len(message_array)):

                                                      
                    dude = message_array[i]

                    if command.strip().lower() == self.symbol + self.commands[2]:

                        self.upcoming_participants = len(message_array) - 1

                        if self.should_calc:

                            self.calc_buffer = self.upcoming_participants + len(self.queue)
                            self.should_calc = False

                        print(self.upcoming_participants + len(self.queue))

                        if self.should_cancel_assign:
                            self.should_cancel_assign = False
                            break

                        server_member = message.guild.get_member(int(dude[2:-1]))

                        if self.calc_buffer >= self.queue_max:
                            self.should_ping = False


                        if server_member and not self.should_cancel_assign: # there is probably a better alternative to this
                            await self.on_queue_enter(message, server_member, message.author, self.should_ping)

                    if command.strip().lower() == self.symbol + self.commands[3]:

                        server_member = message.guild.get_member(int(dude[2:-1]))

                        if server_member:
                            await self.on_queue_leave(message, server_member, message.author)

                self.should_ping = True
                self.should_calc = True
                self.calc_buffer = 0
        
        if not message.content.strip().lower().split()[0][1:] in self.commands:

            if self.user.mentioned_in(message):

                if len(message.content.split()) == 1:

                    await message.channel.send(self.perform_response_choice(self.responses_db_ping, False))

                else:

                    await message.channel.send(self.perform_response_choice(self.responses, False))

    
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True


client = Client(intents=intents)
client.run(key)