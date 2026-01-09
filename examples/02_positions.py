"""
🌙 Moon Dev's Position Dashboard
================================
Beautiful terminal dashboard for tracking large positions near liquidation ($200k+)

Built with love by Moon Dev 🚀
Using the Rich library for gorgeous terminal output

Usage: python 02_positions.py
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
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn
from rich.style import Style
from rich.align import Align


console = Console()


def create_banner():
    """Create the Moon Dev branded header banner"""
    banner = """███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗    ██████╗ ███████╗██╗   ██╗
████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║    ██╔══██╗██╔════╝██║   ██║
██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║    ██║  ██║█████╗  ██║   ██║
██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║    ██████╔╝███████╗ ╚████╔╝
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝ ╚══════╝  ╚═══╝"""
    return Panel(
        Align.center(Text(banner, style="bold cyan")),
        title="🌙 [bold magenta]POSITION TRACKER[/bold magenta] 🌙",
        subtitle="[dim]💰 Large Positions Near Liquidation by Moon Dev 💰[/dim]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1)
    )


def get_full_address(address):
    """Return full wallet address for display - Moon Dev wants the FULL address!"""
    if not address:
        return "Unknown"
    return address


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


def get_risk_color(distance_pct):
    """Get color based on distance to liquidation percentage"""
    if distance_pct is None:
        return "white"

    if isinstance(distance_pct, str):
        distance_pct = float(distance_pct.replace('%', ''))

    # Lower percentage = closer to liquidation = higher risk
    if distance_pct < 2:
        return "bold red"
    elif distance_pct < 5:
        return "red"
    elif distance_pct < 10:
        return "yellow"
    elif distance_pct < 20:
        return "cyan"
    else:
        return "green"


def create_positions_table(positions_data):
    """Create a beautiful table of positions"""
    table = Table(
        title="🐋 Whale Positions Near Liquidation 🐋",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="cyan",
        title_style="bold yellow",
        padding=(0, 1)
    )

    table.add_column("💰 Address", style="cyan", justify="center")
    table.add_column("🪙 Coin", style="bold white", justify="center")
    table.add_column("📊 Side", justify="center")
    table.add_column("💵 Position Value", style="yellow", justify="right")
    table.add_column("⚡ Lev", style="magenta", justify="center")
    table.add_column("💹 Entry", justify="right")
    table.add_column("🎯 Liq Price", justify="right")
    table.add_column("⚠️ Dist%", justify="center")
    table.add_column("📈 PnL", justify="right")

    # Combine longs and shorts from the API response
    all_positions = []

    if isinstance(positions_data, dict):
        longs = positions_data.get('longs', [])
        shorts = positions_data.get('shorts', [])

        # Add side info to each position
        for pos in longs:
            pos['side'] = 'LONG'
            all_positions.append(pos)
        for pos in shorts:
            pos['side'] = 'SHORT'
            all_positions.append(pos)

    # Sort by distance_pct (closest to liquidation first = highest risk)
    all_positions.sort(key=lambda x: x.get('distance_pct', 100))

    if not all_positions:
        table.add_row(
            Text("No positions found", style="dim"),
            "", "", "", "", "", "", "", ""
        )
        return table

    for pos in all_positions[:25]:  # Show top 25 riskiest positions
        address = get_full_address(pos.get('address', ''))
        coin = pos.get('coin', 'N/A').upper()

        # Side with color
        side = pos.get('side', 'N/A')
        side_text = Text(side, style="green" if side == 'LONG' else "red")

        # Position value
        pos_value = pos.get('value', 0)

        # Leverage
        leverage = pos.get('leverage', 0)
        leverage_str = f"{leverage:.1f}x"

        # Entry price
        entry = pos.get('entry_price', 0)
        entry_str = f"${entry:,.2f}" if entry else "N/A"

        # Liquidation price
        liq = pos.get('liq_price', 0)
        liq_str = f"${liq:,.2f}" if liq else "N/A"

        # Risk (distance to liquidation)
        distance_pct = pos.get('distance_pct', None)
        if distance_pct is not None:
            risk_style = get_risk_color(distance_pct)
            risk_text = Text(f"{distance_pct:.2f}%", style=risk_style)
        else:
            risk_text = Text("N/A", style="dim")

        # PnL
        pnl = pos.get('pnl', 0)
        pnl_text = format_pnl(pnl)

        table.add_row(
            address,
            coin,
            side_text,
            format_usd(pos_value),
            leverage_str,
            entry_str,
            liq_str,
            risk_text,
            pnl_text
        )

    return table


def create_stats_panel(positions_data):
    """Create a summary stats panel"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="📊 Position Statistics")

    total_positions = positions_data.get('total_positions', 0)
    total_longs = positions_data.get('total_longs', 0)
    total_shorts = positions_data.get('total_shorts', 0)
    min_value = positions_data.get('min_position_value', 200000)

    longs = positions_data.get('longs', [])
    shorts = positions_data.get('shorts', [])
    all_positions = longs + shorts

    # Calculate aggregated stats
    total_value = sum(p.get('value', 0) for p in all_positions)
    total_pnl = sum(p.get('pnl', 0) for p in all_positions)

    # Count high risk positions
    critical_count = sum(1 for p in all_positions if p.get('distance_pct', 100) < 2)
    high_risk_count = sum(1 for p in all_positions if 2 <= p.get('distance_pct', 100) < 5)

    # Build stats text
    pnl_color = "green" if total_pnl >= 0 else "red"
    pnl_sign = "+" if total_pnl >= 0 else ""
    stats_lines = [
        f"[bold cyan]💰 Total Positions:[/bold cyan] [yellow]{total_positions:,}[/yellow]",
        f"[bold cyan]💵 Position Value:[/bold cyan] [yellow]{format_usd(total_value)}[/yellow]",
        f"[bold cyan]🔎 Min Size:[/bold cyan] [dim]{format_usd(min_value)}[/dim]",
        f"[bold cyan]📊 Unrealized PnL:[/bold cyan] [{pnl_color}]{pnl_sign}{format_usd(total_pnl)}[/{pnl_color}]",
        f"[bold cyan]🟢 Longs:[/bold cyan] [green]{total_longs}[/green] | [bold cyan]🔴 Shorts:[/bold cyan] [red]{total_shorts}[/red]",
        f"[bold cyan]🚨 Critical (<2%):[/bold cyan] [bold red]{critical_count}[/bold red] | [bold cyan]⚠️ High (2-5%):[/bold cyan] [yellow]{high_risk_count}[/yellow]"
    ]
    return Panel(
        "\n".join(stats_lines),
        title="📊 Position Statistics",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_coin_distribution(positions_data):
    """Create a coin distribution breakdown"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="🪙 Positions by Coin")

    longs = positions_data.get('longs', [])
    shorts = positions_data.get('shorts', [])
    all_positions = longs + shorts

    # Count by coin with values
    coins = {}
    for pos in all_positions:
        coin = pos.get('coin', 'UNKNOWN').upper()
        val = pos.get('value', 0)

        if coin not in coins:
            coins[coin] = {'count': 0, 'value': 0, 'longs': 0, 'shorts': 0}
        coins[coin]['count'] += 1
        coins[coin]['value'] += val
        if pos.get('side') == 'LONG' or pos in longs:
            coins[coin]['longs'] += 1
        else:
            coins[coin]['shorts'] += 1

    if not coins:
        return Panel(
            "[dim]No coin data available[/dim]",
            title="🪙 Positions by Coin",
            border_style="bright_yellow"
        )

    # Sort by value
    sorted_coins = sorted(coins.items(), key=lambda x: x[1]['value'], reverse=True)

    # Create display
    lines = []
    max_value = max(c[1]['value'] for c in sorted_coins) if sorted_coins else 1

    coin_colors = {
        'BTC': 'yellow',
        'ETH': 'blue',
        'SOL': 'magenta',
        'HYPE': 'cyan',
        'XRP': 'white',
        'DOGE': 'yellow',
        'LINK': 'blue',
        'AVAX': 'red',
        'SUI': 'cyan',
        'PEPE': 'green',
        'WIF': 'magenta'
    }

    for coin, data in sorted_coins[:10]:  # Top 10 coins
        bar_length = int((data['value'] / max_value) * 15) if max_value > 0 else 0
        color = coin_colors.get(coin, 'white')
        bar = "█" * bar_length + "░" * (15 - bar_length)

        lines.append(
            f"[{color}]{coin:>5}[/{color}] [{color}]{bar}[/{color}] "
            f"[yellow]${data['value']/1e6:>6.2f}M[/yellow] "
            f"[green]L:{data['longs']:>2}[/green] [red]S:{data['shorts']:>2}[/red]"
        )

    return Panel(
        "\n".join(lines) if lines else "[dim]No data[/dim]",
        title="🪙 Positions by Coin (Top Value)",
        border_style="bright_yellow",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_risk_analysis(positions_data):
    """Create a risk analysis panel"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="⚠️ Risk Analysis")

    longs = positions_data.get('longs', [])
    shorts = positions_data.get('shorts', [])
    all_positions = longs + shorts

    # Categorize by risk level based on distance_pct
    critical = []  # < 2%
    high = []      # 2-5%
    medium = []    # 5-10%
    moderate = []  # 10-20%
    low = []       # > 20%

    for pos in all_positions:
        dist = pos.get('distance_pct', 100)
        if dist < 2:
            critical.append(pos)
        elif dist < 5:
            high.append(pos)
        elif dist < 10:
            medium.append(pos)
        elif dist < 20:
            moderate.append(pos)
        else:
            low.append(pos)

    # Calculate values at risk for each category
    critical_value = sum(p.get('value', 0) for p in critical)
    high_value = sum(p.get('value', 0) for p in high)
    medium_value = sum(p.get('value', 0) for p in medium)

    lines = [
        f"[bold red]🚨 CRITICAL (<2%):[/bold red] [red]{len(critical)}[/red] pos | [yellow]${critical_value/1e6:.2f}M[/yellow]",
        f"[bold yellow]⚠️ HIGH (2-5%):[/bold yellow] [yellow]{len(high)}[/yellow] pos | [yellow]${high_value/1e6:.2f}M[/yellow]",
        f"[bold cyan]📊 MEDIUM (5-10%):[/bold cyan] [cyan]{len(medium)}[/cyan] pos | [yellow]${medium_value/1e6:.2f}M[/yellow]",
        f"[bold white]📉 MODERATE (10-20%):[/bold white] [white]{len(moderate)}[/white] positions",
        f"[bold green]✅ LOW (>20%):[/bold green] [green]{len(low)}[/green] positions"
    ]
    return Panel(
        "\n".join(lines),
        title="⚠️ Risk Analysis",
        border_style="bright_red",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_top_whales_panel(positions_data):
    """Create a panel showing the biggest whale positions"""
    if not isinstance(positions_data, dict):
        return Panel("[dim]No data available[/dim]", title="🐋 Top Whales")

    longs = positions_data.get('longs', [])
    shorts = positions_data.get('shorts', [])
    all_positions = longs + shorts

    # Sort by position value
    sorted_by_value = sorted(all_positions, key=lambda x: x.get('value', 0), reverse=True)

    lines = []
    for i, pos in enumerate(sorted_by_value[:5], 1):
        addr = get_full_address(pos.get('address', ''))
        coin = pos.get('coin', '?')
        value = pos.get('value', 0)
        side = 'L' if pos in longs else 'S'
        pnl = pos.get('pnl', 0)
        side_color = "green" if side == 'L' else "red"
        pnl_color = "green" if pnl >= 0 else "red"
        pnl_sign = "+" if pnl >= 0 else ""
        lines.append(
            f"[yellow]{i}.[/yellow] [{side_color}]{side}[/{side_color}] "
            f"[cyan]{coin:>4}[/cyan] [yellow]${value/1e6:.2f}M[/yellow] "
            f"[{pnl_color}]{pnl_sign}${pnl/1e3:.1f}k[/{pnl_color}]"
        )
    return Panel(
        "\n".join(lines),
        title="🐋 Top 5 Whales",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def main():
    """Main function to run the position dashboard"""
    console.print(create_banner())
    # Initialize API
    console.print("[bold cyan]🌙 Moon Dev: Initializing API...[/bold cyan]")
    api = MoonDevAPI()
    if not api.api_key:
        console.print(Panel(
            "[bold red]❌ No API key found![/bold red]\n"
            "Please set MOONDEV_API_KEY in your .env file\n"
            "[dim]Get your API key at: https://moondev.com[/dim]",
            title="⚠️ Auth Error",
            border_style="red",
            padding=(0, 1)
        ))
        return
    console.print("[green]✅ API Key loaded[/green]")
    console.print("[bold magenta]📡 Fetching positions...[/bold magenta]")
    positions_data = api.get_positions()
    # Create and display stats panels side by side
    stats_panel = create_stats_panel(positions_data)
    coin_panel = create_coin_distribution(positions_data)
    risk_panel = create_risk_analysis(positions_data)
    whale_panel = create_top_whales_panel(positions_data)
    console.print(Columns([stats_panel, coin_panel], equal=True))
    console.print(Columns([risk_panel, whale_panel], equal=True))
    # Create and display positions table
    positions_table = create_positions_table(positions_data)
    console.print(positions_table)
    # Footer with timestamp
    updated_at = positions_data.get('updated_at', '') if isinstance(positions_data, dict) else ''
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[dim]─── 🌙 Moon Dev │ {timestamp} │ Data: {updated_at} │ moondev.com ───[/dim]")


if __name__ == "__main__":
    main()
