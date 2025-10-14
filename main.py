"""Test script for search functionality."""

import vlrdevapi as vlr


def main():
    """Test search functionality with various queries."""
    
    print("=" * 80)
    print("VLR.gg Search Module Test")
    print("=" * 80)
    
    # Test 1: Search for everything related to "nrg"
    print("\n1. Searching for 'nrg' (all types)...")
    print("-" * 80)
    results = vlr.search.search("nrg")
    
    print(f"Query: {results.query}")
    print(f"Total Results: {results.total_results}")
    print(results)
    
    if results.teams:
        print(f"Teams ({len(results.teams)}):")
        for team in results.teams:
            status = "inactive" if team.is_inactive else "active"
            country = f", {team.country}" if team.country else ""
            print(f"  - {team.name} (ID: {team.team_id}{country}, {status})")
            print(f"    URL: {team.url}")
        print()
    
    if results.players:
        print(f"Players ({len(results.players)}):")
        for player in results.players[:5]:
            real_name = f" ({player.real_name})" if player.real_name else ""
            country = f", {player.country}" if player.country else ""
            print(f"  - {player.ign}{real_name} (ID: {player.player_id}{country})")
            print(f"    URL: {player.url}")
        if len(results.players) > 5:
            print(f"  ... and {len(results.players) - 5} more players")
        print()
    
    if results.events:
        print(f"Events ({len(results.events)}):")
        for event in results.events[:5]:
            date_info = f" - {event.date_range}" if event.date_range else ""
            prize_info = f" - {event.prize}" if event.prize else ""
            print(f"  - {event.name}{date_info}{prize_info}")
            print(f"    URL: {event.url}")
        if len(results.events) > 5:
            print(f"  ... and {len(results.events) - 5} more events")
        print()
    
    if results.series:
        print(f"Series ({len(results.series)}):")
        for s in results.series:
            print(f"  - {s.name} (ID: {s.series_id})")
            print(f"    URL: {s.url}")
        print()
    
    # Test 2: Search for players only
    print("\n2. Searching for 'tenz' (players only)...")
    print("-" * 80)
    players = vlr.search.search_players("tenz")
    print(players)
    print(f"Found {len(players)} players:")
    for player in players[:3]:
        real_name = f" ({player.real_name})" if player.real_name else ""
        country = f" - {player.country}" if player.country else ""
        print(f"  - {player.ign}{real_name}{country}")
        print(f"    URL: {player.url}")
    if len(players) > 3:
        print(f"  ... and {len(players) - 3} more")
    print()
    
    # Test 3: Search for teams only
    print("\n3. Searching for 'sentinels' (teams only)...")
    print("-" * 80)
    teams = vlr.search.search_teams("sentinels")
    print(f"Found {len(teams)} teams:")
    for team in teams[:3]:
        status = "inactive" if team.is_inactive else "active"
        country = f" - {team.country}" if team.country else ""
        print(f"  - {team.name}{country} ({status})")
        print(f"    URL: {team.url}")
    if len(teams) > 3:
        print(f"  ... and {len(teams) - 3} more")
    print()
    
    # Test 4: Search for events only
    print("\n4. Searching for 'champions' (events only)...")
    print("-" * 80)
    events = vlr.search.search_events("champions")
    print(f"Found {len(events)} events:")
    for event in events[:3]:
        date_info = f" - {event.date_range}" if event.date_range else ""
        print(f"  - {event.name}{date_info}")
        print(f"    URL: {event.url}")
    if len(events) > 3:
        print(f"  ... and {len(events) - 3} more")
    print()
    
    print("=" * 80)
    print("Search tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
