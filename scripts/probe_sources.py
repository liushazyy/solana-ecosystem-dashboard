import json, io, sys, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 solana-dashboard'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or '{}')
    except Exception as e:
        return None, f'ERR {e}'

tests = [
    ('DeFiLlama v2/chains', 'https://api.llama.fi/v2/chains'),
    ('DeFiLlama protocols/Solana', 'https://api.llama.fi/protocol/solana'),
    ('CoinGecko search', 'https://api.coingecko.com/api/v3/search/trending'),
    ('CoinGecko ping', 'https://api.coingecko.com/api/v3/ping'),
    ('CoinGecko coins/solana', 'https://api.coingecko.com/api/v3/coins/solana?localization=false&tickers=false&market_data=true'),
    ('CoinPaprika solana', 'https://api.coinpaprika.com/v1/tickers/sol-solana'),
    ('Binance API', 'https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT'),
    ('OKX API', 'https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT'),
    ('Gate.io API', 'https://api.gateio.ws/api/v4/spot/tickers?currency_pair=SOL_USDT'),
    ('Jupiter API', 'https://api.jup.ag/price/v2?ids=So11111111111111111111111111111111111111112'),
]
for name, url in tests:
    code, data = get(url)
    if code == 200:
        s = str(data)[:120]
        print(f'OK  {name}: {s}')
    else:
        print(f'ERR {name}: {data}')
