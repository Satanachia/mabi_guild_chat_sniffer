What is this


## to discord
its a simple sniffer that uses tshark (pyshark) to read incoming packets from the mabinogi chat server
it will find any packets that are used for guild messages and send them to discord via a simple web hook

## to_client
will take a message from a choosen discord channel, find the display name for the user
attempt to remove any unicode emotes
attempt to give names to any discord based emote
split the message into chunks with out breaking apart whole words
then type those messages out using a linux command "xdotool"


the message will be typed into any text box that is currently selected so make sure you select the mabinogi chat box using the chat log


## extra

this will only work on linux. weird i know but my server runs linux and its easy for me

make sure you install on pip
- discord.py
- discord_webhook
- pyshark

make sure you have wireshark installed and network traffic capture dumpcap or tshark
in my case i used

```$> sudo apt install wireshark```

you will need to set perms for dumpcap and all that

