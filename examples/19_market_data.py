"""
🌙 Moon Dev's Market Data Example
Real-time prices, orderbooks, fills, candles, and account data - NO RATE LIMITS!

Built with love by Moon Dev 🚀

These endpoints replace Hyperliquid's rate-limited API calls:
- /api/prices           → replaces metaAndAssetCtxs
- /api/price/{coin}     → quick single-coin price
- /api/orderbook/{coin} → replaces l2Book
- /api/account/{addr}   → replaces clearinghouseState
- /api/fills/{addr}     → replaces userFills (Hyperliquid-compatible format!)
- /api/candles/{coin}   → OHLCV candles (1m, 5m, 15m, 1h, 4h, 1d)

No more rate limits - all calls go through Moon Dev's node!
"""

import sys
import os

# Add parent directory to path for api.py import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import MoonDevAPI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def show_all_prices(api):
    """Display all coin prices with funding and open interest"""
    console.print("\n[bold cyan]📈 ALL PRICES (224 Coins) - Moon Dev[/bold cyan]")

    data = api.get_prices()

    # Summary
    console.print(f"\n[green]✅ Loaded {data.get('count', 0)} coins")
    console.print(f"[dim]   Timestamp: {data.get('timestamp', 'N/A')}")

    prices = data.get('prices', {})
    funding = data.get('funding_rates', {})
    oi = data.get('open_interest', {})

    # Top coins table
    table = Table(title="Top Coins", box=box.ROUNDED)
    table.add_column("Coin", style="cyan", width=8)
    table.add_column("Price", justify="right", style="green", width=14)
    table.add_column("Funding", justify="right", width=12)
    table.add_column("Open Interest", justify="right", width=14)

    top_coins = ["BTC", "ETH", "SOL", "HYPE", "XRP", "DOGE", "AVAX", "LINK"]
    for coin in top_coins:
        if coin in prices:
            price = f"${float(prices[coin]):,.2f}"
            fund = funding.get(coin, "N/A")
            if fund != "N/A":
                fund_pct = float(fund) * 100
                fund_str = f"{fund_pct:.4f}%"
                if fund_pct > 0:
                    fund_str = f"[green]{fund_str}[/green]"
                else:
                    fund_str = f"[red]{fund_str}[/red]"
            else:
                fund_str = "N/A"
            open_int = oi.get(coin, "N/A")
            if open_int != "N/A":
                open_int = f"{float(open_int):,.2f}"
            table.add_row(coin, price, fund_str, open_int)

    console.print(table)

    # Quick stats
    console.print(f"\n[yellow]💡 TIP: Use api.get_prices() to get all {data.get('count', 0)} coins at once!")
    console.print("[dim]   Replaces Hyperliquid's rate-limited metaAndAssetCtxs call")


def show_quick_price(api, coin="BTC"):
    """Display quick price for a single coin"""
    console.print(f"\n[bold cyan]💰 QUICK PRICE: {coin}[/bold cyan]")

    data = api.get_price(coin)

    panel_content = f"""
[green]Best Bid:[/green] ${data.get('best_bid', 'N/A')} (size: {data.get('best_bid_size', 'N/A')})
[red]Best Ask:[/red] ${data.get('best_ask', 'N/A')} (size: {data.get('best_ask_size', 'N/A')})
[yellow]Mid Price:[/yellow] ${data.get('mid_price', 'N/A')}
[cyan]Spread:[/cyan] ${data.get('spread', 'N/A')} ({data.get('spread_bps', 'N/A')} bps)

[dim]Timestamp: {data.get('timestamp', 'N/A')}[/dim]
"""
    console.print(Panel(panel_content, title=f"{coin} Price", border_style="cyan"))


def show_orderbook(api, coin="BTC"):
    """Display L2 orderbook for a coin"""
    console.print(f"\n[bold cyan]📚 ORDERBOOK: {coin}[/bold cyan]")

    data = api.get_orderbook(coin)
    levels = data.get('levels', [[], []])
    bids = levels[0]
    asks = levels[1]

    # Summary
    console.print(f"\n[green]✅ Best Bid: ${data.get('best_bid', 'N/A')} | Best Ask: ${data.get('best_ask', 'N/A')}")
    console.print(f"[yellow]   Mid: ${data.get('mid_price', 'N/A')} | Spread: {data.get('spread_bps', 'N/A')} bps")
    console.print(f"[dim]   Depth: {data.get('bid_depth', 0)} bids, {data.get('ask_depth', 0)} asks")

    # Orderbook table
    table = Table(title=f"{coin} Orderbook (Top 10)", box=box.ROUNDED)
    table.add_column("Bid Size", justify="right", style="green", width=12)
    table.add_column("Bid Price", justify="right", style="green", width=12)
    table.add_column("Ask Price", justify="right", style="red", width=12)
    table.add_column("Ask Size", justify="right", style="red", width=12)

    for i in range(min(10, max(len(bids), len(asks)))):
        bid_px = f"${float(bids[i]['px']):,.1f}" if i < len(bids) else ""
        bid_sz = f"{float(bids[i]['sz']):,.4f}" if i < len(bids) else ""
        ask_px = f"${float(asks[i]['px']):,.1f}" if i < len(asks) else ""
        ask_sz = f"{float(asks[i]['sz']):,.4f}" if i < len(asks) else ""
        table.add_row(bid_sz, bid_px, ask_px, ask_sz)

    console.print(table)

    console.print(f"\n[yellow]💡 TIP: Use api.get_orderbook('{coin}') for full ~20 levels each side!")
    console.print("[dim]   Replaces Hyperliquid's rate-limited l2Book call")


