# Solana Ecosystem Auto-Updating Report & Interactive Dashboard

An automated, dependency-light report on the current state of the Solana
ecosystem: network performance, validator health, market economics, and
anomaly alerts — refreshed on a schedule with zero API keys required.

Built for the [Superteam Canada bounty](https://superteam.fun)
"Develop Solana Ecosystem Auto-Updating Report & Interactive Dashboard".

## Live Outputs

- **Interactive HTML dashboard** (dark theme): `reports/index.html`
- **Human-readable Markdown report**: `reports/solana_ecosystem_<date>.md`
- **Machine-readable JSON**: `reports/solana_ecosystem_<date>.json`
- **On-chain RPC snapshot**: `reports/rpc_snapshot.json`

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| Solana RPC (`api.mainnet-beta.solana.com`) | getHealth, getSlot, getBlockTime, getEpochInfo, getRecentPerformanceSamples, getVoteAccounts, getBalance, getSignaturesForAddress, getSupply | Public, no key |
| DeFiLlama (`api.llama.fi`) | Chain TVL, protocol market cap, stablecoin circulation | Public, no key |
| Gate.io (`api.gateio.ws`) | SOL/USDT spot price, 24h high/low, volume, change | Public, no key |

**No API keys required.** All sources are public endpoints; on-chain data
comes straight from Solana's RPC.

## Metrics Covered

- **Network performance:** slot, block time, epoch progress, TPS
  (from `getRecentPerformanceSamples`), transaction count
- **Validator status:** active vs delinquent validator counts, total stake,
  stake distribution, top validators by stake with commission, delinquency
  alerts
- **Economic indicators:** SOL price & 24h moves, chain TVL, protocol
  market cap, stablecoin supply, SOL total/circulating supply
- **Automation:** configurable refresh interval, scheduled GitHub Actions
  (default daily 04:00 UTC) + manual dispatch

## Anomaly Detection

Threshold-based alerts (reported in all three outputs):

- SOL price 24h move > ±10%
- TPS drop below 1500
- Validator delinquency > 10% of active validators

## Architecture

```
src/
  collector.py        # off-chain data (DeFiLlama, Gate.io) + anomaly detection
  render_markdown.py  # Markdown report generator
  render_html.py      # interactive dark-theme HTML dashboard
  main.py             # entry: python -m src.main
scripts/
  rpc_collect.py      # on-chain RPC snapshot (runs on GitHub Actions)
.github/workflows/
  rpc-collect.yml     # daily RPC refresh on overseas runner + commits back
```

**Why two paths?** The repo is built to run anywhere. Off-chain sources
(DeFiLlama, Gate.io) are reachable from any network; the Solana RPC step
runs in GitHub Actions (overseas runner) so the on-chain snapshot stays
fresh even when the local network cannot reach Solana endpoints. Both
halves are plain Python stdlib — no third-party dependencies.

## Quick Start

```bash
# 1. Collect data + render all outputs (uses local rpc_snapshot.json if present)
python -m src.main

# 2. Just refresh off-chain data
python -m src.main --collect-only

# 3. Re-render from the latest JSON without touching the network
python -m src.main --render-only

# 4. Refresh the on-chain RPC snapshot (needs Solana RPC access)
python scripts/rpc_collect.py
```

## Automation

The `rpc-collect` workflow runs daily (04:00 UTC) and on manual dispatch:

1. Checks out the repo
2. Runs `scripts/rpc_collect.py` on the GitHub-hosted (overseas) runner
3. Commits the fresh `reports/rpc_snapshot.json` back to `main`

To refresh on-chain data on demand, trigger the workflow manually:

```bash
curl -X POST https://api.github.com/repos/<owner>/solana-ecosystem-dashboard/actions/workflows/rpc-collect.yml/dispatches \
  -H "Authorization: Bearer <PAT>" -H "Content-Type: application/json" \
  -d '{"ref":"main"}'
```

## Sample Report (2026-08-06)

| Metric | Value |
|--------|-------|
| SOL price | $72.94 |
| Chain TVL | $4.76B |
| Protocol mcap | $42.57B |
| Slot | 437,590,255 |
| TPS | 3,710 |
| Active validators | 693 |
| Total staked | 434.4M SOL |
| Epoch | 1012 |

Full report: `reports/solana_ecosystem_2026-08-06.md`
