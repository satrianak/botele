# B402 NFT Telegram Bot - BIDIRECTIONAL (Monitor IN & OUT)
# Monitor transfers FROM AND TO wallet kita

import requests
import asyncio
from telegram import Bot
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = "7925753319:AAEWkxrivRuDQHiau8fVQ9hPkOlgvGU5i9c"
TELEGRAM_CHAT_ID = "519076139"
ETHERSCAN_V2_API_KEY = "QKYIDZDBII9I4H8M2UFEZFF8A38J38WAQF"

WATCHED_WALLET = "0x39Dcdd14A0c40E19Cd8c892fD00E9e7963CD49D3"
CONTRACT_ADDRESS = "0xafcD15f17D042eE3dB94CdF6530A97bf32A74E02"

WATCHED_TOKEN_IDS = {
    "0": {"name": "Bronze", "emoji": "🥉", "rarity": "Common (94%)"},
    "1": {"name": "Silver", "emoji": "🥈", "rarity": "Langka (5%)"},
    "2": {"name": "Gold", "emoji": "🏆", "rarity": "Sangat Langka (1%)"}
}

CHECK_INTERVAL = 60
CHAIN_ID = "56"
TIMEOUT = 15

tracked_txhashes = set()
bot = None
floor_prices_cache = {}
bnb_price_cache = None
last_price_update = None

async def send_notification(message: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
        print(f"✓ Notif sent")
    except Exception as e:
        print(f"✗ Error: {e}")

def get_bnb_price():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "binancecoin", "vs_currencies": "usd"},
            timeout=TIMEOUT
        )
        data = response.json()
        if "binancecoin" in data:
            price = data["binancecoin"]["usd"]
            print(f"✓ BNB: ${price:.2f}")
            return price
    except Exception as e:
        print(f"⚠ Price error: {e}")
    return None

def get_floor_price():
    try:
        response = requests.get(
            "https://web3.okx.com/api/v5/mktplace/nft/collection/detail",
            params={"slug": "untitled-382568"},
            timeout=TIMEOUT
        )
        data = response.json()
        if data.get("code") == 0:
            stats = data.get("data", {}).get("stats", {})
            return {
                "price": stats.get("floorPrice"),
                "change24h": stats.get("floorPriceChg24")
            }
    except Exception as e:
        print(f"⚠ Floor error: {e}")
    return None

def get_transfers():
    print(f"📡 Fetching...")
    
    # Try Etherscan
    try:
        if ETHERSCAN_V2_API_KEY:
            print(f"  → Etherscan...")
            params = {
                "chainid": CHAIN_ID,
                "module": "account",
                "action": "tokentx",
                "address": WATCHED_WALLET,
                "contractaddress": CONTRACT_ADDRESS,
                "page": 1,
                "offset": 100,
                "sort": "desc",
                "apikey": ETHERSCAN_V2_API_KEY
            }
            response = requests.get("https://api.etherscan.io/v2/api", params=params, timeout=TIMEOUT)
            data = response.json()
            if data.get("status") == "1":
                print(f"    ✓ OK ({len(data['result'])})")
                return data.get("result", [])
    except Exception as e:
        print(f"    ⚠ Error: {e}")
    
    # Try BSCScan
    try:
        print(f"  → BSCScan...")
        params = {
            "module": "account",
            "action": "tokentx",
            "address": WATCHED_WALLET,
            "contractaddress": CONTRACT_ADDRESS,
            "page": 1,
            "offset": 100,
            "sort": "desc"
        }
        response = requests.get("https://api.bscscan.com/api", params=params, timeout=TIMEOUT)
        data = response.json()
        if data.get("status") == "1":
            print(f"    ✓ OK ({len(data['result'])})")
            return data.get("result", [])
    except Exception as e:
        print(f"    ⚠ Error: {e}")
    
    print("  ✗ All failed")
    return []

