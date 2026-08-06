# Solana Ecosystem Report

*Generated: 2026-08-06T13:18:07.714104+00:00 UTC | Source: on-chain RPC + DeFiLlama + exchange tickers*

## 1. Network Performance

| Metric | Value |
|--------|-------|
| Slot | 437590255 |
| Epoch | 1012 |
| Slot index in epoch | 406256 / 432000 |
| TPS (recent sample) | 3710 |
| Block time (latest slot) | 1786022199 |

## 2. Validators

| Metric | Value |
|--------|-------|
| Active validators | 693 |
| Delinquent validators | 7 |
| Total staked | 434,423,483 SOL |
| Active stake | 434,421,657 SOL |
| Delinquent stake | 1,826 SOL |

**Top validators by stake:**

| # | Validator | Stake | Commission |
|---|-----------|-------|------------|
| 1 | `Fd7btgySsrju…` | 16,808,220 SOL | 7% |
| 2 | `HEL1USMZKAL2…` | 16,003,205 SOL | 0% |
| 3 | `JUPiTERrZqgf…` | 12,472,697 SOL | 5% |
| 4 | `DRpbCBMxVnDK…` | 12,265,636 SOL | 0% |
| 5 | `C8Bey3LKVJHV…` | 9,189,333 SOL | 7% |

## 3. Economic Indicators

| Indicator | Value |
|-----------|-------|
| SOL price (USDT) | $72.94 |
| SOL 24h change | -1.28% |
| 24h high / low | $74.82 / $72.88 |
| 24h volume | $41.20M |
| Chain TVL (DeFiLlama) | $4.76B |
| Protocol mcap (DeFiLlama) | $42.57B |
| SOL supply (total) | 631,629,084,966,970,624 SOL |
| SOL circulating | 581,306,136,258,693,376 SOL |

## 4. Data Sources

- **On-chain:** Solana RPC (`getSlot`, `getEpochInfo`, `getRecentPerformanceSamples`, `getVoteAccounts`, `getSupply`)
- **TVL:** DeFiLlama (`api.llama.fi/v2/chains`, `protocol/solana`)
- **Price/volume:** Gate.io spot ticker (`SOL_USDT`)
- **Stablecoins:** DeFiLlama stablecoin charts (Solana)

## 5. Methodology & Automation

- Data refresh: configurable interval via scheduled GitHub Actions (default daily 04:00 UTC) + manual dispatch
- RPC snapshot runs on an overseas runner; off-chain sources run anywhere
- Anomaly detection: threshold-based alerts on price moves >10%, TPS <1500, validator delinquency >10%
- Outputs: this Markdown report, machine-readable JSON, interactive HTML dashboard