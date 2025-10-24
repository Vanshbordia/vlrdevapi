"""Team transactions and previous players retrieval."""

from __future__ import annotations

from datetime import date
from collections import defaultdict
from bs4 import BeautifulSoup

from ..config import get_config
from ..countries import map_country_code
from ..fetcher import fetch_html  # Uses connection pooling automatically
from ..exceptions import NetworkError
from ..utils import extract_text, extract_id_from_url, normalize_whitespace, extract_country_code

from .models import PlayerTransaction, PreviousPlayer

_config = get_config()

def _parse_transaction_date(date_str: str | None) -> date | None:
    """
    Parse transaction date string into a date object.
    
    Args:
        date_str: Date string in format "YYYY/MM/DD" (e.g., "2025/10/02")
    
    Returns:
        date object or None if parsing fails or date is "Unknown"
    """
    if not date_str or date_str.strip().lower() == "unknown":
        return None
    
    try:
        # Parse YYYY/MM/DD format
        from datetime import datetime
        parsed = datetime.strptime(date_str.strip(), "%Y/%m/%d")
        return parsed.date()
    except (ValueError, AttributeError):
        return None


def transactions(team_id: int, timeout: float | None = None) -> list[PlayerTransaction]:
    """
    Get all team transactions (joins, leaves, inactive status changes, etc.).
    
    Retrieves the complete transaction history for a team from the VLR.gg transactions page.
    Each transaction includes the date, action type, player information, position, and reference URL.
    
    Args:
        team_id: Team ID from VLR.gg (e.g., 1034 for NRG)
        timeout: Request timeout in seconds (default: 5.0)
    
    Returns:
        List of PlayerTransaction objects, ordered by date (most recent first).
        Returns empty list if team not found or has no transactions.
    
    Raises:
        NetworkError: If the request fails after retries
    
    Example:
        >>> import vlrdevapi as vlr
        >>> 
        >>> # Get all transactions for NRG
        >>> txns = vlr.teams.transactions(team_id=1034)
        >>> 
        >>> # Display recent transactions
        >>> for txn in txns[:5]:
        ...     if txn.date:
        ...         print(f"{txn.date.strftime('%Y/%m/%d')}: {txn.ign} - {txn.action} ({txn.position})")
        ...     else:
        ...         print(f"Unknown: {txn.ign} - {txn.action} ({txn.position})")
        2025/10/02: FiNESSE - leave (Player)
        2025/05/09: skuba - join (Player)
        
        >>> # Filter by action type
        >>> joins = [t for t in txns if t.action == "join"]
        >>> leaves = [t for t in txns if t.action == "leave"]
    
    Note:
        Transaction actions include: 'join', 'leave', 'inactive', and others.
        All text fields are cleaned of extra whitespace, tabs, and newlines.
    """
    url = f"{_config.vlr_base}/team/transactions/{team_id}"
    effective_timeout = timeout if timeout is not None else _config.default_timeout
    try:
        html = fetch_html(url, effective_timeout)
    except NetworkError:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    
    # Find the transactions table
    table = soup.select_one("table.wf-faux-table")
    if not table:
        return []
    
    tbody = table.select_one("tbody")
    if not tbody:
        return []
    
    transactions_list: list[PlayerTransaction] = []
    
    # Process each transaction row
    for row in tbody.select("tr.txn-item"):
        # Extract date
        date_td = row.select_one("td:nth-of-type(1)")
        date_str = normalize_whitespace(extract_text(date_td)) if date_td else None
        if date_str == "":
            date_str = None
        
        # Parse date
        transaction_date = _parse_transaction_date(date_str)
        
        # Extract action
        action_td = row.select_one("td.txn-item-action")
        action = normalize_whitespace(extract_text(action_td)) if action_td else None
        if action == "":
            action = None
        
        # Extract country from flag using utility function
        flag_td = row.select_one("td:nth-of-type(3)")
        country_code = extract_country_code(flag_td)
        country = map_country_code(country_code) if country_code else None
        
        # Extract player info
        player_td = row.select_one("td:nth-of-type(4)")
        player_id = None
        ign = None
        real_name = None
        
        if player_td:
            # Get player link
            player_link = player_td.select_one("a[href]")
            if player_link:
                href_val = player_link.get("href")
                href = href_val if isinstance(href_val, str) else None
                player_id = extract_id_from_url(href, "player")
                ign = normalize_whitespace(extract_text(player_link))
                if ign == "":
                    ign = None
            
            # Get real name
            real_name_el = player_td.select_one(".ge-text-light")
            if real_name_el:
                real_name = normalize_whitespace(extract_text(real_name_el))
                if real_name == "":
                    real_name = None
        
        # Extract position
        position_td = row.select_one("td:nth-of-type(5)")
        position = normalize_whitespace(extract_text(position_td)) if position_td else None
        if position == "":
            position = None
        
        # Extract reference URL
        reference_url = None
        reference_td = row.select_one("td:nth-of-type(6)")
        if reference_td:
            ref_link = reference_td.select_one("a[href]")
            if ref_link:
                href_val = ref_link.get("href")
                href = href_val if isinstance(href_val, str) else None
                reference_url = normalize_whitespace(href or "")
                if reference_url == "":
                    reference_url = None
        
        transactions_list.append(PlayerTransaction(
            date=transaction_date,
            action=action,
            player_id=player_id,
            ign=ign,
            real_name=real_name,
            country=country,
            position=position,
            reference_url=reference_url,
        ))
    
    return transactions_list


