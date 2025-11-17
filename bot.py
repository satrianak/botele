# B402 NFT Telegram Bot - Railway Version (Direct Input)
# LANGSUNG INPUT TOKEN DI SINI - BUKAN ENV VARIABLES

import requests
import asyncio
from telegram import Bot
from datetime import datetime, timedelta

# ╔══════════════════════════════════════════════════════════╗
# ║     ⬇️ SESUAIKAN DENGAN DATA ANDA DI BAWAH INI ⬇️       ║
# ╚══════════════════════════════════════════════════════════╝

ETHERSCAN_V2_API_KEY = "QKYIDZDBII9I4H8M2UFEZFF8A38J38WAQF"  # Ganti dengan API key Anda
TELEGRAM_BOT_TOKEN = "7925753319:AAEWkxrivRuDQHiau8fVQ9hPkOlgvGU5i9c"  # Ganti dengan token Anda
TELEGRAM_CHAT_ID = "519076139"  # Ganti dengan chat ID Anda

# Konfigurasi
WATCHED_WALLET = "0x39Dcdd14A0c40E19Cd8c892fD00E9e7963CD49D3"
CONTRACT_ADDRESS = "0xafcD15f17D042eE3dB94CdF6530A97bf32A74E02"

WATCHED_TOKEN_IDS = {
    "1": {"name": "Silver Mystery Box", "emoji": "🥈", "rarity": "Langka (5%)"},
    "2": {"name": "Gold Mystery Box", "emoji": "🏆", "rarity": "Sangat Langka (1%)"}
}

CHECK_INTERVAL = 180
CHAIN_ID = "56"
TIMEOUT = 8

# ╔══════════════════════════════════════════════════════════╗
# ║              JANGAN UBAH DIBAWAH INI                   ║
# ╚══════════════════════════════════════════════════════════╝

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
        response = requests.get(
            "https://web3.okx.com/api/v5/mktplace/nft/collection/detail",
            params={"slug": "untitled-382568"},
            timeout=TIMEOUT
        )
        data = response.json()
        if data.get("code") == 0:
            stats = data.get("data", {}).get("stats", {})
            floor_price = stats.get("floorPrice")
            change_24h = stats.get("floorPriceChg24")
            print(f"✓ Floor: {floor_price} BNB")
            return {"floor_price": floor_price, "change_24h": change_24h}
    except Exception as e:
        print(f"⚠ OKX: {e}")
    return None

def get_transfers_from_etherscan():
    """Coba Etherscan V2"""
    if not ETHERSCAN_V2_API_KEY:
        return None, None
    
    try:
        print(f"  → Etherscan V2...")
        params = {
            "chainid": CHAIN_ID,
            "module": "account",
            "action": "tokentx",
            "address": WATCHED_WALLET,
            "contractaddress": CONTRACT_ADDRESS,
            "page": 1,
            "offset": 50,
            "sort": "desc",
            "apikey": ETHERSCAN_V2_API_KEY
        }
        response = requests.get(
            "https://api.etherscan.io/v2/api",
            params=params,
            timeout=TIMEOUT
        )
        data = response.json()
        if data.get("status") == "1":
            print(f"    ✓ Etherscan OK ({len(data['result'])})")
            return data.get("result", []), "Etherscan V2"
    except Exception as e:
        print(f"    ⚠ {e}")
    return None, None

def get_transfers_from_bscscan():
    """Coba BSCScan"""
    try:
        print(f"  → BSCScan...")
        params = {
            "module": "account",
            "action": "tokentx",
            "address": WATCHED_WALLET,
            "contractaddress": CONTRACT_ADDRESS,
            "page": 1,
            "offset": 50,
            "sort": "desc"
        }
        response = requests.get(
            "https://api.bscscan.com/api",
            params=params,
            timeout=TIMEOUT
        )
        data = response.json()
        if data.get("status") == "1":
            print(f"    ✓ BSCScan OK ({len(data['result'])})")
            return data.get("result", []), "BSCScan"
    except Exception as e:
        print(f"    ⚠ {e}")
    return None, None

def get_token_transfers():
    """Try APIs"""
    global last_api_used
    
    print(f"📡 Fetching...")
    
    transfers, api = get_transfers_from_etherscan()
    if transfers is not None:
        last_api_used = api
        return transfers
    
    transfers, api = get_transfers_from_bscscan()
    if transfers is not None:
        last_api_used = api
        return transfers
    
    print("  ✗ All failed")
    last_api_used = "FAILED"
    return []

def convert_bnb_to_usd(bnb_amount, bnb_price):
    try:
        return f"${float(bnb_amount) * bnb_price:.4f}"
    except:
        return "N/A"

async def check_for_transfers():
    """Main check"""
    global bnb_price_cache, last_price_update
    
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    now = datetime.now()
    if last_price_update is None or (now - last_price_update) > timedelta(minutes=10):
        bnb_price_cache = get_bnb_price_usd()
        last_price_update = now
    
    floor_prices = get_floor_prices()
    if floor_prices:
        floor_prices_cache.update(floor_prices)
    
    transfers = get_token_transfers()
    
    if not transfers:
        print("  ℹ No transfers")
        return
    
    print(f"✓ Processing {len(transfers)}")
    
    for token_id, token_info in WATCHED_TOKEN_IDS.items():
        token_transfers = [tx for tx in transfers if tx.get("tokenID") == token_id]
        
        for tx in token_transfers:
            tx_hash = tx.get("hash")
            
            if tx_hash in tracked_txhashes:
                continue
            
            tracked_txhashes.add(tx_hash)
            print(f"  🚨 NEW: Token ID {token_id}")
            
            from_addr = tx.get("from", "?")[:10]
            to_addr = tx.get("to", "?")[:10]
            value = tx.get("value", "0")
            block = tx.get("blockNumber", "?")
            
            floor_price_bnb = floor_prices_cache.get("floor_price", "N/A")
            price_change = floor_prices_cache.get("change_24h", "N/A")
            
            floor_price_usd = "N/A"
            if floor_price_bnb != "N/A" and bnb_price_cache:
                floor_price_usd = convert_bnb_to_usd(floor_price_bnb, bnb_price_cache)
            
            msg = f"""
🚨 <b>NFT TRANSFER!</b>

{token_info['emoji']} <b>{token_info['name']}</b>
📊 Token ID: {token_id}
🎯 {token_info['rarity']}

💰 <b>Floor Price:</b>
   <code>{floor_price_bnb} BNB</code> (~{floor_price_usd})
   24H: {price_change}%

📤 From: <code>{from_addr}...</code>
📥 To: <code>{to_addr}...</code>
📦 Qty: {value}
📍 Block: {block}

🔗 https://bscscan.com/tx/{tx_hash}

📡 {last_api_used}
            """
            
            await send_notification(msg)

async def main():
    """Main loop"""
    global bot
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("\n" + "=" * 60)
    print("🤖 B402 NFT TRACKER (RAILWAY DIRECT)")
    print("=" * 60)
    print(f"Wallet: {WATCHED_WALLET}")
    print(f"Token ID 1 & 2")
    print("=" * 60 + "\n")
    
    await send_notification(
        f"🤖 <b>Bot Started!</b>\n\n"
        f"Monitoring: Token ID 1 & 2"
    )
    
    try:
        while True:
            await check_for_transfers()
            await asyncio.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n❌ Stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        await send_notification(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
