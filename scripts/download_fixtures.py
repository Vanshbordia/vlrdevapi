import asyncio
from pathlib import Path

import httpx

BASE_URL = "https://www.vlr.gg"
FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "test_html"
DELAY = 0.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.7",
    "Sec-Ch-Ua": '"Google Chrome";v="147", "Not(A:Brand";v="99", "Chromium";v="147"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}


ROUTES: list[tuple[str, str, dict[str, str]]] = []

# ── Matches ────────────────────────────────────────────────────
ROUTES += [
    ("/matches", "matches/matches.html", {}),
    ("/matches/?page=2", "matches/matches_page2.html", {}),
    ("/matches/results", "matches/results.html", {}),
    ("/matches/results/?page=2", "matches/results_page2.html", {}),
]

# ── News ───────────────────────────────────────────────────────
ROUTES += [
    ("/news", "news/news.html", {}),
    ("/news/?page=2", "news/news_page2.html", {}),
    ("/news/?page=300", "news/news_page300.html", {}),
    ("/734100", "news/article_734100.html", {}),
    ("/720033/americas-recent-victors-start-strong-in-week-1", "news/article_720033.html", {}),
]

# ── Events ─────────────────────────────────────────────────────
ROUTES += [
    ("/events", "events/events.html", {}),
    ("/events/?region=all", "events/events_region_all.html", {}),
    ("/events/?region=26", "events/events_region_26_americas.html", {}),
    ("/events/?region=27", "events/events_region_27_emea.html", {}),
    ("/events/?region=28", "events/events_region_28_pacific.html", {}),
    ("/events/?region=24", "events/events_region_24_china.html", {}),
]

TIERS = {
    60: "vct",
    61: "vcl",
    62: "t3",
    63: "game_changers",
    64: "collegiate",
    67: "offseason",
}

REGIONS = {
    "all": "all",
    "26": "americas",
    "27": "emea",
    "28": "pacific",
    "24": "china",
}

for region_code, region_name in REGIONS.items():
    for tier_code, tier_name in TIERS.items():
        ROUTES.append(
            (
                f"/events/?region={region_code}&tier={tier_code}",
                f"events/events_region_{region_code}_{region_name}_tier_{tier_code}_{tier_name}.html",
                {},
            )
        )

# ── Event detail ───────────────────────────────────────────────
EVENT_ID = 2682
EVENT_SLUG = "vct-2026-americas-kickoff"
SERIES_ID = 5221

ROUTES += [
    (
        f"/event/{EVENT_ID}/{EVENT_SLUG}",
        f"event/{EVENT_ID}_{EVENT_SLUG}/overview.html",
        {},
    ),
    (
        f"/event/matches/{EVENT_ID}/{EVENT_SLUG}/?series_id={SERIES_ID}&group=all",
        f"event/{EVENT_ID}_{EVENT_SLUG}/matches_all.html",
        {},
    ),
    (
        f"/event/matches/{EVENT_ID}/{EVENT_SLUG}/?series_id={SERIES_ID}&group=upcoming",
        f"event/{EVENT_ID}_{EVENT_SLUG}/matches_upcoming.html",
        {},
    ),
    (
        f"/event/matches/{EVENT_ID}/{EVENT_SLUG}/?series_id={SERIES_ID}&group=completed",
        f"event/{EVENT_ID}_{EVENT_SLUG}/matches_completed.html",
        {},
    ),
]

# ── Event detail: additional events for info parsing ────────────
ADDITIONAL_EVENTS = [
    (2863, "vct-2026-emea-stage-1"),
    (2949, "gameon-productivity-and-technology-tournament-2026"),
    (2847, "challengers-2026-japan-split-1"),
    (58, "100t-x-cashapp-gamers-for-equality"),
    (2763, "tesfed-turkish-cup-2025"),
    (2544, "morocco-gaming-expo-2025"),
    (3074, "raidiant-academy-2026"),
]

