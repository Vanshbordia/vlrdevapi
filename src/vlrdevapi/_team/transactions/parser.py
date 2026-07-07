
from selectolax.parser import HTMLParser, Node

from vlrdevapi._team.transactions.models import (
    TeamTransaction,
    TeamTransactions,
    TransactionAction,
    TransactionPlayer,
)
from vlrdevapi.commons.countries import get_country_name
from vlrdevapi.commons.datetime import date_to_utc_datetime, parse_vlr_date


def parse_team_transactions(html: HTMLParser, team_id: int) -> TeamTransactions:
    result = TeamTransactions(team_id=team_id)

    table = html.css_first("table.wf-faux-table")
    if not table:
        return result

    rows = table.css("tr.txn-item")
    for row in rows:
        transaction = _parse_transaction_row(row)
        if transaction:
            result.transactions.append(transaction)

    return result


def _parse_transaction_row(row: Node) -> TeamTransaction | None:
    tds = row.css("td")
    if len(tds) < 6:
        return None

    date_td = tds[0]
    date_text = date_td.text(strip=True)
    parsed = parse_vlr_date(date_text)
    transaction_date = date_to_utc_datetime(parsed) if parsed else None

    action_td = tds[1]
    action_text = action_td.text(strip=True).capitalize()
    try:
        action = TransactionAction(action_text)
    except ValueError:
        return None

    flag_td = tds[2]
    flag_el = flag_td.css_first("i.flag")
    country = ""
    if flag_el:
        class_attr = flag_el.attributes.get("class") or ""
        if "mod-" in class_attr:
            code = class_attr.split("mod-")[-1].split()[0]
            country = get_country_name(code)

    player_td = tds[3]
    player = _parse_player_info(player_td)
    player.country = country

    position_td = tds[4]
    position = position_td.text(strip=True)

    source_td = tds[5]
    source_url = ""
    source_link = source_td.css_first("a[href]")
    if source_link:
        href = source_link.attributes.get("href") or ""
        if href.startswith("http"):
            source_url = href

    return TeamTransaction(
        date=transaction_date,
        action=action,
        player=player,
        position=position,
        source_url=source_url,
    )


def _parse_player_info(td: Node) -> TransactionPlayer:
    player = TransactionPlayer()

    a_el = td.css_first("a[href*='/player/']")
    if a_el:
        href = a_el.attributes.get("href") or ""
        if "/player/" in href:
            parts = href.split("/player/")[-1].split("/")
            if parts and parts[0].isdigit():
                player.id = int(parts[0])

        player.ign = a_el.text(strip=True)

    real_name_el = td.css_first("div.ge-text-light")
    if real_name_el:
        player.real_name = real_name_el.text(strip=True)

    return player
