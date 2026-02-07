"""
🌙 Moon Dev's API Handler
Built with love by Moon Dev 🚀

API Documentation: https://moondev.com/docs

Available Endpoints:
-------------------
CORE:
- /health                               - Service health check (no auth)
- /api/liquidations/{timeframe}.json    - Liquidation data (10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d)
- /api/liquidations/stats.json          - Aggregated liquidation stats
- /api/positions.json                   - Top 50 longs/shorts across ALL symbols (updates every 1s)
- /api/positions/all.json               - All 148 symbols with top 50 positions each (500KB, updates every 60s)
- /api/whales.json                      - Recent whale trades ($25k+)
- /api/whale_addresses.txt              - Plain text whale address list
- /api/events.json                      - Real-time blockchain events
- /api/contracts.json                   - Contract registry with metadata

TICK DATA:
- /api/ticks/stats.json                 - Collection stats and summary
- /api/ticks/latest.json                - Current prices for all symbols
- /api/ticks/{symbol}_{timeframe}.json  - Historical ticks (symbols: btc, eth, hype, sol, xrp)
                                          (timeframes: 10m, 1h, 4h, 24h, 7d)

ORDER FLOW & TRADES (tracking: BTC, ETH, HYPE, SOL, XRP):
- /api/trades.json                      - Recent 500 trades (real-time)
- /api/large_trades.json                - Large trades >$100k (24h)
- /api/orderflow.json                   - Order flow imbalance by timeframe + per coin
- /api/orderflow/stats.json             - Service stats (uptime, trades/sec)
- /api/imbalance/5m.json                - 5-min buy/sell imbalance
- /api/imbalance/15m.json               - 15-min imbalance
- /api/imbalance/1h.json                - 1-hour imbalance
- /api/imbalance/4h.json                - 4-hour imbalance
- /api/imbalance/24h.json               - 24-hour imbalance

SMART MONEY:
- /api/smart_money/rankings.json        - Top 100 smart + Bottom 100 dumb money
- /api/smart_money/leaderboard.json     - Top 50 performers with details
- /api/smart_money/signals_10m.json     - Trading signals (10 min)
- /api/smart_money/signals_1h.json      - Trading signals (1 hour)
- /api/smart_money/signals_24h.json     - Trading signals (24 hour)

MULTI-EXCHANGE LIQUIDATIONS:
- /api/all_liquidations/{timeframe}.json     - Combined liquidations from ALL exchanges
- /api/all_liquidations/stats.json           - Combined stats across all exchanges
- /api/binance_liquidations/{timeframe}.json - Binance Futures liquidations
- /api/bybit_liquidations/{timeframe}.json   - Bybit liquidations
- /api/okx_liquidations/{timeframe}.json     - OKX liquidations
  (timeframes: 10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d)

HIP3 LIQUIDATIONS (Stocks, Commodities, Indices, FX):
- /api/hip3_liquidations/{timeframe}.json    - HIP3 liquidations (10m, 1h, 24h, 7d)
- /api/hip3_liquidations/stats.json          - HIP3 liquidation statistics
  Categories: Stocks (TSLA, NVDA, AAPL, etc.), Commodities (GOLD, SILVER, OIL),
              Indices (XYZ100), FX (EUR, JPY)

HIP3 MARKET DATA (Multi-Dex: Stocks, Commodities, Indices, FX, Crypto):
- /api/hip3/meta                             - All 51 symbols from all 4 dexes with current prices
- /api/hip3_ticks/stats.json                 - Tick collector stats with dex breakdown
- /api/hip3_ticks/{dex}_{ticker}.json        - Individual tick data (e.g., xyz_tsla.json, hyna_btc.json)
  Dexes: xyz (27 stocks/commodities/FX), flx (7), hyna (12 crypto), km (5 US indices)

HYPERLIQUID USER DATA:
- get_user_positions(address)           - Get positions via Hyperliquid API (direct)

MOON DEV USER API (from local node - FAST!):
- /api/user/{address}/positions         - Get positions via Moon Dev API
- /api/user/{address}/fills             - Get historical fills (limit: 100-2000, -1 for all)

MARKET DATA (replaces Hyperliquid rate-limited calls!):
- /api/prices                           - All 224 coin prices + funding rates + open interest
- /api/price/{coin}                     - Quick price for single coin (best bid/ask/mid/spread)
- /api/orderbook/{coin}                 - Full L2 orderbook (~20 levels each side)
- /api/account/{address}                - Full account state (positions, margin, withdrawable)
- /api/fills/{address}                  - Trade fills in Hyperliquid-compatible format
- /api/candles/{coin}                   - OHLCV candles (1m, 5m, 15m, 1h, 4h, 1d)

HLP (HYPERLIQUIDITY PROVIDER) DATA:
- /api/hlp/positions                    - All 7 HLP strategy positions + combined net exposure
                                          (optional: ?include_strategies=false for summary only)
- /api/hlp/trades                       - Historical HLP trade fills (5,000+ collected)
- /api/hlp/trades/stats                 - Trade volume/fee statistics
- /api/hlp/positions/history            - Position snapshots over time
- /api/hlp/liquidators                  - Liquidator activation events
- /api/hlp/deltas                       - Net exposure changes over time
- /api/hlp/sentiment                    - THE BIG ONE! Net delta with z-scores and signals
- /api/hlp/liquidators/status           - Real-time liquidator status (active/idle + PnL)
- /api/hlp/market-maker                 - Strategy B tracker for BTC/ETH/SOL
- /api/hlp/timing                       - Hourly/session profitability analysis
- /api/hlp/correlation                  - Delta-price correlation by coin

Authentication:
--------------
- Header (recommended): X-API-Key: YOUR_API_KEY
- Query param: ?api_key=YOUR_API_KEY

Rate Limits: 3,600 requests/min | Data updates every 30 seconds | 60-day retention

Need an API key? https://moondev.com
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class MoonDevAPI:
    """🌙 Moon Dev's API Client"""

    def __init__(self, api_key=None, base_url="https://api.moondev.com"):
        self.api_key = api_key or os.getenv('MOONDEV_API_KEY')
        self.base_url = base_url
        self.headers = {'X-API-Key': self.api_key} if self.api_key else {}
        self.session = requests.Session()

    def _get(self, endpoint, auth_required=True):
        """Make GET request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = self.headers if auth_required else {}

        response = self.session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response

    # ==================== HEALTH ====================
    def health(self):
        """Check API health status (no auth required)"""
        response = self._get("/health", auth_required=False)
        return response.json()

    # ==================== LIQUIDATIONS ====================
    def get_liquidations(self, timeframe="1h"):
        """Get liquidation data for specified timeframe (10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d)"""
        response = self._get(f"/api/liquidations/{timeframe}.json")
        return response.json()

    def get_liquidation_stats(self):
        """Get aggregated liquidation stats across all timeframes"""
        response = self._get("/api/liquidations/stats.json")
        return response.json()

    # ==================== POSITIONS ====================
    def get_positions(self):
        """Get large positions near liquidation ($200k+) - top 50 across ALL symbols"""
        response = self._get("/api/positions.json")
        return response.json()

    def get_all_positions(self):
        """Get ALL positions for all 148 symbols - top 50 longs/shorts per symbol

        Returns dict with symbols key containing all symbol data.
        Access specific symbol: data['symbols']['BTC'], data['symbols']['HYPE'], etc.
        """
        response = self._get("/api/positions/all.json")
        return response.json()

    # ==================== WHALES ====================
    def get_whales(self):
        """Get recent whale trades ($25k+)"""
        response = self._get("/api/whales.json")
        return response.json()

    def get_whale_addresses(self):
        """Get plain text list of known whale addresses"""
        response = self._get("/api/whale_addresses.txt")
        addresses = response.text.strip().split('\n')
        return [addr.strip() for addr in addresses if addr.strip()]

    def get_buyers(self):
        """Get recent $5k+ buyers on HYPE/SOL/XRP/ETH (buyers only, no sells)"""
        response = self._get("/api/buyers.json")
        return response.json()

    def get_depositors(self):
        """Get all Hyperliquid depositors - canonical list of every address that bridged USDC"""
        response = self._get("/api/depositors.json")
        return response.json()

    # ==================== EVENTS ====================
    def get_events(self):
        """Get real-time blockchain events (Transfers, Swaps, Deposits, etc.)"""
        response = self._get("/api/events.json")
        return response.json()

    # ==================== CONTRACTS ====================
    def get_contracts(self):
        """Get contract registry with metadata and activity tracking"""
        response = self._get("/api/contracts.json")
        return response.json()

    # ==================== TICK DATA ====================
    def get_tick_stats(self):
        """Get tick data collection stats and summary"""
        response = self._get("/api/ticks/stats.json")
        return response.json()

    def get_tick_latest(self):
        """Get latest prices for all symbols"""
        response = self._get("/api/ticks/latest.json")
        return response.json()

    def get_ticks(self, symbol="BTC", duration="1h", limit=10000, start_time=None, end_time=None):
        """
        Get historical tick data for any of 80 tracked symbols.

        Args:
            symbol: Any tracked symbol (BTC, ETH, SOL, DOGE, FARTCOIN, TRUMP, etc.)
                   Use get_candle_symbols() to see all 80 available symbols
            duration: Time window - 10m, 1h, 4h, 24h, 7d (default: 1h)
            limit: Max ticks to return (default: 10000)
            start_time: Start time in Unix ms (optional, overrides duration)
            end_time: End time in Unix ms (optional)

        Returns:
            dict with:
                - symbol: Symbol queried
                - duration: Time window
                - tick_count: Number of ticks returned
                - latest_price: Most recent price
                - ticks: List of tick objects [{t, p, dt}, ...]
        """
        params = [f"duration={duration}", f"limit={limit}"]
        if start_time is not None:
            params.append(f"startTime={start_time}")
        if end_time is not None:
            params.append(f"endTime={end_time}")
        query = "?" + "&".join(params)
        response = self._get(f"/api/ticks/{symbol.upper()}{query}")
        return response.json()

    # ==================== ORDER FLOW & TRADES ====================
    def get_trades(self):
        """Get recent 500 trades (real-time)"""
        response = self._get("/api/trades.json")
        return response.json()

    def get_large_trades(self):
        """Get large trades >$100k (24h)"""
        response = self._get("/api/large_trades.json")
        return response.json()

    def get_orderflow(self):
        """Get order flow imbalance by timeframe + per coin"""
        response = self._get("/api/orderflow.json")
        return response.json()

    def get_orderflow_stats(self):
        """Get order flow service stats (uptime, trades/sec)"""
        response = self._get("/api/orderflow/stats.json")
        return response.json()

    def get_imbalance(self, timeframe="1h"):
        """Get buy/sell imbalance (5m, 15m, 1h, 4h, 24h)"""
        response = self._get(f"/api/imbalance/{timeframe}.json")
        return response.json()

    # ==================== USER POSITIONS (HYPERLIQUID) ====================
    def get_user_positions(self, address):
        """
        Get all open positions for a specific Hyperliquid wallet address.

        Args:
            address: Hyperliquid wallet address (e.g., "0x...")

        Returns:
            dict with 'assetPositions' list and 'marginSummary'

        Example response structure:
            {
                'assetPositions': [
                    {
                        'position': {
                            'coin': 'BTC',
                            'szi': '0.5',  # size (positive=long, negative=short)
                            'entryPx': '45000.0',
                            'positionValue': '22500.0',
                            'unrealizedPnl': '500.0',
                            'liquidationPx': '40000.0',
                            'leverage': {'value': 10}
                        }
                    }
                ],
                'marginSummary': {
                    'accountValue': '50000.0',
                    'totalNtlPos': '22500.0'
                }
            }
        """
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "clearinghouseState", "user": address}

        print(f"📡 Moon Dev: Fetching positions for {address[:6]}...{address[-4:]}")
        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    # ==================== MOON DEV USER API (LOCAL NODE) ====================
    def get_user_positions_api(self, address):
        """
        Get all open positions for a Hyperliquid wallet via Moon Dev's API.

        This uses Moon Dev's local node data - faster and includes additional processing.

        Args:
            address: Hyperliquid wallet address (e.g., "0x...")

        Returns:
            dict with positions, margin summary, and account details
        """
        response = self._get(f"/api/user/{address}/positions")
        return response.json()

    def get_user_fills(self, address, limit=100):
        """
        Get historical fills/trades for a Hyperliquid wallet via Moon Dev's API.

        This uses Moon Dev's local node data - scans hourly fill archives.
        Extremely fast: ~300ms even for 32,000+ fills!

        Args:
            address: Hyperliquid wallet address (e.g., "0x...")
            limit: Number of fills to return (default: 100, max: 2000, use -1 for ALL fills)

        Returns:
            dict with:
                - fills: list of fill objects with trade details
                - total: total number of fills found
                - limit: limit that was applied
                - address: wallet address queried

        Example fill object:
            {
                'coin': 'BTC',
                'px': '45000.0',           # execution price
                'sz': '0.1',               # size
                'side': 'B',               # B=Buy, S=Sell
                'time': 1704067200000,     # timestamp ms
                'startPosition': '0.5',    # position before
                'dir': 'Open Long',        # direction description
                'closedPnl': '0',          # realized PnL if closing
                'hash': 'abc123...',       # transaction hash
                'tid': 12345,              # trade ID
                'fee': '1.5'               # fee paid
            }
        """
        params = f"?limit={limit}" if limit != 100 else ""
        response = self._get(f"/api/user/{address}/fills{params}")
        return response.json()

    # ==================== POSITION SNAPSHOTS ====================
    def get_position_snapshots(self, symbol, hours=24, limit=1000, min_distance_pct=None, max_distance_pct=None, side=None):
        """
        Get historical position snapshots for positions near liquidation.

        Tracks positions within 15% of liquidation price with minimum $10k value.
        Snapshots are taken every 1 minute.

        Args:
            symbol: Symbol to query (BTC, ETH, SOL, XRP, HYPE)
            hours: Lookback period in hours (default: 24)
            limit: Max records to return (default: 1000)
            min_distance_pct: Filter by minimum distance to liquidation %
            max_distance_pct: Filter by maximum distance to liquidation %
            side: Filter by position side ('long' or 'short')

        Returns:
            dict with snapshots and metadata
        """
        params = f"?hours={hours}&limit={limit}"
        if min_distance_pct is not None:
            params += f"&min_distance_pct={min_distance_pct}"
        if max_distance_pct is not None:
            params += f"&max_distance_pct={max_distance_pct}"
        if side is not None:
            params += f"&side={side}"
        response = self._get(f"/api/position_snapshots/symbol/{symbol}{params}")
        return response.json()

    def get_position_snapshot_stats(self, hours=24):
        """
        Get aggregate statistics for position snapshots across all tracked symbols.

        Args:
            hours: Lookback period in hours (default: 24)

        Returns:
            dict with:
                - overall: total snapshots, unique users, avg distance
                - by_symbol: per-symbol breakdown
                - top_10_closest: positions closest to liquidation
                - scan_metadata: recent scan info
        """
        params = f"?hours={hours}"
        response = self._get(f"/api/position_snapshots/stats{params}")
        return response.json()

    # ==================== MARKET DATA (NO RATE LIMITS!) ====================
    def get_prices(self):
        """
        Get all coin prices, funding rates, and open interest.

        This replaces Hyperliquid's rate-limited metaAndAssetCtxs call.
        No rate limits - goes through Moon Dev's node!

        Returns:
            dict with:
                - timestamp: When data was fetched
                - count: Number of coins (224)
                - prices: Dict of coin -> price (e.g., {"BTC": "93200.0", "ETH": "3175.0"})
                - funding_rates: Dict of coin -> funding rate
                - open_interest: Dict of coin -> open interest
        """
        response = self._get("/api/prices")
        return response.json()

    def get_price(self, coin):
        """
        Get quick price for a single coin.

        Args:
            coin: Coin symbol (e.g., "BTC", "ETH", "SOL")

        Returns:
            dict with:
                - coin: Symbol
                - timestamp: When data was fetched
                - best_bid: Best bid price
                - best_ask: Best ask price
                - best_bid_size: Size at best bid
                - best_ask_size: Size at best ask
                - mid_price: (bid + ask) / 2
                - spread: ask - bid
                - spread_bps: Spread in basis points
        """
        response = self._get(f"/api/price/{coin}")
        return response.json()

    def get_orderbook(self, coin):
        """
        Get full L2 orderbook for a coin (~20 levels each side).

        This replaces Hyperliquid's rate-limited l2Book call.
        No rate limits - goes through Moon Dev's node!

        Args:
            coin: Coin symbol (e.g., "BTC", "ETH", "SOL")

        Returns:
            dict with:
                - coin: Symbol
                - timestamp: When data was fetched
                - levels: [[bids], [asks]] - bids sorted high->low, asks sorted low->high
                  Each level: {"px": price, "sz": size, "n": order_count}
                - best_bid: Best bid price
                - best_ask: Best ask price
                - mid_price: (bid + ask) / 2
                - spread: ask - bid
                - spread_bps: Spread in basis points
                - bid_depth: Number of bid levels
                - ask_depth: Number of ask levels
        """
        response = self._get(f"/api/orderbook/{coin}")
        return response.json()

    def get_account(self, address):
        """
        Get full account state for any Hyperliquid wallet.

        This replaces Hyperliquid's rate-limited clearinghouseState call.
        No rate limits - goes through Moon Dev's node!

        Args:
            address: Wallet address (e.g., "0x...")

        Returns:
            dict with:
                - address: Wallet address
                - timestamp: When data was fetched
                - marginSummary: Account value, total position, margin used
                - crossMarginSummary: Cross margin details
                - assetPositions: List of all open positions with full details
                - withdrawable: Available to withdraw
        """
        response = self._get(f"/api/account/{address}")
        return response.json()

    def get_fills(self, address, limit=100):
        """
        Get trade fills for any wallet in Hyperliquid-compatible format.

        This is the DROP-IN REPLACEMENT for Hyperliquid's userFills call.
        Uses Moon Dev's local node - faster and no rate limits!

        Args:
            address: Wallet address (e.g., "0x...")
            limit: Number of fills to return (default: 100)

        Returns:
            list of fill objects in Hyperliquid format:
            [
                {
                    "tid": 293951512222,      # Trade ID
                    "time": 1768392000752,    # Timestamp (ms)
                    "coin": "BTC",            # Symbol
                    "side": "B" or "A",       # B=Buy, A=Sell (Ask)
                    "px": "94000.0",          # Price
                    "sz": "0.1",              # Size
                    "closedPnl": "100.50",    # Realized PnL
                    "dir": "Open Long",       # Direction description
                    "crossed": false,         # Whether crossed the spread
                    "fee": "1.5",             # Fee paid
                    "oid": 293951512222       # Order ID
                }
            ]
        """
        params = f"?limit={limit}" if limit != 100 else ""
        response = self._get(f"/api/fills/{address}{params}")
        return response.json()

    def get_candle_symbols(self):
        """
        Get list of all 80 tracked symbols available for candles/ticks.

        Symbols are selected based on $750k+ daily volume.

        Returns:
            dict with:
                - symbols: List of symbol strings (e.g., ["AAVE", "BTC", "DOGE", ...])
                - count: Number of tracked symbols (80)
                - volume_threshold: Minimum daily volume for inclusion ($750k)
                - intervals: Available candle intervals (1m, 5m, 15m, 1h, 4h, 1d)
                - symbol_details: Dict with per-symbol metadata
        """
        response = self._get("/api/candles/symbols")
        return response.json()

    def get_candles(self, coin, interval="5m", start_time=None, end_time=None):
        """
        Get OHLCV candles for any of 80 tracked symbols in Hyperliquid-compatible format.

        80 symbols tracked including majors, DeFi, L2s, and memes.
        Use get_candle_symbols() to see full list.

        Categories:
            - Major: BTC, ETH, SOL, XRP, DOGE, LTC, ADA, DOT, LINK, AVAX, BNB...
            - DeFi: AAVE, UNI, CRV, LDO, PENDLE, JUP, MORPHO, ONDO, ENA...
            - L2/Alt L1: ARB, OP, SUI, SEI, APT, NEAR, TON, TIA, MOVE, BERA...
            - Memes: HYPE, FARTCOIN, PUMP, WIF, POPCAT, PENGU, TRUMP...

        Args:
            coin: Any tracked symbol (use get_candle_symbols() for full list)
            interval: Candle interval - 1m, 5m, 15m, 1h, 4h, 1d (default: 5m)
            start_time: Start timestamp in ms (optional)
            end_time: End timestamp in ms (optional)

        Returns:
            list of candle objects:
            [
                {
                    "t": 1767787200000,    # Open time (ms)
                    "T": 1767790799999,    # Close time (ms)
                    "s": "BTC",            # Symbol
                    "i": "5m",             # Interval
                    "o": "92194.5",        # Open price
                    "h": "92232.5",        # High price
                    "l": "92049.5",        # Low price
                    "c": "92056.5",        # Close price
                    "v": "0",              # Volume (from ticks, may be 0)
                    "n": 239               # Number of price updates
                }
            ]
        """
        params = [f"interval={interval}"]
        if start_time is not None:
            params.append(f"startTime={start_time}")
        if end_time is not None:
            params.append(f"endTime={end_time}")
        query = "?" + "&".join(params) if params else ""
        response = self._get(f"/api/candles/{coin}{query}")
        return response.json()

    # ==================== HLP (HYPERLIQUIDITY PROVIDER) ====================
    def get_hlp_positions(self, include_strategies=True):
        """
        Get all HLP (HyperLiquidity Provider) positions across all 7 strategies.

        This endpoint provides a comprehensive view of Hyperliquid's market-making
        strategies including combined net exposure calculations.

        Args:
            include_strategies: If True, include individual strategy breakdowns.
                              If False, return summary only (faster response).

        Returns:
            dict with:
                - summary: Total account value (~$210M), position counts, net exposure
                - combined_positions: NET positions across all strategies (longs - shorts)
                - strategies: Individual HLP strategy details (if include_strategies=True)

        HLP Strategies tracked:
            - HLP Strategy A (main market maker)
            - HLP Strategy B (secondary market maker)
            - HLP Liquidator 1-4 (liquidation bots)
            - HLP Strategy X (experimental)

        Example combined_position:
            {
                'coin': 'BTC',
                'net_size': 10.5,           # positive=net long, negative=net short
                'net_value': 500000.0,      # USD value of net position
                'long_strategies': ['HLP Strategy A'],
                'short_strategies': ['HLP Strategy B'],
                'total_long': 15.0,
                'total_short': 4.5
            }
        """
        params = "" if include_strategies else "?include_strategies=false"
        response = self._get(f"/api/hlp/positions{params}")
        return response.json()

    def get_hlp_trades(self, limit=100):
        """
        Get historical HLP trade fills across all strategies.

        Args:
            limit: Number of trades to return (default: 100)

        Returns:
            dict with:
                - trades: List of trade fill objects
                - total: Total trades available
                - strategies: Which strategies have trades
        """
        params = f"?limit={limit}" if limit != 100 else ""
        response = self._get(f"/api/hlp/trades{params}")
        return response.json()

    def get_hlp_trade_stats(self):
        """
        Get HLP trade volume and fee statistics.

        Returns:
            dict with:
                - total_trades: Total number of trades collected
                - total_volume: Total USD volume traded
                - total_fees: Total fees paid
                - date_range: First and last trade timestamps
                - by_strategy: Volume breakdown by strategy
                - by_coin: Volume breakdown by coin
        """
        response = self._get("/api/hlp/trades/stats")
        return response.json()

    def get_hlp_position_history(self, hours=24):
        """
        Get historical position snapshots over time.

        Args:
            hours: Number of hours of history (default: 24)

        Returns:
            dict with:
                - snapshots: List of position snapshots with timestamps
                - interval: Time between snapshots
        """
        params = f"?hours={hours}" if hours != 24 else ""
        response = self._get(f"/api/hlp/positions/history{params}")
        return response.json()

    def get_hlp_liquidators(self):
        """
        Get HLP liquidator activation events.

        Monitors when liquidator accounts become active (non-idle).

        Returns:
            dict with:
                - events: List of liquidator activation events
                - liquidators: Current status of each liquidator account
        """
        response = self._get("/api/hlp/liquidators")
        return response.json()

    def get_hlp_deltas(self, hours=24):
        """
        Get HLP net exposure (delta) changes over time.

        Args:
            hours: Number of hours of history (default: 24)

        Returns:
            dict with:
                - deltas: Time series of net exposure values
                - current: Current net exposure
                - change_24h: 24-hour change in exposure
        """
        params = f"?hours={hours}" if hours != 24 else ""
        response = self._get(f"/api/hlp/deltas{params}")
        return response.json()

    def get_hlp_sentiment(self):
        """
        Get HLP sentiment indicator - THE BIG ONE!

        Returns z-scores showing how positioned HLP is vs historical norms.
        Z-score of 2.2 = HLP is 2.2σ more long than usual = retail heavily SHORT.

        Returns:
            dict with:
                - net_delta: Current net exposure
                - z_score: Standard deviations from mean
                - signal: Human readable signal (e.g., "Retail heavily SHORT")
                - percentile: Where current delta falls historically
        """
        response = self._get("/api/hlp/sentiment")
        return response.json()

    def get_hlp_liquidator_status(self):
        """
        Get real-time HLP liquidator status.

        Shows which liquidators are active/idle and their PnL.

        Returns:
            dict with liquidator addresses, status (active/idle), and PnL data
        """
        response = self._get("/api/hlp/liquidators/status")
        return response.json()

    def get_hlp_market_maker(self):
        """
        Get HLP Strategy B market maker tracker for BTC/ETH/SOL.

        Returns:
            dict with market maker positions and activity for major coins
        """
        response = self._get("/api/hlp/market-maker")
        return response.json()

    def get_hlp_timing(self):
        """
        Get HLP timing analysis - hourly/session profitability.

        Returns:
            dict with profitability breakdown by hour and trading session
        """
        response = self._get("/api/hlp/timing")
        return response.json()

    def get_hlp_correlation(self):
        """
        Get HLP delta-price correlation analysis by coin.

        Returns:
            dict with correlation data showing how HLP delta relates to price moves
        """
        response = self._get("/api/hlp/correlation")
        return response.json()

    def get_hlp_delta(self):
        """
        Get live HLP net delta calculation.

        Shows real-time HLP positioning across all vaults.
        Polls every 30 seconds, snapshots every 60 seconds.

        Returns:
            dict with:
                - net_delta: Current net exposure (positive=LONG, negative=SHORT)
                - long_exposure: Total long exposure in USD
                - short_exposure: Total short exposure in USD
                - position_count: Number of positions across vaults
                - timestamp: Last update time
        """
        response = self._get("/api/hlp/delta")
        return response.json()

    def get_hlp_flips(self):
        """
        Get historical HLP flip events (when delta crosses zero).

        A flip occurs when HLP's net delta crosses from long to short
        or vice versa. Each flip is recorded with BTC/ETH price context.

        Returns:
            list of flip events:
            [
                {
                    "datetime": "2026-01-14T15:30:00Z",
                    "from_direction": "long",
                    "to_direction": "short",
                    "from_delta": 500000,
                    "to_delta": -200000,
                    "hold_duration_hours": 4.5,
                    "btc_price": 95000,
                    "eth_price": 3300
                }
            ]
        """
        response = self._get("/api/hlp/flips")
        return response.json()

    def get_hlp_flip_stats(self):
        """
        Get aggregated HLP flip statistics.

        Provides analysis of historical flip patterns including
        average hold durations, flip frequency, and performance metrics.

        Returns:
            dict with:
                - total_flips: Number of recorded flips
                - avg_hold_duration_hours: Average time between flips
                - long_to_short_count: Number of long→short flips
                - short_to_long_count: Number of short→long flips
                - current_direction: Current HLP direction (long/short)
                - current_hold_hours: Hours in current direction
        """
        response = self._get("/api/hlp/flip-stats")
        return response.json()

    # ==================== SMART MONEY ====================
    def get_smart_money_rankings(self):
        """Get Top 100 smart money + Bottom 100 dumb money rankings"""
        response = self._get("/api/smart_money/rankings.json")
        return response.json()

    def get_smart_money_leaderboard(self):
        """Get Top 50 performers with details"""
        response = self._get("/api/smart_money/leaderboard.json")
        return response.json()

    def get_smart_money_signals(self, timeframe="1h"):
        """Get smart money trading signals (10m, 1h, 24h)"""
        response = self._get(f"/api/smart_money/signals_{timeframe}.json")
        return response.json()

    # ==================== MULTI-EXCHANGE LIQUIDATIONS ====================
    def get_all_liquidations(self, timeframe="1h"):
        """
        Get COMBINED liquidation data from ALL exchanges (Hyperliquid, Binance, Bybit, OKX).

        Args:
            timeframe: 10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d

        Returns:
            dict with liquidation events from all exchanges, sorted by USD value
        """
        response = self._get(f"/api/all_liquidations/{timeframe}.json")
        return response.json()

    def get_all_liquidation_stats(self):
        """
        Get combined liquidation stats across ALL exchanges.

        Returns:
            dict with:
                - total_count: Total liquidations across all exchanges
                - total_volume: Combined USD volume
                - by_exchange: Breakdown by exchange (hyperliquid, binance, bybit, okx)
                - by_side: Long vs short breakdown
        """
        response = self._get("/api/all_liquidations/stats.json")
        return response.json()

    def get_binance_liquidations(self, timeframe="1h"):
        """
        Get Binance Futures liquidation data.

        Args:
            timeframe: 10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d
        """
        response = self._get(f"/api/binance_liquidations/{timeframe}.json")
        return response.json()

    def get_bybit_liquidations(self, timeframe="1h"):
        """
        Get Bybit liquidation data.

        Args:
            timeframe: 10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d
        """
        response = self._get(f"/api/bybit_liquidations/{timeframe}.json")
        return response.json()

    def get_okx_liquidations(self, timeframe="1h"):
        """
        Get OKX liquidation data.

        Args:
            timeframe: 10m, 1h, 4h, 12h, 24h, 2d, 7d, 14d, 30d
        """
        response = self._get(f"/api/okx_liquidations/{timeframe}.json")
        return response.json()

    # ==================== HIP3 LIQUIDATIONS ====================
    def get_hip3_liquidations(self, timeframe="1h"):
        """
        Get HIP3 liquidation data (Stocks, Commodities, Indices, FX).

        HIP3 covers traditional finance assets on Hyperliquid:
        - Stocks: TSLA, NVDA, AAPL, META, MSFT, GOOGL, AMZN, AMD, INTC, PLTR,
                  COIN, HOOD, MSTR, ORCL, MU, NFLX, RIVN, BABA
        - Commodities: GOLD, SILVER, COPPER, CL (Oil), NATGAS, URANIUM
        - Indices: XYZ100 (Nasdaq proxy)
        - FX: EUR, JPY

        Args:
            timeframe: 10m, 1h, 24h, 7d

        Returns:
            list of liquidation events with:
                - symbol: Asset symbol (TSLA, GOLD, etc.)
                - side: 'long' or 'short'
                - size: Position size
                - price: Liquidation price
                - value_usd: USD value of liquidation
                - category: 'stocks', 'commodities', 'indices', or 'fx'
                - timestamp: Event timestamp
        """
        response = self._get(f"/api/hip3_liquidations/{timeframe}.json")
        return response.json()

    def get_hip3_liquidation_stats(self):
        """
        Get HIP3 liquidation statistics.

        Returns:
            dict with:
                - total_count: Total liquidations
                - total_volume: Total USD volume liquidated
                - long_count: Number of long liquidations
                - short_count: Number of short liquidations
                - long_volume: USD volume of long liquidations
                - short_volume: USD volume of short liquidations
                - by_category: Breakdown by category (stocks, commodities, indices, fx)
                - by_symbol: Breakdown by individual symbol
                - top_symbols: Top symbols by liquidation volume
        """
        response = self._get("/api/hip3_liquidations/stats.json")
        return response.json()

    # ==================== HIP3 MARKET DATA (Multi-Dex) ====================
    def get_hip3_meta(self, include_delisted=False):
        """
        Get all HIP3 symbols from all 4 dexes with current prices.

        51 symbols across 4 dexes:
            - xyz (27): Stocks, commodities, FX, indices (TSLA, NVDA, GOLD, EUR, XYZ100)
            - flx (7): Stocks, commodities, XMR (XMR, GOLD, SILVER, OIL)
            - hyna (12): Crypto (BTC, ETH, HYPE, SOL, FARTCOIN, PUMP)
            - km (5): US indices (US500, USTECH, SMALL2000)

        Args:
            include_delisted: If True, includes delisted symbols (default: False)

        Returns:
            dict with:
                - count: Total number of symbols
                - dexes: Dict organized by dex prefix
                - symbols: List of all symbol objects with prices
                - categories: Breakdown by category (stocks, indices, commodities, fx, crypto)

        Symbol format: {dex}:{ticker} (e.g., xyz:TSLA, hyna:BTC, km:US500)
        """
        params = "?include_delisted=true" if include_delisted else ""
        response = self._get(f"/api/hip3/meta{params}")
        return response.json()

    def get_hip3_tick_stats(self):
        """
        Get HIP3 tick collector statistics with dex breakdown.

        Returns:
            dict with:
                - total_symbols: Total symbols being tracked
                - total_ticks: Total ticks collected
                - by_dex: Breakdown by dex (xyz, flx, hyna, km)
                - by_category: Breakdown by category
                - last_update: Last collection timestamp
        """
        response = self._get("/api/hip3_ticks/stats.json")
        return response.json()

    def get_hip3_ticks(self, dex, ticker):
        """
        Get raw tick data for a specific HIP3 symbol.

        Args:
            dex: Dex prefix (xyz, flx, hyna, km)
            ticker: Symbol ticker (tsla, btc, gold, us500, etc.) - case insensitive

        Returns:
            dict/list with tick data for the symbol

        Examples:
            get_hip3_ticks("xyz", "tsla")   # Tesla stock
            get_hip3_ticks("xyz", "gold")   # Gold commodity
            get_hip3_ticks("hyna", "btc")   # Bitcoin
            get_hip3_ticks("km", "us500")   # S&P 500 index
        """
        response = self._get(f"/api/hip3_ticks/{dex.lower()}_{ticker.lower()}.json")
        return response.json()


# ==================== TEST SUITE ====================
def test_all():
    """🌙 Moon Dev API Mass Test Suite"""

    print("=" * 60)
    print("🌙 Moon Dev API Mass Test Suite 🚀")
    print("=" * 60)

    api = MoonDevAPI()

    if not api.api_key:
        print("❌ No API key found! Set MOONDEV_API_KEY in .env")
        return

    print(f"✅ API Key loaded (ends with ...{api.api_key[-4:]})")
    print()

    # ==================== 1. HEALTH CHECK ====================
    print("=" * 60)
    print("🏥 1. HEALTH CHECK")
    print("=" * 60)
    try:
        health = api.health()
        print(f"✅ Health: {health}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    print()

    # ==================== 2. LIQUIDATIONS ====================
    print("=" * 60)
    print("💥 2. LIQUIDATION DATA")
    print("=" * 60)
    timeframes = ["10m", "1h", "4h", "24h"]
    for tf in timeframes:
        try:
            data = api.get_liquidations(tf)
            if isinstance(data, dict):
                stats = data.get('stats', data)
                total_count = stats.get('total_count', 'N/A')
                total_usd = stats.get('total_value_usd', stats.get('total_usd', 'N/A'))
                if isinstance(total_usd, (int, float)):
                    print(f"✅ {tf}: {total_count:,} liqs | ${total_usd:,.0f}")
                else:
                    print(f"✅ {tf}: {total_count} liquidations")
        except Exception as e:
            print(f"❌ {tf} failed: {e}")
    print()

    # ==================== 3. POSITIONS ====================
    print("=" * 60)
    print("💰 3. LARGE POSITIONS ($200k+)")
    print("=" * 60)
    try:
        positions = api.get_positions()
        if isinstance(positions, dict):
            total = positions.get('total_positions', 0)
            print(f"✅ Found {total} positions tracked")
    except Exception as e:
        print(f"❌ Positions failed: {e}")
    print()

    # ==================== 4. WHALE ADDRESSES ====================
    print("=" * 60)
    print("🐋 4. WHALE ADDRESSES")
    print("=" * 60)
    try:
        addresses = api.get_whale_addresses()
        print(f"✅ Found {len(addresses)} whale addresses")
    except Exception as e:
        print(f"❌ Whale addresses failed: {e}")
    print()

    # ==================== 5. EVENTS ====================
    print("=" * 60)
    print("⚡ 5. BLOCKCHAIN EVENTS")
    print("=" * 60)
    try:
        events = api.get_events()
        if isinstance(events, dict):
            stats = events.get('stats', {})
            total = stats.get('total_events', 0)
            by_type = stats.get('events_by_type', {})
            print(f"✅ Found {total:,} total events")
            print(f"   📊 By type: {', '.join(f'{k}:{v}' for k,v in list(by_type.items())[:5])}")
    except Exception as e:
        print(f"❌ Events failed: {e}")
    print()

    # ==================== 6. CONTRACTS ====================
    print("=" * 60)
    print("📜 6. CONTRACT REGISTRY")
    print("=" * 60)
    try:
        contracts = api.get_contracts()
        if isinstance(contracts, dict):
            contract_list = contracts.get('contracts', [])
            high_value = contracts.get('high_value_count', 0)
            print(f"✅ Found {len(contract_list)} contracts ({high_value} high-value)")
    except Exception as e:
        print(f"❌ Contracts failed: {e}")
    print()

    # ==================== 7. TICK DATA ====================
    print("=" * 60)
    print("📈 7. TICK DATA")
    print("=" * 60)
    try:
        stats = api.get_tick_stats()
        symbols = stats.get('symbols', [])
        collector = stats.get('collector_stats', {})
        ticks = collector.get('ticks_collected', 0)
        print(f"✅ Tick Stats: {ticks:,} ticks collected for {symbols}")
    except Exception as e:
        print(f"⚠️  Tick stats: {e}")

    try:
        latest = api.get_tick_latest()
        print(f"✅ Latest prices:")
        for symbol, price in list(latest.items())[:5]:
            if isinstance(price, (int, float)):
                print(f"   {symbol}: ${price:,.2f}")
            elif isinstance(price, dict):
                p = price.get('price', price.get('last_price', 'N/A'))
                print(f"   {symbol}: ${p:,.2f}" if isinstance(p, (int, float)) else f"   {symbol}: {price}")
    except Exception as e:
        print(f"⚠️  Latest prices: {e}")

    for symbol in ["btc", "eth"]:
        try:
            ticks = api.get_ticks(symbol, "1h")
            if isinstance(ticks, list):
                print(f"✅ {symbol.upper()} 1h ticks: {len(ticks)} records")
            elif isinstance(ticks, dict):
                count = ticks.get('count', len(ticks.get('ticks', [])))
                print(f"✅ {symbol.upper()} 1h ticks: {count} records")
        except Exception as e:
            print(f"⚠️  {symbol} ticks: {e}")
    print()

    # ==================== 8. ORDER FLOW & TRADES ====================
    print("=" * 60)
    print("📊 8. ORDER FLOW & TRADES")
    print("=" * 60)
    try:
        stats = api.get_orderflow_stats()
        print(f"✅ Order Flow Stats: {stats}")
    except Exception as e:
        print(f"⚠️  Order flow stats: {e}")

    try:
        trades = api.get_trades()
        if isinstance(trades, list):
            print(f"✅ Recent trades: {len(trades)} trades")
            for t in trades[:3]:
                symbol = t.get('symbol', t.get('coin', '?'))
                side = t.get('side', '?')
                val = t.get('value', t.get('usd_value', t.get('sz', 0)))
                print(f"   {symbol} {side} ${val:,.0f}" if isinstance(val, (int, float)) else f"   {t}")
        elif isinstance(trades, dict):
            trade_list = trades.get('trades', [])
            print(f"✅ Recent trades: {len(trade_list)} trades")
    except Exception as e:
        print(f"⚠️  Recent trades: {e}")

    try:
        large = api.get_large_trades()
        if isinstance(large, list):
            print(f"✅ Large trades (>$100k): {len(large)} trades")
            for t in large[:3]:
                symbol = t.get('symbol', t.get('coin', '?'))
                side = t.get('side', '?')
                val = t.get('value', t.get('usd_value', 0))
                print(f"   {symbol} {side} ${val:,.0f}" if isinstance(val, (int, float)) else f"   {t}")
        elif isinstance(large, dict):
            trade_list = large.get('trades', [])
            print(f"✅ Large trades: {len(trade_list)} trades")
    except Exception as e:
        print(f"⚠️  Large trades: {e}")

    try:
        orderflow = api.get_orderflow()
        print(f"✅ Order flow: {orderflow}")
    except Exception as e:
        print(f"⚠️  Order flow: {e}")

    for tf in ["5m", "1h", "24h"]:
        try:
            imbalance = api.get_imbalance(tf)
            if isinstance(imbalance, dict):
                buy = imbalance.get('buy_volume', imbalance.get('buy', 0))
                sell = imbalance.get('sell_volume', imbalance.get('sell', 0))
                ratio = imbalance.get('ratio', imbalance.get('imbalance', 'N/A'))
                print(f"✅ {tf} imbalance: Buy ${buy:,.0f} | Sell ${sell:,.0f} | Ratio: {ratio}" if isinstance(buy, (int, float)) else f"✅ {tf} imbalance: {imbalance}")
        except Exception as e:
            print(f"⚠️  {tf} imbalance: {e}")
    print()

    # ==================== 9. SMART MONEY ====================
    print("=" * 60)
    print("🧠 9. SMART MONEY")
    print("=" * 60)
    try:
        rankings = api.get_smart_money_rankings()
        if isinstance(rankings, dict):
            smart = rankings.get('smart_money', rankings.get('top', []))
            dumb = rankings.get('dumb_money', rankings.get('bottom', []))
            print(f"✅ Rankings: {len(smart)} smart | {len(dumb)} dumb money wallets")
    except Exception as e:
        print(f"⚠️  Rankings: {e}")

    try:
        leaderboard = api.get_smart_money_leaderboard()
        if isinstance(leaderboard, dict):
            leaders = leaderboard.get('leaderboard', leaderboard.get('top', []))
            print(f"✅ Leaderboard: {len(leaders)} top performers")
            for l in leaders[:3]:
                addr = l.get('address', '')[:10] + '...' if l.get('address') else 'N/A'
                pnl = l.get('pnl', l.get('total_pnl', 0))
                print(f"   {addr} | PnL: ${pnl:,.0f}" if isinstance(pnl, (int, float)) else f"   {l}")
        elif isinstance(leaderboard, list):
            print(f"✅ Leaderboard: {len(leaderboard)} entries")
    except Exception as e:
        print(f"⚠️  Leaderboard: {e}")

    for tf in ["10m", "1h", "24h"]:
        try:
            signals = api.get_smart_money_signals(tf)
            if isinstance(signals, dict):
                signal_list = signals.get('signals', [])
                print(f"✅ Signals ({tf}): {len(signal_list)} trading signals")
            elif isinstance(signals, list):
                print(f"✅ Signals ({tf}): {len(signals)} trading signals")
        except Exception as e:
            print(f"⚠️  Signals ({tf}): {e}")
    print()

    # ==================== 10. USER POSITIONS (HYPERLIQUID) ====================
    print("=" * 60)
    print("📊 10. USER POSITIONS (HYPERLIQUID)")
    print("=" * 60)
    try:
        # Test with a known active address (HLP_LONG)
        test_address = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
        positions = api.get_user_positions(test_address)
        if isinstance(positions, dict):
            asset_positions = positions.get('assetPositions', [])
            margin = positions.get('marginSummary', {})
            account_value = margin.get('accountValue', 'N/A')
            print(f"✅ Found {len(asset_positions)} positions for {test_address[:10]}...")
            if isinstance(account_value, (int, float, str)):
                print(f"   Account Value: ${float(account_value):,.2f}" if account_value != 'N/A' else f"   Account Value: {account_value}")
            for pos in asset_positions[:3]:
                if 'position' in pos:
                    p = pos['position']
                    coin = p.get('coin', '?')
                    size = float(p.get('szi', 0))
                    pnl = float(p.get('unrealizedPnl', 0))
                    direction = "LONG" if size > 0 else "SHORT"
                    print(f"   {coin} {direction} | PnL: ${pnl:,.2f}")
    except Exception as e:
        print(f"⚠️  User positions: {e}")
    print()

    # ==================== 11. USER FILLS (MOON DEV API) ====================
    print("=" * 60)
    print("📜 11. USER FILLS (MOON DEV LOCAL NODE)")
    print("=" * 60)
    try:
        test_address = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
        fills = api.get_user_fills(test_address, limit=100)
        if isinstance(fills, dict):
            fill_list = fills.get('fills', [])
            total = fills.get('total', len(fill_list))
            print(f"✅ Found {total:,} total fills for {test_address[:10]}...")
            print(f"   Showing last {len(fill_list)} fills")
            for fill in fill_list[:5]:
                coin = fill.get('coin', '?')
                side = fill.get('side', '?')
                side_str = "BUY" if side == 'B' else "SELL"
                px = float(fill.get('px', 0))
                sz = float(fill.get('sz', 0))
                pnl = float(fill.get('closedPnl', 0))
                print(f"   {coin} {side_str} {sz:.4f} @ ${px:,.2f} | PnL: ${pnl:,.2f}")
    except Exception as e:
        print(f"⚠️  User fills: {e}")
    print()

    # ==================== 12. MARKET DATA (NO RATE LIMITS!) ====================
    print("=" * 60)
    print("📈 12. MARKET DATA (NO RATE LIMITS!)")
    print("=" * 60)

    # All Prices
    try:
        prices_data = api.get_prices()
        count = prices_data.get('count', 0)
        prices = prices_data.get('prices', {})
        funding = prices_data.get('funding_rates', {})
        oi = prices_data.get('open_interest', {})
        print(f"✅ All Prices: {count} coins")
        print(f"   BTC: ${prices.get('BTC', 'N/A')} | Funding: {funding.get('BTC', 'N/A')} | OI: {oi.get('BTC', 'N/A')}")
        print(f"   ETH: ${prices.get('ETH', 'N/A')} | Funding: {funding.get('ETH', 'N/A')}")
        print(f"   SOL: ${prices.get('SOL', 'N/A')} | Funding: {funding.get('SOL', 'N/A')}")
    except Exception as e:
        print(f"⚠️  All prices: {e}")

    # Quick Price
    try:
        price_data = api.get_price("BTC")
        print(f"✅ Quick Price (BTC):")
        print(f"   Best Bid: ${price_data.get('best_bid', 'N/A')}")
        print(f"   Best Ask: ${price_data.get('best_ask', 'N/A')}")
        print(f"   Mid Price: ${price_data.get('mid_price', 'N/A')}")
        print(f"   Spread: {price_data.get('spread_bps', 'N/A')} bps")
    except Exception as e:
        print(f"⚠️  Quick price: {e}")

    # Orderbook
    try:
        ob_data = api.get_orderbook("ETH")
        levels = ob_data.get('levels', [[], []])
        print(f"✅ Orderbook (ETH):")
        print(f"   Best Bid: ${ob_data.get('best_bid', 'N/A')} | Best Ask: ${ob_data.get('best_ask', 'N/A')}")
        print(f"   Spread: {ob_data.get('spread_bps', 'N/A')} bps")
        print(f"   Depth: {len(levels[0])} bids, {len(levels[1])} asks")
        if levels[0]:
            top_bid = levels[0][0]
            print(f"   Top Bid Level: ${top_bid.get('px', 'N/A')} x {top_bid.get('sz', 'N/A')} ({top_bid.get('n', 'N/A')} orders)")
    except Exception as e:
        print(f"⚠️  Orderbook: {e}")

    # Account State
    try:
        test_address = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
        account_data = api.get_account(test_address)
        margin = account_data.get('marginSummary', {})
        positions = account_data.get('assetPositions', [])
        print(f"✅ Account State ({test_address[:10]}...):")
        print(f"   Account Value: ${float(margin.get('accountValue', 0)):,.2f}")
        print(f"   Total Position: ${float(margin.get('totalNtlPos', 0)):,.2f}")
        print(f"   Margin Used: ${float(margin.get('totalMarginUsed', 0)):,.2f}")
        print(f"   Positions: {len(positions)}")
        print(f"   Withdrawable: ${float(account_data.get('withdrawable', 0)):,.2f}")
    except Exception as e:
        print(f"⚠️  Account state: {e}")

    # Fills (Hyperliquid-compatible)
    try:
        test_address = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
        fills = api.get_fills(test_address, limit=5)
        print(f"✅ Fills ({test_address[:10]}...): {len(fills)} fills")
        if fills:
            fill = fills[0]
            side = "BUY" if fill.get('side') == 'B' else "SELL"
            print(f"   Latest: {fill.get('coin')} {side} {fill.get('sz')} @ ${fill.get('px')} | PnL: ${fill.get('closedPnl')}")
    except Exception as e:
        print(f"⚠️  Fills: {e}")

    # Candles (OHLCV)
    try:
        candles = api.get_candles("BTC", interval="1h")
        print(f"✅ Candles (BTC 1h): {len(candles)} candles")
        if candles:
            latest = candles[-1]
            print(f"   Latest: O:${latest.get('o')} H:${latest.get('h')} L:${latest.get('l')} C:${latest.get('c')}")
    except Exception as e:
        print(f"⚠️  Candles: {e}")

    # Test all candle symbols
    for symbol in ["ETH", "SOL", "HYPE", "XRP"]:
        try:
            candles = api.get_candles(symbol, interval="1h")
            if candles:
                print(f"   ✅ {symbol}: {len(candles)} candles, close: ${candles[-1].get('c')}")
        except Exception as e:
            print(f"   ⚠️  {symbol}: {e}")

    print()

    # ==================== 13. HLP (HYPERLIQUIDITY PROVIDER) ====================
    print("=" * 60)
    print("🏦 13. HLP (HYPERLIQUIDITY PROVIDER)")
    print("=" * 60)

    # HLP Positions
    try:
        hlp_data = api.get_hlp_positions(include_strategies=False)
        if isinstance(hlp_data, dict):
            summary = hlp_data.get('summary', {})
            total_value = summary.get('total_account_value', 0)
            total_positions = summary.get('total_positions', 0)
            net_exposure = summary.get('net_exposure_delta', 0)
            print(f"✅ HLP Positions:")
            print(f"   Total Account Value: ${total_value:,.0f}")
            print(f"   Total Positions: {total_positions}")
            print(f"   Net Exposure Delta: ${net_exposure:,.0f}")

            combined = hlp_data.get('combined_positions', [])
            if combined:
                print(f"   Top Combined Net Positions:")
                for pos in combined[:3]:
                    coin = pos.get('coin', '?')
                    net_size = pos.get('net_size', 0)
                    net_value = pos.get('net_value', 0)
                    direction = "LONG" if net_size > 0 else "SHORT"
                    print(f"      {coin} NET {direction}: {abs(net_size):.4f} (${abs(net_value):,.0f})")
    except Exception as e:
        print(f"⚠️  HLP positions: {e}")

    # HLP Trade Stats
    try:
        trade_stats = api.get_hlp_trade_stats()
        if isinstance(trade_stats, dict):
            total_trades = trade_stats.get('total_trades', 0)
            total_volume = trade_stats.get('total_volume', 0)
            total_fees = trade_stats.get('total_fees', 0)
            print(f"✅ HLP Trade Stats:")
            print(f"   Total Trades: {total_trades:,}")
            print(f"   Total Volume: ${total_volume:,.2f}")
            print(f"   Total Fees: ${total_fees:,.2f}")
    except Exception as e:
        print(f"⚠️  HLP trade stats: {e}")

    # HLP Trades
    try:
        trades = api.get_hlp_trades(limit=5)
        if isinstance(trades, dict):
            trade_list = trades.get('trades', [])
            total = trades.get('total', len(trade_list))
            print(f"✅ HLP Trades: {total:,} total, showing {len(trade_list)}")
            for t in trade_list[:3]:
                coin = t.get('coin', '?')
                side = t.get('side', '?')
                sz = float(t.get('sz', 0))
                px = float(t.get('px', 0))
                print(f"      {coin} {'BUY' if side == 'B' else 'SELL'} {sz:.4f} @ ${px:,.2f}")
    except Exception as e:
        print(f"⚠️  HLP trades: {e}")

    # HLP Liquidators
    try:
        liquidators = api.get_hlp_liquidators()
        if isinstance(liquidators, dict):
            liq_list = liquidators.get('liquidators', [])
            events = liquidators.get('events', [])
            active = sum(1 for l in liq_list if l.get('status') == 'active')
            print(f"✅ HLP Liquidators: {active}/{len(liq_list)} active, {len(events)} events")
    except Exception as e:
        print(f"⚠️  HLP liquidators: {e}")

    # HLP Deltas
    try:
        deltas = api.get_hlp_deltas(hours=24)
        if isinstance(deltas, dict):
            current = deltas.get('current', 0)
            change = deltas.get('change_24h', 0)
            delta_list = deltas.get('deltas', [])
            print(f"✅ HLP Deltas: Current ${current:,.0f}, 24h change ${change:,.0f}, {len(delta_list)} data points")
    except Exception as e:
        print(f"⚠️  HLP deltas: {e}")

    print()

    # ==================== 14. MULTI-EXCHANGE LIQUIDATIONS ====================
    print("=" * 60)
    print("🔥 14. MULTI-EXCHANGE LIQUIDATIONS")
    print("=" * 60)

    # Combined All Exchange Stats
    try:
        stats = api.get_all_liquidation_stats()
        if isinstance(stats, dict):
            total_count = stats.get('total_count', stats.get('count', 0))
            total_volume = stats.get('total_volume', stats.get('total_value_usd', 0))
            print(f"✅ Combined All Exchanges:")
            print(f"   Total Count: {total_count:,}")
            print(f"   Total Volume: ${total_volume:,.0f}")
            by_exchange = stats.get('by_exchange', {})
            if by_exchange:
                print(f"   By Exchange:")
                for ex, ex_stats in by_exchange.items():
                    if isinstance(ex_stats, dict):
                        ex_count = ex_stats.get('count', 0)
                        ex_vol = ex_stats.get('volume', 0)
                        print(f"      {ex}: {ex_count:,} liqs | ${ex_vol:,.0f}")
    except Exception as e:
        print(f"⚠️  All liquidation stats: {e}")

    # Per-exchange liquidations (1h sample)
    exchanges = [
        ("Binance", api.get_binance_liquidations),
        ("Bybit", api.get_bybit_liquidations),
        ("OKX", api.get_okx_liquidations),
    ]
    for name, func in exchanges:
        try:
            data = func("1h")
            if isinstance(data, list):
                print(f"✅ {name} 1h: {len(data)} liquidations")
            elif isinstance(data, dict):
                liq_list = data.get('liquidations', data.get('data', []))
                print(f"✅ {name} 1h: {len(liq_list)} liquidations")
        except Exception as e:
            print(f"⚠️  {name} 1h: {e}")

    print()

    print("=" * 60)
    print("🌙 Moon Dev API Test Complete! 🚀")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
