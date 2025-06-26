"""Basic example of using the CryptoSenti client."""

import asyncio
import logging

from cryptosenti import CryptoSentiConfig, SentimentClient

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def main():
    """Main example function."""
    # Create configuration
    config = CryptoSentiConfig(
        hub_url="https://crypto.pysenti.com/sentimentHub", log_level="INFO"
    )

    # Create client
    client = SentimentClient(config)

    # Define event handlers
    def on_summary_received(summary):
        print("\n=== NEWS SUMMARY ===")
        print(f"Importance: {summary.importance * 10}%")
        print(f"Timestamp: {summary.timestamp}")
        print(f"Key Themes: {', '.join(summary.key_themes_trends)}")
        print(f"Sentiment Summary: {summary.sentiment_summary}")
        print(
            f"Impactful Events: {', '.join(summary.impactful_events_and_implications)}"
        )
        print(f"Actionable Insights: {', '.join(summary.actionable_insights)}")
        print("==================\n")

    def on_sentiment_received(sentiment):
        print("\n=== SENTIMENT DATA ===")
        print(f"Headline: {sentiment.news.headline}")
        print(f"Sentiment: {sentiment.sentiment}")
        print(f"Confidence: {sentiment.confidence * 10}%")
        print(f"Emotion: {sentiment.emotion}")
        print(f"Strength: {sentiment.strength * 10}%")
        print(f"Explanation: {sentiment.explanation}")
        print("====================\n")

    def on_connection_changed(connected):
        if connected:
            print("✅ Connected to crypto.pysenti.com SignalR hub")
        else:
            print("❌ Disconnected from SignalR hub")

    # Register event handlers
    client.on_summary_received(on_summary_received)
    client.on_sentiment_received(on_sentiment_received)
    client.on_connection_changed(on_connection_changed)

    try:
        # Connect to the hub
        await client.connect()

        # Join SignalR groups to receive updates
        await client.join_summary_group()
        await client.join_sentiment_group()

        print("🚀 Connected and listening for updates...")
        print("Press Ctrl+C to stop")

        # Keep the connection alive and listen for updates
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️  Stopping client...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up
        await client.disconnect()
        print("👋 Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