def show_account(api, address):
    """Display full account state"""
    console.print(f"\n[bold cyan]👤 ACCOUNT STATE[/bold cyan]")

    data = api.get_account(address)
    margin = data.get('marginSummary', {})
    positions = data.get('assetPositions', [])

    # Account summary
    account_value = float(margin.get('accountValue', 0))
    total_pos = float(margin.get('totalNtlPos', 0))
    margin_used = float(margin.get('totalMarginUsed', 0))
    withdrawable = float(data.get('withdrawable', 0))

    panel_content = f"""
[green]Account Value:[/green] ${account_value:,.2f}
[yellow]Total Position:[/yellow] ${total_pos:,.2f}
[red]Margin Used:[/red] ${margin_used:,.2f}
[cyan]Withdrawable:[/cyan] ${withdrawable:,.2f}
[dim]Positions: {len(positions)}[/dim]
"""
    console.print(Panel(panel_content, title=f"Account: {address[:10]}...{address[-4:]}", border_style="cyan"))

    # Positions table
    if positions:
        table = Table(title="Open Positions (Top 10)", box=box.ROUNDED)
        table.add_column("Coin", style="cyan", width=8)
        table.add_column("Side", width=6)
        table.add_column("Size", justify="right", width=12)
        table.add_column("Entry", justify="right", width=12)
        table.add_column("Value", justify="right", width=14)
        table.add_column("PnL", justify="right", width=14)
        table.add_column("ROE", justify="right", width=10)

        for pos_data in positions[:10]:
            pos = pos_data.get('position', {})
            coin = pos.get('coin', '?')
            size = float(pos.get('szi', 0))
            side = "[green]LONG[/green]" if size > 0 else "[red]SHORT[/red]"
            entry = f"${float(pos.get('entryPx', 0)):,.2f}"
            value = f"${float(pos.get('positionValue', 0)):,.2f}"
            pnl = float(pos.get('unrealizedPnl', 0))
            pnl_str = f"[green]${pnl:,.2f}[/green]" if pnl >= 0 else f"[red]${pnl:,.2f}[/red]"
            roe = float(pos.get('returnOnEquity', 0)) * 100
            roe_str = f"[green]{roe:.1f}%[/green]" if roe >= 0 else f"[red]{roe:.1f}%[/red]"

            table.add_row(coin, side, f"{abs(size):.4f}", entry, value, pnl_str, roe_str)

        console.print(table)

    console.print(f"\n[yellow]💡 TIP: Use api.get_account('0x...') for any Hyperliquid wallet!")
    console.print("[dim]   Replaces Hyperliquid's rate-limited clearinghouseState call")


def show_fills(api, address):
    """Display trade fills for a wallet"""
    console.print(f"\n[bold cyan]📝 FILLS (Hyperliquid-Compatible)[/bold cyan]")

    fills = api.get_fills(address, limit=10)

    console.print(f"\n[green]✅ Found {len(fills)} fills for {address[:10]}...{address[-4:]}")

    if fills:
        table = Table(title="Recent Fills", box=box.ROUNDED)
        table.add_column("Time", width=12)
        table.add_column("Coin", style="cyan", width=8)
        table.add_column("Side", width=6)
        table.add_column("Size", justify="right", width=10)
        table.add_column("Price", justify="right", width=12)
        table.add_column("PnL", justify="right", width=12)
        table.add_column("Direction", width=14)

        from datetime import datetime
        for fill in fills[:10]:
            ts = fill.get('time', 0)
            time_str = datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S') if ts else "N/A"
            coin = fill.get('coin', '?')
            side = fill.get('side', '?')
            side_str = "[green]BUY[/green]" if side == 'B' else "[red]SELL[/red]"
            sz = fill.get('sz', '0')
            px = f"${float(fill.get('px', 0)):,.2f}"
            pnl = float(fill.get('closedPnl', 0))
            pnl_str = f"[green]${pnl:,.2f}[/green]" if pnl >= 0 else f"[red]${pnl:,.2f}[/red]"
            direction = fill.get('dir', 'N/A')

            table.add_row(time_str, coin, side_str, sz, px, pnl_str, direction)

        console.print(table)

    console.print(f"\n[yellow]💡 TIP: Use api.get_fills('0x...', limit=100) for any wallet!")
    console.print("[dim]   Drop-in replacement for Hyperliquid's userFills call")


