# B402 NFT Telegram Bot - Version ROBUST (With Better Retry)
# Perbaikan: Monitor semua Token ID + Better error handling

import requests
import asyncio
from telegram import Bot
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "7925753319:AAEWkxrivRuDQHiau8fVQ9hPkOlgvGU5i9c"
TELEGRAM_CHAT_ID = "519076139"
ETHERSCAN_V2_API_KEY = "QKYIDZDBII9I4H8M2UFEZFF8A38J38WAQF"

WATCHED_WALLET = "0x39Dcdd14A0c40E19Cd8c892fD00E9e7963CD49D3"
CONTRACT_ADDRESS = "0xafcD15f17D042eE3dB94CdF6530A97bf32A74E02"

# Monitor SEMUA Token ID (0, 1, 2)
WATCHED_TOKEN_IDS = {
    "0": {"name": "Bronze Mystery Box", "emoji": "🥉", "rarity": "Common (94%)"},
    "1": {"name": "Silver Mystery Box", "emoji": "🥈", "rarity": "Langka (5%)"},
    "2": {"name": "Gold Mystery Box", "emoji": "🏆", "rarity": "Sangat Langka (1%)"}
}

CHECK_INTERVAL = 60  # LEBIH SERING: setiap 1 menit (bukan 3)
CHAIN_ID = "56"
TIMEOUT = 15  # LEBIH LAMA: 15 detik timeout

tracked_txhashes = set()
bot = None
last_api_used = None
floor_prices_cache = {}
bnb_price_cache = None
last_price_update = None

async def send_notification(message: str):
    """Kirim pesan ke Telegram"""
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )
        print(f"✓ Notif terkirim")
    except Exception as e:
        print(f"✗ Error: {e}")

def get_bnb_price_usd():
    """Ambil harga BNB"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "binancecoin", "vs_currencies": "usd"},
            timeout=TIMEOUT
        )
        data = response.json()
        if "binancecoin" in data:
            bnb_price = data["binancecoin"]["usd"]
            print(f"✓ BNB: ${bnb_price:.2f}")
            return bnb_price
    except Exception as e:
        print(f"⚠ CoinGecko: {e}")
    return None

def get_floor_prices():
    """Ambil floor price dari OKX"""
    try:
        response 
