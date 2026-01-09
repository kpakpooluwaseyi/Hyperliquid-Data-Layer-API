"""
Moon Dev's User Positions Dashboard
====================================
Beautiful terminal dashboard for viewing Hyperliquid wallet positions

Built with love by Moon Dev

Usage: python 10_user_positions.py [address]
       python 10_user_positions.py 0x010461c14e146ac35fe42271bdc1134ee31c703a
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import api.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import MoonDevAPI

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.align import Align


console = Console()


def create_banner():
    """Create the Moon Dev branded header banner"""
    banner = """
 _   _ ___  ___ _ __
| | | / __|/ _ \\ '__|
| |_| \\__ \\  __/ |
 \\__,_|___/\\___|_|
 ____   ___  ____ ___ _____ ___ ___  _   _ ____
|  _ \\ / _ \\/ ___|_ _|_   _|_ _/ _ \\| \\ | / ___|
| |_) | | | \\___ \\| |  | |  | | | | |  \\| \\___ \\
|  __/| |_| |___) | |  | |  | | |_| | |\\  |___) |
|_|    \\___/|____/___| |_| |___\\___/|_| \\_|____/
"""
    return Panel(
        Align.center(Text(banner, style="bold cyan")),
        title="[bold magenta]MOON DEV'S HYPERLIQUID POSITION VIEWER[/bold magenta]",
        subtitle="[dim]Get positions for any Hyperliquid wallet[/dim]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1)
    )


def format_usd(value):
    """Format USD value with commas and dollar sign"""
    if value is None:
        return "$0"
    if isinstance(value, str):
        value = float(value.replace(',', '').replace('$', ''))
    return f"${value:,.2f}"


def format_pnl(value):
    """Format PnL with color coding"""
    if value is None:
        return Text("$0.00", style="white")
    if isinstance(value, str):
        value = float(value.replace(',', '').replace('$', ''))

    if value > 0:
        return Text(f"+${value:,.2f}", style="bold green")
    elif value < 0:
        return Text(f"-${abs(value):,.2f}", style="bold red")
    else:
        return Text("$0.00", style="white")


def create_positions_table(positions_data, address):
    """Create a beautiful table of positions"""
    table = Table(
        title=f"Positions for {address[:10]}...{address[-6:]}",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold yellow",
        padding=(0, 1)
    )

    table.add_column("Coin", style="bold white", justify="center")
    table.add_column("Side", justify="center")
    table.add_column("Size", style="cyan", justify="right")
    table.add_column("Position Value", style="yellow", justify="right")
    table.add_column("Entry Price", justify="right")
    table.add_column("Mark Price", justify="right")
    table.add_column("Liq Price", style="red", justify="right")
    table.add_column("Leverage", style="magenta", justify="center")
    table.add_column("PnL", justify="right")

    if not isinstance(positions_data, dict):
        table.add_row(Text("No data available", style="dim"), "", "", "", "", "", "", "", "")
        return table

    asset_positions = positions_data.get('assetPositions', [])

    if not asset_positions:
        table.add_row(Text("No open positions", style="dim"), "", "", "", "", "", "", "", "")
        return table

    # Process and sort positions by value
    processed_positions = []
    for pos in asset_positions:
        if 'position' not in pos:
            continue
        p = pos['position']

        size = float(p.get('szi', 0))
        if size == 0:
            continue

        position_value = float(p.get('positionValue', 0))
        processed_positions.append({
            'coin': p.get('coin', '?'),
            'size': size,
            'is_long': size > 0,
            'position_value': position_value,
            'entry_price': float(p.get('entryPx', 0)),
            'unrealized_pnl': float(p.get('unrealizedPnl', 0)),
            'liquidation_price': float(p.get('liquidationPx', 0) or 0),
            'leverage': p.get('leverage', {}).get('value', 0) if isinstance(p.get('leverage'), dict) else 0
        })

    # Sort by position value
    processed_positions.sort(key=lambda x: abs(x['position_value']), reverse=True)

    for pos in processed_positions:
        coin = pos['coin']
        size = pos['size']
        is_long = pos['is_long']

        # Side with color
        side_text = Text("LONG", style="bold green") if is_long else Text("SHORT", style="bold red")

        # Size formatting
        size_str = f"{abs(size):,.4f}" if abs(size) < 1000 else f"{abs(size):,.2f}"

        # Position value
        pos_value = format_usd(pos['position_value'])

        # Entry price
        entry_str = f"${pos['entry_price']:,.2f}" if pos['entry_price'] else "N/A"

        # Mark price (calculate from position value / size)
        if size != 0 and pos['position_value'] != 0:
            mark_price = abs(pos['position_value'] / size)
            mark_str = f"${mark_price:,.2f}"
        else:
            mark_str = "N/A"

        # Liquidation price
        liq = pos['liquidation_price']
        liq_str = f"${liq:,.2f}" if liq > 0 else "N/A"

        # Leverage
        leverage = pos['leverage']
        leverage_str = f"{leverage:.1f}x" if leverage else "N/A"

        # PnL
        pnl_text = format_pnl(pos['unrealized_pnl'])

        table.add_row(
            coin,
            side_text,
            size_str,
            pos_value,
            entry_str,
            mark_str,
            liq_str,
            leverage_str,
            pnl_text
        )

    return table


def create_summary_panel(positions_data, address):
    """Create a summary stats panel"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="Summary")

    margin = positions_data.get('marginSummary', {})
    account_value = float(margin.get('accountValue', 0))
    total_ntl_pos = float(margin.get('totalNtlPos', 0))
    total_margin_used = float(margin.get('totalMarginUsed', 0))

    asset_positions = positions_data.get('assetPositions', [])

    # Calculate totals
    total_pnl = 0
    long_count = 0
    short_count = 0
    long_value = 0
    short_value = 0

    for pos in asset_positions:
        if 'position' not in pos:
            continue
        p = pos['position']
        size = float(p.get('szi', 0))
        if size == 0:
            continue
        pnl = float(p.get('unrealizedPnl', 0))
        pos_value = float(p.get('positionValue', 0))
        total_pnl += pnl

        if size > 0:
            long_count += 1
            long_value += pos_value
        else:
            short_count += 1
            short_value += pos_value

    pnl_color = "green" if total_pnl >= 0 else "red"
    pnl_sign = "+" if total_pnl >= 0 else ""

    lines = [
        f"[bold cyan]Wallet:[/bold cyan] [dim]{address[:20]}...{address[-8:]}[/dim]",
        f"[bold cyan]Account Value:[/bold cyan] [yellow]{format_usd(account_value)}[/yellow]",
        f"[bold cyan]Total Position Value:[/bold cyan] [yellow]{format_usd(total_ntl_pos)}[/yellow]",
        f"[bold cyan]Margin Used:[/bold cyan] [yellow]{format_usd(total_margin_used)}[/yellow]",
        f"[bold cyan]Unrealized PnL:[/bold cyan] [{pnl_color}]{pnl_sign}{format_usd(total_pnl)}[/{pnl_color}]",
        f"[bold cyan]Long Positions:[/bold cyan] [green]{long_count}[/green] ({format_usd(long_value)})",
        f"[bold cyan]Short Positions:[/bold cyan] [red]{short_count}[/red] ({format_usd(short_value)})",
    ]

    return Panel(
        "\n".join(lines),
        title="Account Summary",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_coin_breakdown(positions_data):
    """Create a coin breakdown panel"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="Coin Breakdown")

    asset_positions = positions_data.get('assetPositions', [])

    coins = {}
    for pos in asset_positions:
        if 'position' not in pos:
            continue
        p = pos['position']
        size = float(p.get('szi', 0))
        if size == 0:
            continue

        coin = p.get('coin', '?')
        pos_value = float(p.get('positionValue', 0))
        pnl = float(p.get('unrealizedPnl', 0))

        if coin not in coins:
            coins[coin] = {'value': 0, 'pnl': 0, 'is_long': size > 0}
        coins[coin]['value'] += pos_value
        coins[coin]['pnl'] += pnl

    if not coins:
        return Panel("[dim]No positions[/dim]", title="Coin Breakdown", border_style="bright_yellow")

    sorted_coins = sorted(coins.items(), key=lambda x: x[1]['value'], reverse=True)

    lines = []
    for coin, data in sorted_coins[:10]:
        side = "L" if data['is_long'] else "S"
        side_color = "green" if data['is_long'] else "red"
        pnl_color = "green" if data['pnl'] >= 0 else "red"
        pnl_sign = "+" if data['pnl'] >= 0 else ""

        lines.append(
            f"[{side_color}]{side}[/{side_color}] [bold white]{coin:>5}[/bold white] "
            f"[yellow]{format_usd(data['value']):>12}[/yellow] "
            f"[{pnl_color}]{pnl_sign}{format_usd(data['pnl']):>10}[/{pnl_color}]"
        )

    return Panel(
        "\n".join(lines) if lines else "[dim]No data[/dim]",
        title="Coin Breakdown",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def main():
    """Main function to run the user positions dashboard"""
    console.print(create_banner())

    # Get address from command line or use default
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        # Default to HLP_LONG for demo
        address = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
        console.print(f"[dim]No address provided, using default: {address[:10]}...[/dim]")

    console.print(f"[bold cyan]Moon Dev: Fetching positions for {address[:10]}...{address[-6:]}[/bold cyan]")

    # Initialize API
    api = MoonDevAPI()

    # Fetch positions
    positions_data = api.get_user_positions(address)

    # Create and display panels
    summary_panel = create_summary_panel(positions_data, address)
    coin_panel = create_coin_breakdown(positions_data)
    console.print(Columns([summary_panel, coin_panel], equal=True))

    # Create and display positions table
    positions_table = create_positions_table(positions_data, address)
    console.print(positions_table)

    # Footer with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"\n[dim]Moon Dev | {timestamp} | Hyperliquid User Positions | moondev.com[/dim]")


if __name__ == "__main__":
    main()