for _eid, _eslug in ADDITIONAL_EVENTS:
    ROUTES.append(
        (
            f"/event/{_eid}/{_eslug}",
            f"event/{_eid}_{_eslug}/overview.html",
            {},
        )
    )

# ── Event 2860 matches (for stages parser test) ─────────────────
ROUTES += [
    ("/event/matches/2860", "event/2860/matches.html", {}),
]

# ── Event standings pages (for standings filtering tests) ──────
ROUTES += [
    ("/event/2283/valorant-champions-2025", "event/2283_valorant-champions-2025/overview.html", {}),
    ("/event/2682/vct-2026-americas-kickoff", "event/2682_vct-2026-americas-kickoff/overview.html", {}),
]

# ── Event matches pages ─────────────────────────────────────────
EVENTS_WITH_MATCHES = [
    (2863, "vct-2026-emea-stage-1"),
    (2760, "valorant-masters-santiago-2026"),
]

for _eid, _eslug in EVENTS_WITH_MATCHES:
    ROUTES += [
        (
            f"/event/matches/{_eid}/{_eslug}/?series_id=all&group=all",
            f"event/{_eid}_{_eslug}/matches_all.html",
            {},
        ),
        (
            f"/event/matches/{_eid}/{_eslug}/?series_id=all&group=completed",
            f"event/{_eid}_{_eslug}/matches_completed.html",
            {},
        ),
        (
            f"/event/matches/{_eid}/{_eslug}/?series_id=all&group=upcoming",
            f"event/{_eid}_{_eslug}/matches_upcoming.html",
            {},
        ),
    ]

# ── Reference match for timezone detection ─────────────────────
ROUTES += [
    (
        "/670471/paper-rex-vs-leviat-n-valorant-masters-london-2026-gf",
        "matches/reference_match_timezone.html",
        {},
    ),
]

# ── Game / Series detail ───────────────────────────────────────
SERIES_ID_GAME = 542272
SERIES_SLUG = "nrg-vs-fnatic-valorant-champions-2025-gf"
GAME_ID = 233478

ROUTES += [
    (
        f"/{SERIES_ID_GAME}/{SERIES_SLUG}",
        f"series/{SERIES_ID_GAME}_{SERIES_SLUG}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_GAME}/{SERIES_SLUG}/?game={GAME_ID}&tab=overview",
        f"series/{SERIES_ID_GAME}_{SERIES_SLUG}/game_{GAME_ID}_overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_GAME}/{SERIES_SLUG}/?game={GAME_ID}&tab=performance",
        f"series/{SERIES_ID_GAME}_{SERIES_SLUG}/game_{GAME_ID}_performance.html",
        {},
    ),
    (
        f"/{SERIES_ID_GAME}/{SERIES_SLUG}/?game={GAME_ID}&tab=economy",
        f"series/{SERIES_ID_GAME}_{SERIES_SLUG}/game_{GAME_ID}_economy.html",
        {},
    ),
    (
        f"/{SERIES_ID_GAME}/{SERIES_SLUG}/?game={GAME_ID}&tab=all",
        f"series/{SERIES_ID_GAME}_{SERIES_SLUG}/game_{GAME_ID}_all.html",
        {},
    ),
]

# ── Player detail ──────────────────────────────────────────────
PLAYER_PAGES = [
    (11225, "ethan"),
    (53, "inspire"),
    (46051, "yuvi"),
]

for _pid, _pslug in PLAYER_PAGES:
    ROUTES += [
        (
            f"/player/{_pid}/{_pslug}",
            f"player/{_pid}_{_pslug}/overview.html",
            {},
        ),
        (
            f"/player/matches/{_pid}/{_pslug}/",
            f"player/{_pid}_{_pslug}/matches.html",
            {},
        ),
        (
            f"/player/matches/{_pid}/{_pslug}/?page=2",
            f"player/{_pid}_{_pslug}/matches_page2.html",
            {},
        ),
    ]

