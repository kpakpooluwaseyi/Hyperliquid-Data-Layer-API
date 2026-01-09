"""
🌙 Moon Dev's Trade Dashboard - Hyperliquid Trades
"""
import sys, os
from datetime import datetime
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import MoonDevAPI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box

console = Console()

def format_usd(v): return f"${v/1_000_000:,.2f}M" if v >= 1_000_000 else f"${v/1_000:,.1f}K" if v >= 1_000 else f"${v:,.2f}"
def format_price(p): return f"${p:,.2f}" if p >= 1000 else f"${p:,.4f}" if p >= 1 else f"${p:,.6f}"
def format_size(s, _): return f"{s:,.2f}" if s >= 1000 else f"{s:,.4f}" if s >= 1 else f"{s:,.6f}"


def print_header():
    """Print Moon Dev branding header"""
    from rich.align import Align
    banner = """███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗    ██████╗ ███████╗██╗   ██╗
████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║    ██╔══██╗██╔════╝██║   ██║
██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║    ██║  ██║█████╗  ██║   ██║
██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║    ██████╔╝███████╗ ╚████╔╝
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝ ╚══════╝  ╚═══╝"""
    console.print(Panel(Align.center(Text(banner, style="bold cyan")),
        title="🌙 [bold magenta]TRADE DASHBOARD[/bold magenta] 🌙",
        subtitle="[dim]Hyperliquid Trades by Moon Dev[/dim]",
        border_style="bright_cyan", box=box.DOUBLE_EDGE, padding=(0, 1)))


def print_stats_panels(trades, large_trades):
    """Print statistics panels"""
    total_trades = len(trades) if trades else 0
    total_large = len(large_trades) if large_trades else 0
    total_volume = sum(float(t.get('value_usd', t.get('value', 0))) for t in (trades or []))
    large_volume = sum(float(t.get('value_usd', t.get('value', 0))) for t in (large_trades or []))

    stats1 = Text()
    stats1.append("💹 RECENT TRADES\n", style="bold yellow")
    stats1.append("Count: ", style="dim"); stats1.append(f"{total_trades:,}\n", style="bold green")
    stats1.append("Volume: ", style="dim"); stats1.append(format_usd(total_volume), style="bold cyan")

    stats2 = Text()
    stats2.append("🔥 LARGE (>$100K)\n", style="bold red")
    stats2.append("Count: ", style="dim"); stats2.append(f"{total_large:,}\n", style="bold yellow")
    stats2.append("Volume: ", style="dim"); stats2.append(format_usd(large_volume), style="bold magenta")

    stats3 = Text()
    stats3.append("⏰ UPDATED\n", style="bold blue")
    stats3.append(datetime.now().strftime("%Y-%m-%d\n"), style="bold white")
    stats3.append(datetime.now().strftime("%H:%M:%S"), style="bold cyan")

    panels = [
        Panel(stats1, border_style="green", box=box.ROUNDED, width=28, padding=(0, 1)),
        Panel(stats2, border_style="red", box=box.ROUNDED, width=28, padding=(0, 1)),
        Panel(stats3, border_style="blue", box=box.ROUNDED, width=28, padding=(0, 1)),
    ]
    console.print(Columns(panels, equal=True, expand=True))


def create_trade_table(trades, title, limit=None, highlight_large=False):
    """Create a beautiful trade table"""
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan",
        border_style="blue", title_style="bold yellow", show_lines=False, padding=(0, 1))
    table.add_column("🪙 Coin", style="bold", justify="center", width=8)
    table.add_column("📊 Side", justify="center", width=7)
    table.add_column("📦 Size", justify="right", width=12)
    table.add_column("💵 Price", justify="right", width=12)
    table.add_column("💰 USD", justify="right", width=12)
    table.add_column("⏰ Time", justify="center", width=10)
    if not trades:
        table.add_row("No data", "-", "-", "-", "-", "-")
        return table
    for trade in (trades[:limit] if limit else trades):
        symbol = trade.get('coin', trade.get('symbol', 'N/A'))
        side = trade.get('side', 'N/A').upper()
        size = float(trade.get('size', trade.get('sz', 0)))
        price = float(trade.get('price', trade.get('px', 0)))
        value = float(trade.get('value_usd', trade.get('value', size * price)))
        timestamp = trade.get('timestamp', trade.get('time', ''))
        if timestamp:
            try:
                if isinstance(timestamp, str) and 'T' in timestamp:
                    time_str = timestamp.split('T')[1].split('.')[0]
                elif isinstance(timestamp, (int, float)):
                    time_str = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp).strftime("%H:%M:%S")
                else:
                    time_str = str(timestamp)[-8:]
            except: time_str = "N/A"
        else: time_str = "N/A"
        side_text = Text("🟢 BUY", style="bold green") if side in ["BUY", "B"] else Text("🔴 SELL", style="bold red") if side in ["SELL", "S", "A"] else Text(side, style="dim")
        is_large = value >= 100_000
        value_style = "bold yellow on red" if is_large and highlight_large else "bold white"
        symbol_style = "bold yellow" if is_large and highlight_large else "bold cyan"
        table.add_row(Text(symbol, style=symbol_style), side_text, format_size(size, symbol),
            format_price(price), Text(format_usd(value), style=value_style), time_str)
    return table


