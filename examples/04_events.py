#!/usr/bin/env python3
"""
🌙 Moon Dev's Blockchain Events Dashboard
==========================================
Beautiful terminal visualization of real-time blockchain events
Built with love by Moon Dev 🚀

Usage:
    python API_examples/04_events.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import MoonDevAPI
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.align import Align
from rich.columns import Columns

# =============================================================================
# 🌙 Moon Dev's Events Dashboard - Developer Porn Edition
# =============================================================================

console = Console()

# Color palette for event types
EVENT_COLORS = {
    'Transfer': 'cyan',
    'Swap': 'magenta',
    'Deposit': 'green',
    'Withdraw': 'yellow',
    'Liquidation': 'red',
    'Mint': 'blue',
    'Burn': 'bright_red',
    'Stake': 'bright_green',
    'Unstake': 'bright_yellow',
    'Claim': 'bright_cyan',
    'Bridge': 'bright_magenta',
    'Default': 'white'
}

# Emoji mapping for event types
EVENT_EMOJIS = {
    'Transfer': '🔄',
    'Swap': '💱',
    'Deposit': '📥',
    'Withdraw': '📤',
    'Liquidation': '💥',
    'Mint': '🪙',
    'Burn': '🔥',
    'Stake': '🔒',
    'Unstake': '🔓',
    'Claim': '🎁',
    'Bridge': '🌉',
    'Default': '⚡'
}


def create_banner():
    """Create the Moon Dev header banner"""
    banner = """███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗    ██████╗ ███████╗██╗   ██╗