def previous_players(team_id: int, timeout: float | None = None) -> list[PreviousPlayer]:
    """
    Get all previous and current players with their status calculated from transaction history.
    
    This function analyzes all team transactions to determine each player's current status,
    join/leave dates, and complete transaction history. Players are grouped by their player_id
    and their status is calculated based on their most recent transactions.
    
    Status Determination Logic:
        - **Active**: Player has joined and has no subsequent leave/inactive action
        - **Left**: Player has a 'leave' action as their most recent status change
        - **Inactive**: Player has an 'inactive' action as their most recent status change
        - **Unknown**: Cannot determine status from available transactions
    
    Args:
        team_id: Team ID from VLR.gg (e.g., 1034 for NRG)
        timeout: Request timeout in seconds (default: 5.0)
    
    Returns:
        List of PreviousPlayer objects, sorted by most recent activity (latest transaction first).
        Each player includes:
        - Basic info (IGN, real name, country, position)
        - Calculated status
        - Join and leave dates
        - Complete transaction history
        
        Returns empty list if team not found or has no transactions.
    
    Raises:
        NetworkError: If the request fails after retries
    
    Example:
        >>> import vlrdevapi as vlr
        >>> 
        >>> # Get all players
        >>> players = vlr.teams.previous_players(team_id=1034)
        >>> 
        >>> # Display player status
        >>> for player in players[:5]:
        ...     print(f"{player.ign} - {player.status} ({player.position})")
        ...     join_str = player.join_date.strftime('%Y/%m/%d') if player.join_date else 'Unknown'
        ...     leave_str = player.leave_date.strftime('%Y/%m/%d') if player.leave_date else 'None'
        ...     print(f"  Joined: {join_str}, Left: {leave_str}")
        mada - Active (Player)
          Joined: 2024/10/10, Left: None
        FiNESSE - Left (Player)
          Joined: 2024/05/09, Left: 2025/10/02
        
        >>> # Filter by status
        >>> active = [p for p in players if p.status == "Active"]
        >>> left = [p for p in players if p.status == "Left"]
        >>> 
        >>> # Filter by position
        >>> coaches = [p for p in players if p.position and "coach" in p.position.lower()]
        >>> 
        >>> # Access transaction history
        >>> player = players[0]
        >>> for txn in player.transactions:
        ...     print(f"{txn.date}: {txn.action}")
    
    Note:
        - Players without a player_id are excluded from results
        - Transaction dates are date objects or None if not available
        - Players can have multiple join/leave cycles (rejoining after leaving)
        - Status is calculated from the most recent transaction
        - All text fields are cleaned of extra whitespace
    """
    txns = transactions(team_id, timeout)
    
    # Group transactions by player
    player_txns: dict[int, list[PlayerTransaction]] = defaultdict(list)
    player_info: dict[int, dict[str, str | None]] = {}
    
    for txn in txns:
        if txn.player_id is None:
            continue
        
        player_txns[txn.player_id].append(txn)
        
        # Store player info (use most recent non-None values)
        if txn.player_id not in player_info:
            player_info[txn.player_id] = {
                'ign': txn.ign,
                'real_name': txn.real_name,
                'country': txn.country,
                'position': txn.position,
            }
        else:
            # Update with non-None values
            if txn.ign:
                player_info[txn.player_id]['ign'] = txn.ign
            if txn.real_name:
                player_info[txn.player_id]['real_name'] = txn.real_name
            if txn.country:
                player_info[txn.player_id]['country'] = txn.country
            if txn.position:
                player_info[txn.player_id]['position'] = txn.position
    
    # Calculate status for each player
    players: list[PreviousPlayer] = []
    
    for player_id, txn_list in player_txns.items():
        # Sort transactions by date (most recent first)
        # Use a sentinel date for None values (far in the past)
        from datetime import date as date_type
        sentinel_date = date_type(1900, 1, 1)
        sorted_txns = sorted(txn_list, key=lambda t: t.date or sentinel_date, reverse=True)
        
        # Determine status based on transactions
        status = "Unknown"
        join_date = None
        leave_date = None
        
        # Separate transactions with known dates from unknown dates
        txns_with_dates = [t for t in sorted_txns if t.date is not None]
        _txns_without_dates = [t for t in sorted_txns if t.date is None]
        
        # Find join and leave dates (most recent of each)
        # Process chronologically to track the player's journey
        for txn in reversed(sorted_txns):  # Process chronologically (oldest first)
            action_lower = (txn.action or "").lower()
            
            if action_lower == "join":
                # Update join date to the most recent join
                join_date = txn.date
                # Reset leave date when rejoining
                leave_date = None
            elif action_lower in ["leave", "inactive"]:
                # Update leave date
                leave_date = txn.date
        
        # Determine status based on most recent action WITH A KNOWN DATE
        # If we have transactions with dates, use those to determine status
        if txns_with_dates:
            most_recent_dated_action = (txns_with_dates[0].action or "").lower()
            
            if most_recent_dated_action == "join":
                status = "Active"
            elif most_recent_dated_action == "leave":
                status = "Left"
            elif most_recent_dated_action == "inactive":
                status = "Inactive"
            else:
                # Fallback based on dates
                if leave_date and not join_date:
                    status = "Left"
                elif join_date and not leave_date:
                    status = "Active"
                else:
                    status = "Unknown"
        else:
            # All transactions have unknown dates, use the first action
            most_recent_action = (sorted_txns[0].action or "").lower()
            
            if most_recent_action == "join":
                status = "Active"
            elif most_recent_action == "leave":
                status = "Left"
            elif most_recent_action == "inactive":
                status = "Inactive"
            else:
                status = "Unknown"
        
        info = player_info.get(player_id, {'ign': None, 'real_name': None, 'country': None, 'position': None})
        
        players.append(PreviousPlayer(
            player_id=player_id,
            ign=info['ign'],
            real_name=info['real_name'],
            country=info['country'],
            position=info['position'],
            status=status,
            join_date=join_date,
            leave_date=leave_date,
            transactions=sorted_txns,
        ))
    
    # Sort by most recent activity (based on latest transaction date)
    from datetime import date as date_type
    sentinel_date = date_type(1900, 1, 1)
    players.sort(key=lambda p: p.transactions[0].date or sentinel_date, reverse=True)
    
    return players
