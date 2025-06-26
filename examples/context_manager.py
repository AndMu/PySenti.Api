"""Example using the client as a context manager."""

import asyncio
import logging

from cryptosenti import SentimentClient

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """Example using async context manager."""

    # Define handlers
    async def handle_summary(summary):
        print(f"📊 Summary received - Importance: {summary.importance}")
        print(f"   Sentiment: {summary.sentiment_summary}")

    async def handle_sentiment(sentiment):
        print(
            f"💭 Sentiment: {sentiment.sentiment} for '{sentiment.news.headline[:50]}...'"
        )

    # Use client as context manager for automatic cleanup
    try:
        async with SentimentClient() as client:
            # Register handlers
            client.on_summary_received(handle_summary)
            client.on_sentiment_received(handle_sentiment)

            print("🎯 Listening for crypto sentiment updates...")
            print("Press Ctrl+C to stop")

            # Listen for updates
            await asyncio.sleep(3600)  # Run for 1 hour

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