def is_watched_transfer(tx):
    """Check if transfer involves WATCHED_WALLET (FROM or TO)"""
    from_addr = tx.get("from", "").lower()
    to_addr = tx.get("to", "").lower()
    wallet = WATCHED_WALLET.lower()
    
    # Return True jika wallet kita ada di FROM atau TO
    return from_addr == wallet or to_addr == wallet

def get_direction(tx):
    """Tentukan arah transfer (IN atau OUT)"""
    from_addr = tx.get("from", "").lower()
    wallet = WATCHED_WALLET.lower()
    
    if from_addr == wallet:
        return "OUT (Kirim)"
    else:
        return "IN (Terima)"

async def check_transfers():
    global bnb_price_cache, last_price_update
    
    print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    now = datetime.now()
    if last_price_update is None or (now - last_price_update) > timedelta(minutes=10):
        bnb_price_cache = get_bnb_price()
        last_price_update = now
    
    floor_data = get_floor_price()
    if floor_data:
        floor_prices_cache.update(floor_data)
    
    transfers = get_transfers()
    if not transfers:
        print("  ℹ No transfers")
        return
    
    print(f"✓ Processing {len(transfers)}")
    
    for token_id, token_info in WATCHED_TOKEN_IDS.items():
        # Filter: token_id match AND wallet involved
        token_txs = [tx for tx in transfers 
                     if tx.get("tokenID") == token_id and is_watched_transfer(tx)]
        
        if token_txs:
            print(f"  Found {len(token_txs)} of Token ID {token_id}")
        
        for tx in token_txs:
            tx_hash = tx.get("hash")
            if tx_hash in tracked_txhashes:
                continue
            
            tracked_txhashes.add(tx_hash)
            
            from_addr = tx.get("from", "?")[:10]
            to_addr = tx.get("to", "?")[:10]
            value = tx.get("value", "0")
            block = tx.get("blockNumber", "?")
            direction = get_direction(tx)
            
            floor_price = floor_prices_cache.get("price", "N/A")
            change_24h = floor_prices_cache.get("change24h", "N/A")
            
            floor_usd = "N/A"
            if floor_price != "N/A" and bnb_price_cache:
                try:
                    floor_usd = f"${float(floor_price) * bnb_price_cache:.4f}"
                except:
                    pass
            
            print(f"  🚨 NEW: Token {token_id} - {direction} - {tx_hash[:10]}")
            
            msg = f"""
🚨 <b>NFT TRANSFER!</b>

{token_info['emoji']} <b>{token_info['name']}</b>
📊 Token ID: {token_id}
🎯 {token_info['rarity']}

📍 <b>Direction: {direction}</b>

💰 <b>Floor Price:</b>
   <code>{floor_price} BNB</code> (~{floor_usd})
   24H: {change_24h}%

📤 From: <code>{from_addr}...</code>
📥 To: <code>{to_addr}...</code>
📦 Qty: {value}
📍 Block: {block}

🔗 https://bscscan.com/tx/{tx_hash}
            """
            
            await send_notification(msg)

async def main():
    global bot
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    print("\n" + "=" * 60)
    print("🤖 B402 NFT TRACKER (BIDIRECTIONAL)")
    print("=" * 60)
    print(f"Wallet: {WATCHED_WALLET}")
    print(f"Tokens: 0 (Bronze), 1 (Silver), 2 (Gold)")
    print(f"Mode: Monitor IN + OUT transfers")
    print("=" * 60 + "\n")
    
    await send_notification(
        f"🤖 <b>Bot Started! (BIDIRECTIONAL)</b>\n\n"
        f"Monitoring:\n"
        f"✓ Token ID 0, 1, 2\n"
        f"✓ Transfers IN & OUT"
    )
    
    try:
        while True:
            await check_transfers()
            await asyncio.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n❌ Stopped")
    except Exception as e:
        print(f"❌ Fatal: {e}")
        await send_notification(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
