"""SignalR client for CryptoSenti API."""

import asyncio
import logging
from typing import Callable, Optional, Any, Dict

from pysignalr.client import SignalRClient

from .config import CryptoSentiConfig
from .models import NewsSummary, SentimentData


logger = logging.getLogger(__name__)


class SentimentClient:
    """SignalR client for PySenti sentiment analysis."""
    
    def __init__(self, config: Optional[CryptoSentiConfig] = None):
        """Initialize the sentiment client.
        
        Args:
            config: Configuration for the client. If None, uses default config.
        """
        self.config = config or CryptoSentiConfig()
        self._client: Optional[SignalRClient] = None
        self._connection_lock = asyncio.Lock()
        self._is_connected = False
        self._connected_ev = asyncio.Event()
        self._client_task: Optional[asyncio.Task] = None

        # Event handlers
        self._summary_handlers: list[Callable[[NewsSummary], None]] = []
        self._sentiment_handlers: list[Callable[[SentimentData], None]] = []
        self._connection_handlers: list[Callable[[bool], None]] = []

        # Setup logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format=self.config.log_format
        )

    async def connect(self) -> None:
        """Connect to the SignalR hub."""
        async with self._connection_lock:
            if self._is_connected:
                logger.info("Already connected to SignalR hub")
                return

            try:
                # Setup SignalR client
                self._client = SignalRClient(
                    url=self.config.hub_url
                )

                # Register event handlers using the correct pysignalr API
                self._client.on_open(self._on_connected)
                self._client.on_close(self._on_disconnected)
                self._client.on_error(self._on_error)
                self._client.on("SummaryReceived", self._on_summary_received)
                self._client.on("SentimentReceived", self._on_sentiment_received)

                # Start the client task (this replaces the old connect method)
                self._client_task = asyncio.create_task(self._client.run())

                # Wait for connection with timeout
                try:
                    await asyncio.wait_for(self._connected_ev.wait(), timeout=self.config.connection_timeout)
                    logger.info("Successfully connected to SignalR hub")
                except asyncio.TimeoutError:
                    await self._cleanup()
                    raise ConnectionError("Failed to connect to SignalR hub within timeout")

            except:
                logger.exception(f"Failed to connect to SignalR hub")
                await self._cleanup()
                raise

    async def disconnect(self) -> None:
        """Disconnect from the SignalR hub."""
        async with self._connection_lock:
            if not self._is_connected:
                return

            try:
                # Cancel the client task (this handles disconnection)
                if self._client_task:
                    self._client_task.cancel()
                    try:
                        await self._client_task
                    except asyncio.CancelledError:
                        pass

            except:
                logger.exception(f"Error during disconnect")
            finally:
                await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources."""
        self._is_connected = False
        self._connected_ev.clear()
        self._client = None
        self._client_task = None

    async def join_summary_group(self) -> None:
        """Join the summary SignalR group."""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected")

        try:
            await self._client.send("JoinSummaryGroup", [])
            logger.info("Joined summary group")
        except:
            logger.exception(f"Failed to join summary group")
            raise

    async def join_sentiment_group(self) -> None:
        """Join the sentiment SignalR group."""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected")

        try:
            await self._client.send("JoinSentimentGroup", [])
            logger.info("Joined sentiment group")
        except:
            logger.exception(f"Failed to join sentiment group")
            raise

    def on_summary_received(self, handler: Callable[[NewsSummary], None]) -> None:
        """Register a handler for summary received events.

        Args:
            handler: Function to call when a summary is received.
        """
        self._summary_handlers.append(handler)

    def on_sentiment_received(self, handler: Callable[[SentimentData], None]) -> None:
        """Register a handler for sentiment received events.

        Args:
            handler: Function to call when sentiment data is received.
        """
        self._sentiment_handlers.append(handler)

    def on_connection_changed(self, handler: Callable[[bool], None]) -> None:
        """Register a handler for connection state changes.

        Args:
            handler: Function to call when connection state changes.
                     Receives True for connected, False for disconnected.
        """
        self._connection_handlers.append(handler)

    async def _on_summary_received(self, data: Dict[str, Any]) -> None:
        """Handle summary received from SignalR."""
        try:
            summary = NewsSummary.model_validate(data)
            logger.debug(f"Received summary: {summary.importance}")

            # Call all registered handlers
            for handler in self._summary_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(summary)
                    else:
                        handler(summary)
                except:
                    logger.exception(f"Error in summary handler")

        except:
            logger.exception(f"Failed to parse summary data")

    async def _on_sentiment_received(self, data: Dict[str, Any]) -> None:
        """Handle sentiment data received from SignalR."""
        try:
            sentiment = SentimentData.model_validate(data)
            logger.debug(f"Received sentiment for news {sentiment.correlation_id}")

            # Call all registered handlers
            for handler in self._sentiment_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(sentiment)
                    else:
                        handler(sentiment)
                except:
                    logger.exception(f"Error in sentiment handler")

        except Exception as e:
            logger.exception(f"Failed to parse sentiment data: {e}")

    async def _on_connected(self) -> None:
        """Handle SignalR connection established."""
        logger.info("SignalR connection established")
        self._is_connected = True
        self._connected_ev.set()  # Signal that connection is ready

        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(True)
                else:
                    handler(True)
            except:
                logger.exception(f"Error in connection handler")

    async def _on_disconnected(self) -> None:
        """Handle SignalR connection lost."""
        logger.warning("SignalR connection lost")
        self._is_connected = False
        self._connected_ev.clear()

        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(False)
                else:
                    handler(False)
            except:
                logger.exception(f"Error in connection handler")

    async def _on_error(self, message) -> None:
        """Handle SignalR errors."""
        error_text = getattr(message, 'error', str(message))
        logger.error(f"SignalR error: {error_text}")
    
    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._is_connected
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()