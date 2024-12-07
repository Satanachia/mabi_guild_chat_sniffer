import os
import time
import discord
import re

TARGET_CHANNEL_ID = 111111111111111 #discord channel id here
TOKEN = "TOKEN_HERE"

DISCORD_EMOTE_PATTERN = r'<a?:(\w+):\d+>'
UNICODE_EMOJI_PATTERN = r'[\U0001F1E6-\U0001F1FF\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]'
INVISIBLE_CHAR_PATTERN = r'[\u200B\u200C\u200D\u200E\u200F\u202A-\u202E\u2060\u2061\u2062\u2063\u206A-\u206F\uFEFF]'


def split_message(message, limit=80):
    words = message.split(' ')  # Split the message into words
    chunks = []
    current_chunk = ''

    for word in words:
        # Check if adding the next word would exceed the limit
        if len(current_chunk) + len(word) + 1 > limit:  # +1 for the space
            chunks.append(current_chunk)  # Store the current chunk
            current_chunk = word  # Start a new chunk with the current word
        else:
            if current_chunk:  # If current_chunk isn't empty, add a space
                current_chunk += ' '
            current_chunk += word  # Add the word to the current chunk

    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def replace_unicode_emojis_with_star(message):
    # Replace all unicode emojis with a star
    cleaned_message = re.sub(UNICODE_EMOJI_PATTERN, '*', message)
    message = re.sub(INVISIBLE_CHAR_PATTERN, '', message)
    return cleaned_message



class MyClient(discord.Client):
    async def on_ready(self):
        print(f'logged on as {self.user}!')
    
    async def on_message(self, message):
        if message.channel.id == TARGET_CHANNEL_ID:
            usrname = message.author.display_name

            print(usrname)
            print(message.content)

            messageout = ""
            if message.content == None:
                messageout = " "
            else:
                messageout = message.content

            cleaned_message = re.sub(DISCORD_EMOTE_PATTERN, r':\1: ', messageout)
            cleaned_message = replace_unicode_emojis_with_star(cleaned_message)


            startsendmabi = "[" + usrname + "] : " + cleaned_message

            chunks = split_message(startsendmabi, 80)
            print (chunks)

            for chunk in chunks:
                string = f'xdotool type "{chunk}"'
                print (string)
                os.system(string)
                os.system('xdotool key Return')
                time.sleep(0.02)



intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)

client.run(TOKEN)
