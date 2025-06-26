# CryptoSenti

A Python client library for connecting to the PySenti crypto sentiment analysis SignalR API at [crypto.pysenti.com](https://crypto.pysenti.com).

## About

[crypto.pysenti.com](https://crypto.pysenti.com) is a real-time news sentiment analysis platform that provides live sentiment data and summaries for cryptocurrency and financial news. This Python client allows you to connect to the SignalR API and receive real-time sentiment updates and news summaries.

## Installation

```bash
pip install cryptosenti
```

## Quick Start

```python
import asyncio
from cryptosenti import SentimentClient, CryptoSentiConfig

async def main():
    # Create client with default configuration
    async with SentimentClient() as client:
        # Register event handlers
        client.on_summary_received(lambda summary: print(f"Summary: {summary.sentiment_summary}"))
        client.on_sentiment_received(lambda sentiment: print(f"Sentiment: {sentiment.sentiment}"))
        
        # Keep the connection alive
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

You can customize the client behavior using `CryptoSentiConfig`:

```python
from cryptosenti import SentimentClient, CryptoSentiConfig

config = CryptoSentiConfig(
    hub_url="https://crypto.pysenti.com/sentimentHub",
    connection_timeout=30,
    reconnect_attempts=5,
    log_level="DEBUG"
)

client = SentimentClient(config)
```

## Usage

### Connecting and Subscribing

```python
import asyncio
from cryptosenti import SentimentClient

async def main():
    client = SentimentClient()
    
    # Connect to the hub
    await client.connect()
    
    # Join SignalR groups
    await client.join_summary_group()
    await client.join_sentiment_group()
    
    # Register handlers
    client.on_summary_received(handle_summary)
    client.on_sentiment_received(handle_sentiment)
    client.on_connection_changed(handle_connection_change)
    
    # Keep alive
    await asyncio.sleep(3600)  # Run for 1 hour
    
    # Disconnect
    await client.disconnect()

def handle_summary(summary):
    print(f"Received summary with importance: {summary.importance}")
    print(f"Key themes: {', '.join(summary.key_themes_trends)}")

def handle_sentiment(sentiment):    
    print(f"Sentiment: {sentiment.sentiment}")
    print(f"Confidence: {sentiment.confidence}")

def handle_connection_change(connected):
    if connected:
        print("Connected to SignalR hub")
    else:
        print("Disconnected from SignalR hub")

if __name__ == "__main__":
    asyncio.run(main())
```

### Data Models

The library provides strongly-typed data models that match the C# backend:

#### NewsSummary
- `key_themes_trends`: Key themes and trends
- `impactful_events_and_implications`: Impactful events and implications
- `sentiment_summary`: Overall sentiment summary
- `actionable_insights`: Actionable insights
- `importance`: Importance score
- `timestamp`: When the summary was created

#### SentimentData
- `sentiment`: Sentiment value (positive/negative/neutral)
- `confidence`: Confidence score
- `explanation`: Explanation of the sentiment
- `news`: Associated news item
- `temporal`: Temporal aspect (past/present/future)
- `emotion`: Detected emotion
- `strength`: Sentiment strength

#### WorldNews
- `headline`: News headline
- `source`: News source
- `urgency`: Urgency level
- `event_date`: When the event occurred
- `type`: Type of news (breaking/regular/analysis/opinion)

## Development

### Setup

```bash
git clone https://github.com/pysenti/cryptosenti.git
cd cryptosenti
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Linting and Formatting

```bash
ruff check .
ruff format .
mypy src/
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.