████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║    ██╔══██╗██╔════╝██║   ██║
██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║    ██║  ██║█████╗  ██║   ██║
██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║    ██║  ██║██╔══╝  ╚██╗ ██╔╝
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║    ██████╔╝███████╗ ╚████╔╝
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝    ╚═════╝ ╚══════╝  ╚═══╝"""
    return Panel(
        Align.center(Text(banner, style="bold cyan")),
        title="🌙 [bold magenta]BLOCKCHAIN EVENTS DASHBOARD[/bold magenta] 🌙",
        subtitle="[dim]⚡ Real-time event monitoring by Moon Dev ⚡[/dim]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1)
    )


def create_big_number(number, label, color="cyan"):
    """Create a big number display"""
    formatted = f"{number:,}" if isinstance(number, int) else str(number)
    big_text = f"╔════════════════════════╗\n║  {formatted:^20}  ║\n╚════════════════════════╝"
    return Panel(
        Align.center(Text(big_text, style=f"bold {color}")),
        title=f"[bold {color}]{label}[/bold {color}]",
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_bar(value, max_value, width=30, color="cyan"):
    """Create a visual bar using block characters"""
    if max_value == 0:
        filled = 0
    else:
        filled = int((value / max_value) * width)

    bar = "█" * filled + "░" * (width - filled)
    return f"[{color}]{bar}[/{color}]"


def create_events_by_type_table(events_by_type):
    """Create a beautiful table showing events by type with bar chart"""
    table = Table(
        title="⚡ [bold cyan]Events by Type[/bold cyan] ⚡",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold magenta",
        show_lines=False,
        padding=(0, 1)
    )

    table.add_column("Type", style="bold", justify="left", width=15)
    table.add_column("Count", justify="right", width=12)
    table.add_column("Distribution", justify="left", width=35)
    table.add_column("%", justify="right", width=8)

    if not events_by_type:
        table.add_row("No data", "-", "-", "-")
        return table

    # Sort by count descending
    sorted_events = sorted(events_by_type.items(), key=lambda x: x[1], reverse=True)
    max_count = sorted_events[0][1] if sorted_events else 1
    total = sum(events_by_type.values())

    for event_type, count in sorted_events:
        emoji = EVENT_EMOJIS.get(event_type, EVENT_EMOJIS['Default'])
        color = EVENT_COLORS.get(event_type, EVENT_COLORS['Default'])
        bar = create_bar(count, max_count, width=30, color=color)
        percentage = (count / total * 100) if total > 0 else 0

        table.add_row(
            f"{emoji} [{color}]{event_type}[/{color}]",
            f"[bold {color}]{count:,}[/bold {color}]",
            bar,
            f"[{color}]{percentage:.1f}%[/{color}]"
        )

    return table


def create_stats_panel(stats, large_transfers, large_swaps):
    """Create a panel with key statistics"""
    total_events = stats.get('total_events', 0)
    stats_text = Text()
    stats_text.append("🎯 ", style="bold")
    stats_text.append("TOTAL EVENTS: ", style="bold white")
    stats_text.append(f"{total_events:,}\n", style="bold cyan")
    stats_text.append("🔄 ", style="bold")
    stats_text.append("Large Transfers: ", style="bold white")
    stats_text.append(f"{large_transfers:,}\n", style="bold green")
    stats_text.append("💱 ", style="bold")
    stats_text.append("Large Swaps: ", style="bold white")
    stats_text.append(f"{large_swaps:,}", style="bold magenta")
    if 'events_per_minute' in stats:
        stats_text.append("\n⚡ ", style="bold")
        stats_text.append("Events/min: ", style="bold white")
        stats_text.append(f"{stats['events_per_minute']:.1f}", style="bold yellow")
    return Panel(
        stats_text,
        title="📊 [bold yellow]Key Metrics[/bold yellow] 📊",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def create_recent_events_table(events_list):
    """Create a table of recent events"""
    table = Table(
        title="🔥 [bold red]Recent Events[/bold red] 🔥",
        box=box.ROUNDED,
        border_style="red",
        header_style="bold yellow",
        show_lines=False,
        padding=(0, 1)
    )

    table.add_column("Type", style="bold", justify="center", width=12)
    table.add_column("From", justify="left", width=44)
    table.add_column("To", justify="left", width=44)
    table.add_column("Value", justify="right", width=15)
    table.add_column("Time", justify="center", width=12)

    if not events_list:
        table.add_row("No events", "-", "-", "-", "-")
        return table

    for event in events_list[:10]:  # Show top 10
        event_type = event.get('type', event.get('event_type', 'Unknown'))
        emoji = EVENT_EMOJIS.get(event_type, EVENT_EMOJIS['Default'])
        color = EVENT_COLORS.get(event_type, EVENT_COLORS['Default'])

        from_addr = event.get('from', event.get('from_address', 'N/A'))
        to_addr = event.get('to', event.get('to_address', 'N/A'))

        # Show FULL addresses - Moon Dev says the full address is the main event!
        from_display = str(from_addr)
        to_display = str(to_addr)

        value = event.get('value', event.get('usd_value', event.get('amount', 0)))
        if isinstance(value, (int, float)):
            value_display = f"${value:,.2f}"
        else:
            value_display = str(value)

        timestamp = event.get('timestamp', event.get('time', 'N/A'))
        if isinstance(timestamp, str) and len(timestamp) > 10:
            timestamp = timestamp[11:19] if 'T' in timestamp else timestamp[-8:]

        table.add_row(
            f"{emoji} [{color}]{event_type}[/{color}]",
            f"[dim]{from_display}[/dim]",
            f"[dim]{to_display}[/dim]",
            f"[bold green]{value_display}[/bold green]",
            f"[dim cyan]{timestamp}[/dim cyan]"
        )

    return table


def create_event_type_bars(events_by_type):
    """Create a visual horizontal bar chart"""
    if not events_by_type:
        return Panel("[dim]No event data available[/dim]", title="Event Distribution", padding=(0, 1))
    sorted_events = sorted(events_by_type.items(), key=lambda x: x[1], reverse=True)
    max_val = sorted_events[0][1] if sorted_events else 1
    lines = []
    for event_type, count in sorted_events[:8]:  # Top 8 types
        emoji = EVENT_EMOJIS.get(event_type, '⚡')
        color = EVENT_COLORS.get(event_type, 'white')
        bar_width = int((count / max_val) * 40) if max_val > 0 else 0
        bar = "▓" * bar_width
        lines.append(f"{emoji} [{color}]{event_type:12}[/{color}] [{color}]{bar}[/{color}] [bold]{count:,}[/bold]")
    content = "\n".join(lines)
    return Panel(
        content,
        title="📊 [bold blue]Event Type Distribution[/bold blue] 📊",
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 1)
    )


def main():
    """Main dashboard function - Moon Dev style!"""
    console.clear()
    console.print(create_banner())
    console.print("[bold cyan]🌙 Moon Dev[/bold cyan]: Initializing API connection...", style="dim")
    api = MoonDevAPI()
    if not api.api_key:
        console.print(Panel(
            "[bold red]❌ No API key found![/bold red]\n"
            "Set MOONDEV_API_KEY in your .env file:\n"
            "[dim]echo 'MOONDEV_API_KEY=your_key' >> .env[/dim]",
            title="⚠️ Authentication Error",
            border_style="red",
            padding=(0, 1)
        ))
        return
    console.print(f"[bold green]✅ API Key loaded[/bold green] [dim](ends with ...{api.api_key[-4:]})[/dim]")
    console.print("[bold cyan]🌙 Moon Dev[/bold cyan]: Fetching blockchain events...", style="dim")
    events_data = api.get_events()
    console.print("[bold green]✅ Data received![/bold green]")

    # Parse the response
    stats = {}
    events_by_type = {}
    events_list = []
    large_transfers = 0
    large_swaps = 0

    if isinstance(events_data, dict):
        stats = events_data.get('stats', {})
        events_by_type = stats.get('events_by_type', events_data.get('events_by_type', {}))
        events_list = events_data.get('events', events_data.get('recent_events', []))
        large_transfers = stats.get('large_transfers', events_data.get('large_transfers_count', 0))
        large_swaps = stats.get('large_swaps', events_data.get('large_swaps_count', 0))

        # If events_by_type is still empty, try to compute from events list
        if not events_by_type and events_list:
            for event in events_list:
                etype = event.get('type', event.get('event_type', 'Unknown'))
                events_by_type[etype] = events_by_type.get(etype, 0) + 1
    elif isinstance(events_data, list):
        events_list = events_data
        for event in events_data:
            etype = event.get('type', event.get('event_type', 'Unknown'))
            events_by_type[etype] = events_by_type.get(etype, 0) + 1
        stats = {'total_events': len(events_data), 'events_by_type': events_by_type}

    total_events = stats.get('total_events', sum(events_by_type.values()) if events_by_type else len(events_list))

    console.print(create_big_number(total_events, "⚡ TOTAL BLOCKCHAIN EVENTS ⚡", "cyan"))
    stats_panel = create_stats_panel(stats, large_transfers, large_swaps)
    bar_chart = create_event_type_bars(events_by_type)
    console.print(Columns([stats_panel, bar_chart], equal=True, expand=True))
    console.print(create_events_by_type_table(events_by_type))
    if events_list:
        console.print(create_recent_events_table(events_list))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(f"[dim]─── 🌙 Moon Dev | {now} | moondev.com ───[/dim]", justify="center")
    console.print("[bold cyan]🌙 Moon Dev[/bold cyan]: Dashboard complete! Stay based, Dr. Data Dawg! 🚀", style="bold")


if __name__ == "__main__":
    main()
