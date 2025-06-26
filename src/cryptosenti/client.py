"""SignalR client for CryptoSenti API."""

import asyncio
import logging
from typing import Callable, Optional, Any, Dict

import aiohttp
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
        self._session: Optional[aiohttp.ClientSession] = None
        self._connection_lock = asyncio.Lock()
        self._is_connected = False
        
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
                self._session = aiohttp.ClientSession()
                
                # Setup SignalR client
                self._client = SignalRClient(
                    url=self.config.hub_url,
                    session=self._session
                )
                
                # Register event handlers
                self._client.on("SummaryReceived", self._on_summary_received)
                self._client.on("SentimentReceived", self._on_sentiment_received)
                self._client.on_connect = self._on_connected
                self._client.on_disconnect = self._on_disconnected
                
                # Connect with retry logic
                await self._connect_with_retry()
                
                logger.info("Successfully connected to SignalR hub")
                
            except Exception as e:
                logger.error(f"Failed to connect to SignalR hub: {e}")
                await self._cleanup()
                raise
    
    async def _connect_with_retry(self) -> None:
        """Connect with retry logic."""
        for attempt in range(self.config.reconnect_attempts):
            try:
                await self._client.connect()
                self._is_connected = True
                
                # Auto-join groups if configured
                if self.config.auto_subscribe_summary:
                    await self.join_summary_group()
                
                if self.config.auto_subscribe_sentiment:
                    await self.join_sentiment_group()
                
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.config.reconnect_attempts - 1:
                    await asyncio.sleep(self.config.reconnect_delay)
                else:
                    raise
    
    async def disconnect(self) -> None:
        """Disconnect from the SignalR hub."""
        async with self._connection_lock:
            if not self._is_connected:
                return
            
            try:
                if self._client:
                    await self._client.cl.disconnect()
                    
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                await self._cleanup()
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        self._is_connected = False
        self._client = None
        
        if self._session:
            await self._session.close()
            self._session = None
    
    async def join_summary_group(self) -> None:
        """Join the summary SignalR group."""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected")
        
        try:
            await self._client.send("JoinSummaryGroup")
            logger.info("Joined summary group")
        except Exception as e:
            logger.error(f"Failed to join summary group: {e}")
            raise
    
    async def join_sentiment_group(self) -> None:
        """Join the sentiment SignalR group."""
        if not self._client or not self._is_connected:
            raise RuntimeError("Client not connected")
        
        try:
            await self._client.send("JoinSentimentGroup")
            logger.info("Joined sentiment group")
        except Exception as e:
            logger.error(f"Failed to join sentiment group: {e}")
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
                except Exception as e:
                    logger.error(f"Error in summary handler: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to parse summary data: {e}")
    
    async def _on_sentiment_received(self, data: Dict[str, Any]) -> None:
        """Handle sentiment data received from SignalR."""
        try:
            sentiment = SentimentData.model_validate(data)
            logger.debug(f"Received sentiment for news {sentiment.news_id}")
            
            # Call all registered handlers
            for handler in self._sentiment_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(sentiment)
                    else:
                        handler(sentiment)
                except Exception as e:
                    logger.error(f"Error in sentiment handler: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to parse sentiment data: {e}")
    
    async def _on_connected(self) -> None:
        """Handle SignalR connection established."""
        logger.info("SignalR connection established")
        
        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(True)
                else:
                    handler(True)
            except Exception as e:
                logger.error(f"Error in connection handler: {e}")
    
    async def _on_disconnected(self) -> None:
        """Handle SignalR connection lost."""
        logger.warning("SignalR connection lost")
        self._is_connected = False
        
        # Notify connection handlers
        for handler in self._connection_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(False)
                else:
                    handler(False)
            except Exception as e:
                logger.error(f"Error in connection handler: {e}")
    
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