def show_candles(api, coin="BTC", interval="1h"):
    """Display OHLCV candles"""
    console.print(f"\n[bold cyan]📊 CANDLES: {coin} ({interval})[/bold cyan]")

    candles = api.get_candles(coin, interval=interval)

    console.print(f"\n[green]✅ Found {len(candles)} {interval} candles for {coin}")

    if candles:
        # Show latest 10 candles
        table = Table(title=f"{coin} {interval} Candles (Latest 10)", box=box.ROUNDED)
        table.add_column("Time", width=12)
        table.add_column("Open", justify="right", style="white", width=12)
        table.add_column("High", justify="right", style="green", width=12)
        table.add_column("Low", justify="right", style="red", width=12)
        table.add_column("Close", justify="right", style="cyan", width=12)
        table.add_column("Ticks", justify="right", width=8)

        from datetime import datetime
        for candle in candles[-10:]:
            ts = candle.get('t', 0)
            time_str = datetime.fromtimestamp(ts / 1000).strftime('%m/%d %H:%M') if ts else "N/A"
            o = f"${float(candle.get('o', 0)):,.2f}"
            h = f"${float(candle.get('h', 0)):,.2f}"
            l = f"${float(candle.get('l', 0)):,.2f}"
            c = f"${float(candle.get('c', 0)):,.2f}"
            n = str(candle.get('n', 0))

            table.add_row(time_str, o, h, l, c, n)

        console.print(table)

    # Show available intervals
    console.print("\n[yellow]Available intervals: 1m, 5m, 15m, 1h, 4h, 1d")
    console.print("[yellow]Available symbols: BTC, ETH, HYPE, SOL, XRP")
    console.print("[dim]   Data available: ~8 days (from Jan 6 onwards)")


def show_migration_guide():
    """Show migration cheatsheet"""
    console.print("\n[bold cyan]🔄 MIGRATION CHEATSHEET[/bold cyan]")

    table = Table(title="Replace Hyperliquid Rate-Limited Calls", box=box.ROUNDED)
    table.add_column("Old Hyperliquid Call", style="red", width=40)
    table.add_column("New Moon Dev API", style="green", width=25)

    table.add_row('{"type": "metaAndAssetCtxs"}', 'GET /api/prices')
    table.add_row('{"type": "l2Book", "coin": "BTC"}', 'GET /api/orderbook/BTC')
    table.add_row('{"type": "clearinghouseState", "user": "0x..."}', 'GET /api/account/0x...')
    table.add_row('{"type": "userFills", "user": "0x..."}', 'GET /api/fills/0x...')
    table.add_row('{"type": "candleSnapshot", ...}', 'GET /api/candles/BTC?interval=1h')
    table.add_row('(new!) Quick single price', 'GET /api/price/BTC')

    console.print(table)

    console.print("\n[green]✅ Benefits:")
    console.print("   • No rate limits - all calls go through Moon Dev's node")
    console.print("   • Faster response times")
    console.print("   • Pre-calculated spreads, mid prices, and more")
    console.print("   • Same data, better API")


def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]🌙 Moon Dev's Market Data API[/bold cyan]\n"
        "[dim]Real-time prices, orderbooks, accounts - NO RATE LIMITS![/dim]",
        border_style="cyan"
    ))

    api = MoonDevAPI()

    if not api.api_key:
        console.print("[red]❌ No API key found! Set MOONDEV_API_KEY in .env[/red]")
        return

    console.print(f"[green]✅ API Key loaded (ends with ...{api.api_key[-4:]})[/green]")

    # Show all examples
    show_all_prices(api)
    show_quick_price(api, "BTC")
    show_quick_price(api, "ETH")
    show_orderbook(api, "BTC")
    show_account(api, "0x010461c14e146ac35fe42271bdc1134ee31c703a")
    show_fills(api, "0x010461c14e146ac35fe42271bdc1134ee31c703a")
    show_candles(api, "BTC", "1h")
    show_candles(api, "BTC", "1m")
    show_candles(api, "ETH", "1m")
    show_migration_guide()

    console.print("\n[bold green]🌙 Market Data Demo Complete! - Moon Dev 🚀[/bold green]")


if __name__ == "__main__":
    main()