# ── Team detail ────────────────────────────────────────────────
TEAMS = [
    (120, "100-thieves"),
    (2, "sentinels"),
    (17676, "humble-5"),  # Team without current roster for testing
    (1034, "nrg"),  # Added NRG for testing
    (8326, None),  # M3 Champions — no slug in URL
    (682, None),  # Gambit Esports — no slug in URL
]

for TEAM_ID, TEAM_SLUG in TEAMS:
    team_path = f"/team/{TEAM_ID}/{TEAM_SLUG}" if TEAM_SLUG else f"/team/{TEAM_ID}/"
    ROUTES += [
        (team_path, f"team/{TEAM_ID}/overview_light.html", {}),
        (
            team_path,
            f"team/{TEAM_ID}/overview_dark.html",
            {"settings": "%7B%22dark_mode%22%3A1%7D"},
        ),
        (
            f"/team/matches/{TEAM_ID}/?core_id=all&group=completed",
            f"team/{TEAM_ID}/completed_matches.html",
            {},
        ),
        (
            f"/team/transactions/{TEAM_ID}/",
            f"team/{TEAM_ID}/transactions.html",
            {},
        ),
        (
            f"/team/stats/{TEAM_ID}/",
            f"team/{TEAM_ID}/stats.html",
            {},
        ),
    ]

# ── Team with upcoming matches + paginated completed matches ───
ROUTES += [
    (
        "/team/13790/wolves-esports",
        "team/13790/overview_light.html",
        {},
    ),
    (
        "/team/14137/titan-esports-club",
        "team/14137/overview_light.html",
        {},
    ),
    (
        "/team/matches/120/?core_id=all&group=completed&page=2",
        "team/120/completed_matches_page2.html",
        {},
    ),
]

STATS_EVENT_ID = 2860
STATS_SERIES_ID = 5556
STATS_SUBSERIES_ID = 37169

for TEAM_ID, _ in TEAMS:
    ROUTES += [
        (
            f"/team/stats/{TEAM_ID}/?event_id={STATS_EVENT_ID}",
            f"team/{TEAM_ID}/stats_event_{STATS_EVENT_ID}.html",
            {},
        ),
        (
            f"/team/stats/{TEAM_ID}/?event_id={STATS_EVENT_ID}&series_id={STATS_SERIES_ID}",
            f"team/{TEAM_ID}/stats_event_{STATS_EVENT_ID}_series_{STATS_SERIES_ID}.html",
            {},
        ),
        (
            f"/team/stats/{TEAM_ID}/?event_id={STATS_EVENT_ID}&series_id={STATS_SERIES_ID}&subseries_id={STATS_SUBSERIES_ID}",
            f"team/{TEAM_ID}/stats_event_{STATS_EVENT_ID}_series_{STATS_SERIES_ID}_subseries_{STATS_SUBSERIES_ID}.html",
            {},
        ),
        (
            f"/team/stats/{TEAM_ID}/?date_start=2025-01-01&date_end=2025-12-31",
            f"team/{TEAM_ID}/stats_date_range.html",
            {},
        ),
        (
            f"/team/stats/{TEAM_ID}/?date_start=2025-06-01&date_end=2025-06-30",
            f"team/{TEAM_ID}/stats_date_june_2025.html",
            {},
        ),
    ]

MATCHES_FOR_SERIES = [
    645484,
    645479,
    644718,
]

for MATCH_ID in MATCHES_FOR_SERIES:
    ROUTES += [
        (f"/{MATCH_ID}", f"series/{MATCH_ID}/overview.html", {}),
    ]

# ── Series 644718 game tabs (rounds + economy) ────────────────
GAME_ID_644718 = 258363
ROUTES += [
    (
        f"/644718?game={GAME_ID_644718}&tab=overview",
        f"series/644718/game_{GAME_ID_644718}_rounds.html",
        {},
    ),
    (
        f"/644718?game={GAME_ID_644718}&tab=economy",
        f"series/644718/game_{GAME_ID_644718}_economy.html",
        {},
    ),
]