def print_volume_summary(trades):
    """Print volume summary by coin"""
    if not trades: return
    volume_by_coin = defaultdict(lambda: {'buy': 0, 'sell': 0, 'total': 0, 'count': 0})
    for trade in trades:
        symbol = trade.get('coin', trade.get('symbol', 'N/A'))
        side = trade.get('side', '').upper()
        value = float(trade.get('value_usd', trade.get('value', 0)))
        if side in ['BUY', 'B']: volume_by_coin[symbol]['buy'] += value
        elif side in ['SELL', 'S', 'A']: volume_by_coin[symbol]['sell'] += value
        volume_by_coin[symbol]['total'] += value
        volume_by_coin[symbol]['count'] += 1
    sorted_coins = sorted(volume_by_coin.items(), key=lambda x: x[1]['total'], reverse=True)
    table = Table(title="💰 VOLUME BY COIN", box=box.ROUNDED, header_style="bold magenta",
        border_style="magenta", title_style="bold yellow", padding=(0, 1))
    table.add_column("🪙 Coin", style="bold cyan", justify="center", width=8)
    table.add_column("🟢 Buy", justify="right", width=12)
    table.add_column("🔴 Sell", justify="right", width=12)
    table.add_column("📊 Total", justify="right", width=12)
    table.add_column("📈 #", justify="center", width=6)
    table.add_column("⚖️ Δ", justify="center", width=8)
    for coin, vol in sorted_coins:
        buy_vol, sell_vol, total_vol, count = vol['buy'], vol['sell'], vol['total'], vol['count']
        if total_vol > 0:
            imbalance = (buy_vol - sell_vol) / total_vol * 100
            imbalance_text = Text(f"+{imbalance:.0f}%", style="bold green") if imbalance > 10 else Text(f"{imbalance:.0f}%", style="bold red") if imbalance < -10 else Text(f"{imbalance:.0f}%", style="dim")
        else: imbalance_text = Text("N/A", style="dim")
        table.add_row(coin, Text(format_usd(buy_vol), style="green"), Text(format_usd(sell_vol), style="red"),
            Text(format_usd(total_vol), style="bold white"), str(count), imbalance_text)
    console.print(table)


def main():
    """Main function - Moon Dev's Trade Dashboard"""
    console.clear()
    print_header()
    console.print("[bold cyan]🌙 Moon Dev:[/bold cyan] Connecting to API...")
    api = MoonDevAPI()
    if not api.api_key:
        console.print(Panel("[bold red]❌ No API key![/bold red] Set MOONDEV_API_KEY in .env",
            border_style="red", title="🔐 Auth Required", padding=(0, 1)))
        return
    console.print(f"[bold green]✅ API Key loaded[/bold green] (...{api.api_key[-4:]})")
    console.print("[bold yellow]📡 Fetching trades...[/bold yellow]")
    trades, large_trades, total_trade_count = None, None, 0
    trades_data = api.get_trades()
    if isinstance(trades_data, list): trades = trades_data
    elif isinstance(trades_data, dict):
        trades = trades_data.get('trades', [])
        total_trade_count = trades_data.get('total_trades', len(trades))
    console.print(f"[green]  ✓ {len(trades) if trades else 0} recent (total: {total_trade_count:,})[/green]")
    large_trades_data = api.get_large_trades()
    if isinstance(large_trades_data, list): large_trades = large_trades_data
    elif isinstance(large_trades_data, dict): large_trades = large_trades_data.get('trades', [])
    console.print(f"[green]  ✓ {len(large_trades) if large_trades else 0} large trades[/green]")
    print_stats_panels(trades, large_trades)
    console.print(create_trade_table(trades, "💹 TOP 20 RECENT TRADES", limit=20, highlight_large=True))
    if large_trades:
        console.print(Panel(f"[bold red]🔥 WHALE ALERT: {len(large_trades)} LARGE TRADES![/bold red]",
            border_style="red", box=box.DOUBLE, padding=(0, 1)))
        console.print(create_trade_table(large_trades, "🔥 LARGE TRADES (>$100K) - 24H", limit=None, highlight_large=True))
    else:
        console.print(Panel("[dim]No large trades (>$100k) in 24h[/dim]", border_style="dim", padding=(0, 1)))
    print_volume_summary(trades)
    console.print(f"[dim]🌙 Moon Dev's Trade Dashboard | Refreshes 30s | [bold magenta]moondev.com[/bold magenta] | {datetime.now().strftime('%H:%M:%S')}[/dim]")

if __name__ == "__main__":
    main()
