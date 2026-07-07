from selectolax.parser import HTMLParser


def _parse_team_basic(html: HTMLParser) -> dict[str, str]:
    data = {"name": "", "tag": ""}

    title_el = html.css_first("title")
    if title_el:
        title_text = title_el.text(strip=True)
        if " - VLR.gg" in title_text:
            data["name"] = title_text.replace(" - VLR.gg", "").strip()

    header_el = html.css_first(".team-header")
    if header_el:
        name_el = header_el.css_first("h1.wf-title")
        if name_el:
            data["name"] = name_el.text(strip=True)

        tag_el = header_el.css_first("h2.team-header-tag")
        if tag_el:
            data["tag"] = tag_el.text(strip=True)

        if not data["tag"] and data["name"] and len(data["name"]) <= 4:
            data["tag"] = data["name"]

    return data