# ── Series 704037 Bo1 (single-map game, no nav tabs, no veto) ─
SERIES_ID_BO1 = 704037
SERIES_SLUG_BO1 = "mushoku-vs-fallen-angels-game-changers-2026-emea-stage-2-promotion-relegation-r1"
GAME_ID_BO1 = 274641

ROUTES += [
    (
        f"/{SERIES_ID_BO1}/{SERIES_SLUG_BO1}",
        f"series/{SERIES_ID_BO1}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1}?game={GAME_ID_BO1}&tab=overview",
        f"series/{SERIES_ID_BO1}/game_{GAME_ID_BO1}_overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1}?game={GAME_ID_BO1}&tab=performance",
        f"series/{SERIES_ID_BO1}/game_{GAME_ID_BO1}_performance.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1}?game={GAME_ID_BO1}&tab=economy",
        f"series/{SERIES_ID_BO1}/game_{GAME_ID_BO1}_economy.html",
        {},
    ),
]

# ── Series 64819 Bo1 (single-map, bans + decider veto) ────────
SERIES_ID_BO1_VETO = 64819
GAME_ID_BO1_VETO = 65212

ROUTES += [
    (
        f"/{SERIES_ID_BO1_VETO}",
        f"series/{SERIES_ID_BO1_VETO}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_VETO}?game={GAME_ID_BO1_VETO}&tab=overview",
        f"series/{SERIES_ID_BO1_VETO}/game_{GAME_ID_BO1_VETO}_overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_VETO}?game={GAME_ID_BO1_VETO}&tab=performance",
        f"series/{SERIES_ID_BO1_VETO}/game_{GAME_ID_BO1_VETO}_performance.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_VETO}?game={GAME_ID_BO1_VETO}&tab=economy",
        f"series/{SERIES_ID_BO1_VETO}/game_{GAME_ID_BO1_VETO}_economy.html",
        {},
    ),
]

# ── Series 30788 Bo1 (single-map, pick veto) ──────────────────
SERIES_ID_BO1_PICK = 30788
GAME_ID_BO1_PICK = 47971

ROUTES += [
    (
        f"/{SERIES_ID_BO1_PICK}",
        f"series/{SERIES_ID_BO1_PICK}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_PICK}?game={GAME_ID_BO1_PICK}&tab=overview",
        f"series/{SERIES_ID_BO1_PICK}/game_{GAME_ID_BO1_PICK}_overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_PICK}?game={GAME_ID_BO1_PICK}&tab=performance",
        f"series/{SERIES_ID_BO1_PICK}/game_{GAME_ID_BO1_PICK}_performance.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO1_PICK}?game={GAME_ID_BO1_PICK}&tab=economy",
        f"series/{SERIES_ID_BO1_PICK}/game_{GAME_ID_BO1_PICK}_economy.html",
        {},
    ),
]

# ── Series 130685 Bo5 (pistol/conv/bonus economy matrix, OT maps) ─
SERIES_ID_BO5_2022 = 130685
SERIES_SLUG_BO5_2022 = "loud-vs-optic-gaming-valorant-champions-2022-gf"
GAMES_BO5_2022 = [95131, 95132, 95133, 95134]

ROUTES += [
    (
        f"/{SERIES_ID_BO5_2022}/{SERIES_SLUG_BO5_2022}",
        f"series/{SERIES_ID_BO5_2022}_{SERIES_SLUG_BO5_2022}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO5_2022}/{SERIES_SLUG_BO5_2022}/?game={GAMES_BO5_2022[0]}&tab=economy",
        f"series/{SERIES_ID_BO5_2022}_{SERIES_SLUG_BO5_2022}/game_{GAMES_BO5_2022[0]}_economy.html",
        {},
    ),
]
for _gid in GAMES_BO5_2022:
    ROUTES += [
        (
            f"/{SERIES_ID_BO5_2022}/{SERIES_SLUG_BO5_2022}/?game={_gid}&tab=overview",
            f"series/{SERIES_ID_BO5_2022}_{SERIES_SLUG_BO5_2022}/game_{_gid}_overview.html",
            {},
        ),
        (
            f"/{SERIES_ID_BO5_2022}/{SERIES_SLUG_BO5_2022}/?game={_gid}&tab=performance",
            f"series/{SERIES_ID_BO5_2022}_{SERIES_SLUG_BO5_2022}/game_{_gid}_performance.html",
            {},
        ),
    ]

