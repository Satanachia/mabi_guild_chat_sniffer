import os
from dotenv import load_dotenv
import datetime
import pyshark
from discord_webhook import DiscordWebhook


NETWORKINTERFACE = os.getenv("NETWORK_INTERFACE")
CHATSERVERIP= os.getenv("MABI_CHAT_SERVER_IP")
DISCORD_HOOK = os.getenv("DISCORD_WEB_HOOK")
MABI_CHAR_NAME = os.getenv("MABI_CHAR_NAME")


if not NETWORKINTERFACE:
    raise ValueError("Network interface not set in .env")

if not CHATSERVERIP:
    raise ValueError("Chat server IP not set in .env")

if not DISCORD_HOOK:
    raise ValueError("Discord webhook address not set in .env")

if not MABI_CHAR_NAME:
    raise ValueError("Chat bot username (in mabinogi) not set in .env")

#capture from
#54.214.176.167 is chat server used for guild chat normally
#however we are are using the ip given from the ENV
filterstring = f'src host {CHATSERVERIP}'
capture = pyshark.LiveCapture(interface=NETWORKINTERFACE, bpf_filter=filterstring)


#inform user we captureing
print ("listening on %s" % NETWORKINTERFACE)

for packet in capture.sniff_continuously():
    #check if tcp packet
    if ("TCP" in str(packet.layers)):

        #make sure the packet has a payload otherwise crash
        if hasattr(packet.tcp, "payload"):

            #make the payload into a string for reading
            tempString = str(packet.tcp.payload)

            #make sure the message is from guild
            if ("00:00:c3:6f" in tempString):

                #turn payload into a byte array
                byte_array = bytes.fromhex(tempString.replace(":", ""))

                #get the name and format
                nameLeng = int.from_bytes(byte_array[20:22], "big")

                name = byte_array[22:22+nameLeng].decode("utf-8")
                name = name.lower()
                if MABI_CHAR_NAME not in name:


                    name = name.capitalize()


                    #get message
                    messageLength = int.from_bytes(byte_array[22+nameLeng+1 :22+nameLeng+3], "big")
                    message = byte_array[22+nameLeng+3:22+nameLeng+3+messageLength].decode("utf-8")

                    #print guild chat message to console
                    localtime = datetime.datetime.now().strftime("%d.%b | %H:%M:%S")
                    log = "(" + localtime + ") " + name + ": " + message
                    out = message
                    print(log)

                    #remove @everyone and @here tags
                    #remove the added & nexon adds
                    out = out.replace("@everyone","")
                    out = out.replace("@here","")
                    out = out.replace("&", "")

                    #send it out to the Webhook
                    Webhook = DiscordWebhook(url=DISCORD_HOOK,username=name,content=out)
                    response = Webhook.execute()

                