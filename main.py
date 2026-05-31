import time
import requests

TELEGRAM_BOT_TOKEN = "8816851424:AAGkZRSOH_DbjuVSr4tIK486wC9F2eKnif4"
TELEGRAM_CHAT_ID = "6205080040"
MIN_LIQUIDITY_USD = 5000.0

seen_pools = set()

def send_telegram_alert(token_name, dex, liquidity, pool_address, created_at):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = (
        f"🚨 *NEW SOLANA POOL DETECTED* 🚨\n\n"
        f"🪙 *Token:* {token_name}\n"
        f"🦅 *DEX:* {dex.upper()}\n"
        f"💧 *Liquidity:* ${float(liquidity):,.2f}\n"
        f"⏰ *Created:* {created_at}\n\n"
        f"🔗 *GeckoTerminal Chart:*\n"
        f"https://www.geckoterminal.com/solana/pools/{pool_address}\n"
        )
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending alert: {e}")

def scan_new_pools():
    api_url = "https://api.geckoterminal.com/api/v2/networks/solana/new_pools"
    headers = {"Accept": "application/json;version=20230203"}
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json().get("data", [])
            for pool in data:
                pool_id = pool.get("id")
                attributes = pool.get("attributes", {})
                if pool_id not in seen_pools:
                    seen_pools.add(pool_id )
                    name = attributes.get("name", "Unknown")
                    dex = attributes.get("dex_target", "Unknown")
                    liquidity = float(attributes.get("reserve_in_usd", 0) or 0)
                    created_at = attributes.get("pool_created_at", "Unknown")
                    pool_address = attributes.get("address")

                    if liquidity >= MIN_LIQUIDITY_USD:
                        print(f"🔥 Found Valid Launch: {name} - Liq: ${liquidity}")
                        send_telegram_alert(name, dex, liquidity, pool_address, created_at)
        elif response.status_code == 429:
            time.sleep(30)
    except Exception:
        pass

if __name__ == "__main__":
    print("🚀 Solana Alpha Sniper Bot active...")
    scan_new_pools()
    while True:
        time.sleep(30)
        scan_new_pools()