# ── Series 754737 Bo5 (Champions 2026 GF; round grids + economy matrix) ─
SERIES_ID_BO5_2026 = 754737
SERIES_SLUG_BO5_2026 = "loud-vs-team-vitality-valorant-champions-2026-gf"
GAMES_BO5_2026 = [283286, 283287, 283288, 283289]

ROUTES += [
    (
        f"/{SERIES_ID_BO5_2026}/{SERIES_SLUG_BO5_2026}",
        f"series/{SERIES_ID_BO5_2026}_{SERIES_SLUG_BO5_2026}/overview.html",
        {},
    ),
    (
        f"/{SERIES_ID_BO5_2026}/{SERIES_SLUG_BO5_2026}/?game={GAMES_BO5_2026[0]}&tab=economy",
        f"series/{SERIES_ID_BO5_2026}_{SERIES_SLUG_BO5_2026}/game_{GAMES_BO5_2026[0]}_economy.html",
        {},
    ),
]
for _gid in GAMES_BO5_2026:
    ROUTES += [
        (
            f"/{SERIES_ID_BO5_2026}/{SERIES_SLUG_BO5_2026}/?game={_gid}&tab=overview",
            f"series/{SERIES_ID_BO5_2026}_{SERIES_SLUG_BO5_2026}/game_{_gid}_overview.html",
            {},
        ),
        (
            f"/{SERIES_ID_BO5_2026}/{SERIES_SLUG_BO5_2026}/?game={_gid}&tab=performance",
            f"series/{SERIES_ID_BO5_2026}_{SERIES_SLUG_BO5_2026}/game_{_gid}_performance.html",
            {},
        ),
    ]

# ── Upcoming series (best_of + TBD map tabs) ─────────────────
SERIES_ID_UPCOMING = 777946
SERIES_SLUG_UPCOMING = "titan-esports-club-vs-unsettled-resentment-vct-china-2026-threshold-week-1-qf"

ROUTES.append(
    (
        f"/{SERIES_ID_UPCOMING}/{SERIES_SLUG_UPCOMING}",
        f"series/{SERIES_ID_UPCOMING}/overview.html",
        {},
    ),
)

# ── Replay/logs tab fixtures (series.replay) ──────────────────
SERIES_LOG_SAMPLES = [
    (754737, "loud-vs-team-vitality-valorant-champions-2026-gf", 283288),
    (754742, "100-thieves-vs-g2-esports-valorant-champions-2026-lr3", 283305),
    (754743, "team-vitality-vs-100-thieves-valorant-champions-2026-lbf", 286701),
    (378829, "edward-gaming-vs-team-heretics-valorant-champions-2024-gf", 180437),
]

for _sid, _sslug, _gid in SERIES_LOG_SAMPLES:
    ROUTES.append(
        (
            f"/{_sid}/{_sslug}/?game={_gid}&tab=logs",
            f"series/{_sid}_{_sslug}/game_{_gid}_logs.html",
            {},
        ),
    )

# Game overview tabs for replay player/team ID enrichment tests
# (`?game={gid}&tab=overview` carries real VLR team + player IDs).
for _sid, _sslug, _gid in SERIES_LOG_SAMPLES:
    ROUTES.append(
        (
            f"/{_sid}/{_sslug}/?game={_gid}&tab=overview",
            f"series/{_sid}_{_sslug}/game_{_gid}_overview.html",
            {},
        ),
    )

