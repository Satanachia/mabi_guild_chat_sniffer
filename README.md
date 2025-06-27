# Mabinogi Chat Sniffer → Discord Bridge

A personal tool for capturing guild chat messages from **Mabinogi** and forwarding them to a Discord channel via webhook — and vice versa.

---

## What it Does

### `to_discord.py`
- Uses `pyshark` to **sniff packets** from the Mabinogi chat server
- Detects in-game messages based on known packet structure
- Extracts and decodes messages
- Forwards cleaned messages to a **Discord Webhook**

### `to_client.py`
- Listens to a selected **Discord channel**
- Cleans and formats messages:
  - Removes Discord emotes and unicode emojis
  - Trims invisible characters
  - Breaks messages into 80-character chunks
- **Types messages** into the currently selected window using `xdotool`

> 💡 Tip: Select the Mabinogi chat input box after running `to_client.py`

---

## Requirements

Works on **Linux only** (designed for my personal server setup)

### Python dependencies
Install with `pip install -r requirements.txt` or manually:
- discord.py
- discord_webhook
- pyshark

###  System dependencies
Make sure you have installed:

- Wireshark
- xdotool

Make sure you have permissions for dumpcap / tshark


---

### Important Notes
-This is a personal project / toy tool
-Use at your own risk
-No support guaranteed

### License
MIT / FOSS — fork it, use it, break it. Have fun.
