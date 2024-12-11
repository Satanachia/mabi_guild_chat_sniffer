import os
import time
import discord
import re
import asyncio
import subprocess

TARGET_CHANNEL_ID = 111111111111111 #discord channel id here
TOKEN = "TOKEN_HERE"
DISCORD_GUILD_ID = 111111111111111111

DISCORD_EMOTE_PATTERN = r'<a?:(\w+):\d+>'
UNICODE_EMOJI_PATTERN = r'[\U0001F1E6-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]'
INVISIBLE_CHAR_PATTERN = r'[\u200B\u200C\u200D\u200E\u200F\u202A-\u202E\u2060\u2061\u2062\u2063\u206A-\u206F\uFEFF]'


def split_message(message, limit=80):
    words = message.split(' ')  # Split the message into words
    chunks = []
    current_chunk = ''

    for word in words:
        # Check if adding the next word would exceed the limit
        if len(current_chunk) + len(word) + 1 > limit:  # +1 for the star
            chunks.append(current_chunk)  # Store the current chunk
            current_chunk = word  # Start a new chunk with the current word
        else:
            if current_chunk:  # If current_chunk isn't empty, add a star
                current_chunk += ' '
            current_chunk += word  # Add the word to the current chunk

    # Don't forget to add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def replace_unicode_emojis_with_star(message):
    # Replace all unicode emojis with a star
    cleaned_message = re.sub(UNICODE_EMOJI_PATTERN, '*', message)
    message = re.sub(INVISIBLE_CHAR_PATTERN, '', message)
    return cleaned_message



class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = asyncio.Queue()  # Initialize an async message queue
        self.scheduled_tasks = {}  # Store scheduled repeating messages
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=discord.Object(id=DISCORD_GUILD_ID))
        await self.tree.sync()


    async def on_ready(self):
        print(f'logged on as {self.user}!')
        # Start the message queue processing loop
        self.loop.create_task(self.process_message_queue())
    
    async def on_message(self, message:discord.Message):
        if message.webhook_id is not None:
            return
        
        if message.author.bot:
            return

        if message.channel.id == TARGET_CHANNEL_ID:
            # Ignore messages sent by webhooks
            usrname = message.author.display_name
            
            if message.content.startswith("!"):
                return


            message_content = message.content or " "

            cleaned_message = re.sub(DISCORD_EMOTE_PATTERN, r':\1: ', message_content)
            cleaned_message = replace_unicode_emojis_with_star(cleaned_message)


            formatted_message = f"[{usrname}] : {cleaned_message}".replace('"', '')

            chunks = split_message(formatted_message, 80)

            for chunk in chunks:
                chunk = chunk.replace('\0', '')  # Remove null byte
                if chunk:  # Only add non-empty chunks to the queue
                    await self.message_queue.put(chunk)


    async def process_message_queue(self):
        while True:
            chunk = await self.message_queue.get()
            try:
                self.type_message(chunk)
            except Exception as e:
                print(f"Error typing message: {e}")
            finally:
                self.message_queue.task_done()
            await asyncio.sleep(0.02)  # Wait between messages

    def type_message(self, message):
        os.system('xdotool key Return')
        time.sleep(0.02)
        subprocess.run(['xdotool', 'type', message])
        time.sleep(0.02)
        os.system('xdotool key Return')
        time.sleep(0.02)
        os.system('xdotool key Return')
        time.sleep(0.02)


    async def handle_schedule_command(self, time, message, interaction: discord.Interaction):
        try:
            interval = time  # Get the interval in seconds
            message_text = message  # Get the message to repeat

            task_id = len(self.scheduled_tasks) + 1
            task = self.loop.create_task(self.send_repeating_message(interval, message_text))
            self.scheduled_tasks[task_id] = {'task': task,'time': interval , 'message': message_text}  

            await interaction.response.send_message(content=f"Scheduled message every {interval} seconds: " + message_text, ephemeral=True)
        except ValueError:
            await interaction.response.send_message(content="Please provide a valid number for the interval.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(content=f"Error scheduling message: {e}", ephemeral=True)

    async def send_repeating_message(self, interval, message_text ):
        while True:
            chunks = split_message(message_text, 80)
            for chunk in chunks:
                chunk = chunk.replace('\0', '')  # Remove null byte
                if chunk:  # Only add non-empty chunks
                    await self.message_queue.put(chunk)
            await asyncio.sleep(interval)


    async def handle_stop_command(self, ID, interaction: discord.Interaction):
        task_id = ID
        task_to_remove = None
        
        # Find the task to remove without modifying the dictionary during iteration
        for task in self.scheduled_tasks:
            if task == task_id:
                task_to_remove = task
                break

        if task_to_remove:
            # Cancel and delete the scheduled task after the loop
            task = self.scheduled_tasks[task_to_remove]['task']
            task.cancel()
            del self.scheduled_tasks[task_to_remove]
            await interaction.response.send_message(content=f"Stopped scheduled message with ID `{task_id}`.", ephemeral=True)
        else:
            await interaction.response.send_message(content="No task found with that ID.", ephemeral=True)
    
    async def handle_list_command(self, interaction: discord.Interaction):
        if not self.scheduled_tasks:
            await interaction.response.send_message(content="There are no active scheduled messages.", ephemeral=True)
        else:
            task_list = "\n".join([f"ID: {str(task)} type: repeating message, interval: {self.scheduled_tasks[task]['time']} seconds, message: {self.scheduled_tasks[task]['message']}" for task in self.scheduled_tasks])
            await interaction.response.send_message(content=f"Active scheduled messages:\n{task_list}", ephemeral=True)



# Define the /reminder command outside the class, but inside the same file
@discord.app_commands.command(name="reminder", description="Set a reminder for the guild chat")
@discord.app_commands.describe(time="wait time between reminders (in seconds)")
@discord.app_commands.describe(message="message to send to guild chat")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def reminder_command(interaction: discord.Interaction,time: int,message: str):
    # Get an instance of the client to use its features
    client: MyClient = interaction.client  # This is the instance of MyClient
    print(interaction.user.display_name)
    await client.handle_schedule_command(time, message, interaction)
        


@discord.app_commands.command(name="list", description="get a list of current reminders")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def list_command(interaction: discord.Interaction):
    # Get an instance of the client to use its features
    client: MyClient = interaction.client  # This is the instance of MyClient

    await client.handle_list_command(interaction)

@discord.app_commands.command(name="stop", description="stop a reminder by ID")
@discord.app_commands.checks.has_permissions(manage_guild=True)
@discord.app_commands.describe(reminder_id="id of the reminder to stop")
async def stop_command(interaction: discord.Interaction, reminder_id: int):
    # Get an instance of the client to use its features
    client: MyClient = interaction.client  # This is the instance of MyClient

    await client.handle_stop_command(reminder_id,interaction)



intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

client.tree.add_command(reminder_command)
client.tree.add_command(list_command)
client.tree.add_command(stop_command)

client.run(TOKEN)
