# Bithumb market collector

Public-market data only. No API key, account data or trading actions.

1. Create a **public** GitHub repository (do not upload personal data).
2. Upload `collect.py` and `.github/workflows/collect.yml` maintaining paths.
3. Repository Settings > Pages > Build and deployment > Source: **GitHub Actions**.
4. Actions > Collect verified Bithumb market data > **Run workflow**.
5. After a successful run, verify `https://USERNAME.github.io/REPOSITORY/latest.json` displays `status: ok`, `collected_at_kst`, prices, and trade timestamps.
6. Share that public JSON URL in ChatGPT. **Do not change the existing automation until the JSON URL can be read and timestamps validated from the automation environment.**

Runs every 15 minutes in UTC. GitHub scheduled runs may be delayed or dropped; freshness must always be checked. Every successful run publishes the complete latest snapshot. A failed run does not publish new data, so the old JSON can become stale. The script rejects missing ticker/candle data and excludes incomplete candles. Do not use published market prices to calculate actual Bithumb collateral values without account details.
