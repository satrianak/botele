# 🚀 B402 NFT Tracker - Railway Deployment Guide

Bot Telegram untuk monitor transfer NFT B402 (Token ID 1 & 2) dengan LIVE floor price.

---

## 📦 Files Yang Sudah Saya Buat

1. **bot.py** - Main bot script (optimized untuk Railway)
2. **requirements.txt** - Python dependencies
3. **Procfile** - Railway startup command
4. **RAILWAY_DEPLOY.md** - Panduan ini

---

## 🚀 Deploy ke Railway - Step by Step

### Step 1: Persiapan Files

1. Download semua files:
   - `bot.py`
   - `requirements.txt`
   - `Procfile`

2. (OPSIONAL) Upload ke GitHub:
   - Buat repo baru di GitHub
   - Upload 3 files di atas
   - Atau bisa deploy langsung dari local files (tanpa GitHub)

---

### Step 2: Setup Railway

1. **Buka Railway**:
   - Kunjungi https://railway.app
   - Sign up / Login dengan GitHub

2. **Create New Project**:
   - Klik "New Project"
   - Pilih salah satu:
     - "Deploy from GitHub repo" (jika sudah upload ke GitHub)
     - "Empty Project" (jika deploy dari local)

3. **Upload Files** (jika tidak pakai GitHub):
   - Klik "Empty Project"
   - Klik "+ New" → "GitHub Repo" atau "Empty Service"
   - Drag & drop 3 files (`bot.py`, `requirements.txt`, `Procfile`)

---

### Step 3: Set Environment Variables

Di Railway Dashboard:

1. Klik project Anda
2. Klik tab **"Variables"** (atau Settings → Variables)
3. Tambahkan 3 environment variables ini:

```
TELEGRAM_BOT_TOKEN = <Your Telegram Bot Token>
TELEGRAM_CHAT_ID = <Your Telegram Chat ID>
ETHERSCAN_V2_API_KEY = <Your Etherscan V2 API Key> (optional)
```

**Cara dapat credentials:**

| Variable | Cara Dapat |
|----------|-----------|
| **TELEGRAM_BOT_TOKEN** | @BotFather di Telegram → `/newbot` |
| **TELEGRAM_CHAT_ID** | @RawDataBot di Telegram → `/start` |
| **ETHERSCAN_V2_API_KEY** | https://etherscan.io/apis (optional) |

---

### Step 4: Deploy!

1. **Railway auto-detect** Python project
2. **Auto install** dependencies dari `requirements.txt`
3. **Auto run** command dari `Procfile`: `python bot.py`
4. Bot akan **mulai berjalan** otomatis

---

### Step 5: Monitor & Verify

1. **Check Logs**:
   - Di Railway dashboard → klik "Deployments"
   - Lihat logs real-time

2. **Expected Output**:
   ```
   ============================================================
   🤖 B402 NFT TRACKER (RAILWAY DEPLOYMENT)
   ============================================================
   Wallet: 0x39Dcdd14A0c40E19Cd8c892fD00E9e7963CD49D3
   Monitoring: Token ID 1 & 2
   Interval: 180s
   ============================================================
   
   ⏰ 12:30:00
   ✓ BNB: $915.00
   ✓ Floor: 0.00034 BNB
   📡 Fetching transfers...
     → BSCScan...
       ✓ BSCScan OK (5)
   ✓ Processing 5 transfers
   ```

3. **Check Telegram**:
   - Bot akan kirim pesan "🤖 B402 Bot Started!"
   - Saat ada transfer, akan dapat notifikasi otomatis

---

## ⚙️ Configuration

### Ubah Check Interval

Edit `bot.py`, line ~30:

```python
CHECK_INTERVAL = 180  # 3 menit (default)
# Ubah ke:
CHECK_INTERVAL = 300  # 5 menit (lebih hemat credit)
CHECK_INTERVAL = 60   # 1 menit (faster, lebih boros credit)
```

### Ubah Wallet yang Dimonitor

Edit `bot.py`, line ~25:

```python
WATCHED_WALLET = "0x39Dcdd14A0c40E19Cd8c892fD00E9e7963CD49D3"
# Ganti dengan wallet address baru
```

### Tambah Token ID 0 (Bronze)

Edit `bot.py`, line ~29, tambahkan:

```python
WATCHED_TOKEN_IDS = {
    "0": {"name": "Bronze Mystery Box", "emoji": "🥉", "rarity": "Common (94%)"},
    "1": {"name": "Silver Mystery Box", "emoji": "🥈", "rarity": "Langka (5%)"},
    "2": {"name": "Gold Mystery Box", "emoji": "🏆", "rarity": "Sangat Langka (1%)"}
}
```

Setelah edit, push ke GitHub atau re-deploy di Railway.

---

## 💰 Railway Free Tier

- **$5 credit per bulan** (gratis)
- Bot Python kecil biasanya pakai **~$2-3 per bulan**
- Cukup untuk monitoring 24/7
- Jika habis credit, bot akan sleep sampai bulan berikutnya

**Tips hemat credit:**
- Set CHECK_INTERVAL = 300 (5 menit) atau lebih
- Jangan jalankan multiple bots dalam 1 project

---

## 🔧 Troubleshooting

### Bot tidak start?

1. **Check Logs** di Railway:
   - Klik "Deployments" → lihat error message
   
2. **Common errors**:
   ```
   ERROR: TELEGRAM_BOT_TOKEN not set!
   ```
   → Set environment variables di Railway

### Bot berhenti tiba-tiba?

1. **Check credit** di Railway dashboard
2. **Restart** manual: Klik "Redeploy"

### API errors?

```
⚠ BSCScan: NOTOK
✗ All APIs failed
```

→ Tunggu beberapa jam, API sedang overloaded. Bot akan auto-retry.

---

## 📊 Monitoring

### Via Railway Dashboard:
- **Logs**: Real-time bot activity
- **Metrics**: CPU, Memory usage
- **Deployments**: History & status

### Via Telegram:
- Bot kirim notifikasi setiap transfer detected
- Bot kirim status saat start/stop

---

## 🚀 Next Steps

1. ✅ Deploy bot ke Railway
2. ✅ Set environment variables
3. ✅ Verify bot running (check logs + Telegram)
4. ✅ Monitor wallet untuk transfers
5. (Optional) Tambah monitoring untuk wallet lain
6. (Optional) Setup GitHub auto-deploy

---

## 📝 File Structure

```
your-project/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── Procfile           # Railway startup command
└── RAILWAY_DEPLOY.md  # This guide
```

---

## 🆘 Support

- **Railway Docs**: https://docs.railway.app/
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Issues**: Check Railway logs atau Telegram untuk error messages

---

**Selamat! Bot Anda siap running 24/7 di Railway! 🎉**