# Unplayed map (Abyss, game 4 of the 2026 GF): graceful empty replay data.
ROUTES.append(
    (
        "/754737/loud-vs-team-vitality-valorant-champions-2026-gf/?game=283290&tab=logs",
        "series/754737_loud-vs-team-vitality-valorant-champions-2026-gf/game_283290_logs.html",
        {},
    ),
)

# ── Series: forfeit and notes parsing ───────────────────────
SERIES_FORFEIT_NOTES = [
    (477343, "shopify-rebellion-gold-vs-yfp-x-game-changers-2025-north-america-stage-1-r3"),
    (67357, "t1-vs-tsm-champions-tour-north-america-stage-1-challengers-lr4"),
    (155313, "blind-esports-vs-onlyfriends-nsg-yuddha-phase-2-all-india-championship-playoffs-lr1"),
    (459856, "team-liquid-vs-karmine-corp-champions-tour-2025-emea-stage-1-w5"),
    (715117, "shopify-rebellion-black-vs-2game-esports-vcl-26-americas-last-chance-qualifier-main-event-gf"),
]

for _sid, _sslug in SERIES_FORFEIT_NOTES:
    ROUTES.append((f"/{_sid}/{_sslug}", f"series/{_sid}/overview.html", {}))


def _parse_last_page(html: str) -> int | None:
    """Parse the highest page number from vlr.gg pagination controls."""
    from selectolax.lexbor import LexborHTMLParser as HTMLParser

    doc = HTMLParser(html)
    pagination = doc.css_first("div.action-container-pages")
    if pagination is None:
        return None
    max_page = 0
    for el in pagination.css("a.btn.mod-page, span.btn.mod-page"):
        try:
            num = int(el.text(strip=True))
            max_page = max(max_page, num)
        except ValueError:
            continue
    return max_page if max_page > 0 else None


async def _download_news_last_page(client: httpx.AsyncClient) -> None:
    """Dynamically determine and download the last news page."""
    out = FIXTURES_DIR / "news" / "news_last_page.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        print("SKIP (exists) news/news_last_page.html")
        return

    print("GET /news (to find last page number)")
    try:
        resp = await client.get("/news")
        resp.raise_for_status()
        last_page = _parse_last_page(resp.text)
        if last_page is None:
            print("         WARNING: could not parse last page number")
            return

        last_path = f"/news/?page={last_page}"
        print(f"GET {BASE_URL}{last_path}")
        resp2 = await client.get(last_path)
        resp2.raise_for_status()
        out.write_text(resp2.text, encoding="utf-8")
        print(f"         -> {out.relative_to(FIXTURES_DIR.parent)}")
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"         ERROR {e}")


async def download_all():
    async with httpx.AsyncClient(
        base_url=BASE_URL, headers=HEADERS, follow_redirects=True, timeout=30
    ) as client:
        await _download_news_last_page(client)

        total = len(ROUTES)
        for i, (path, filename, cookies) in enumerate(ROUTES, 1):
            out = FIXTURES_DIR / filename
            out.parent.mkdir(parents=True, exist_ok=True)

            if out.exists():
                print(f"[{i}/{total}] SKIP (exists) {filename}")
                continue

            url = BASE_URL + path
            print(f"[{i}/{total}] GET {url}")
            try:
                resp = await client.get(path, cookies=cookies)
                resp.raise_for_status()
                out.write_text(resp.text, encoding="utf-8")
                print(f"         -> {out.relative_to(FIXTURES_DIR.parent)}")
            except httpx.HTTPStatusError as e:
                print(f"         ERROR {e.response.status_code}")
            except httpx.RequestError as e:
                print(f"         ERROR {e}")

            await asyncio.sleep(DELAY)

    print(f"\nDone. Files saved to {FIXTURES_DIR}")


if __name__ == "__main__":
    asyncio.run(download_all())
