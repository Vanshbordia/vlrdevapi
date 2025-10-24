import vlrdevapi as vlr
# Paginate when you need historical data
page2 = vlr.matches.completed(limit=5, page=2)