### Disclaimer
This project is for educational and research purposes only.  
It does not constitute financial advice and does not place real trades.




What the system actually does:

1.Data ingestion
- Scrapes live Reddit data using public .json endpoints
- No Reddit API keys required
- Handles rate limits, network errors, and malformed responses

2.Signal construction
- Extracts stock tickers using pattern recognition and stop-word filtering
- Computes sentiment scores from post language
- Weights sentiment by post popularity (reddit upvotes)
- Separates recent hype vs older hype using time windows
- Computes sentiment acceleration (delta)

3.Trading logic
Uses contrarian logic:
- Accelerating bullish crowd -> SELL
- Accelerating bearish crowd -> BUY
- No crowd acceleration -> NO_TRADE
- Signals are intentionally rare to reduce noise

4.Output
- Logs every run to CSV with:
Run ID, Timestamp, Ticker, Sentiment metrics, Final trading signal


# NOTE: Script is intended to be run infrequently (e.g. every 10–30 minutes)
