import json, io, sys, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 solana-dashboard'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or '{}')
    except Exception as e:
        return {'error': str(e)}

# DeFiLlama protocol/Solana
d = get('https://api.llama.fi/protocol/solana')
print('keys:', list(d.keys())[:30])
print()
for k in ('name', 'symbol', 'url', 'chain', 'tvl', 'tvlChange', 'mcap', 'fdv', 'listedAt', 'chains', 'metrics'):
    if k in d:
        print(f'{k}: {str(d[k])[:200]}')

# v2/chains solana entry
chains = get('https://api.llama.fi/v2/chains')
for c in chains:
    if c.get('name', '').lower() == 'solana':
        print()
        print('v2/chains SOLANA:', json.dumps(c, indent=1)[:600])
        break

# stablecoin data
sc = get('https://stablecoins.llama.fi/stablecoincharts/Solana?stablecoin=1')
print()
print('stablecoin charts keys:', list(sc.keys())[:5] if isinstance(sc, dict) else type(sc))
