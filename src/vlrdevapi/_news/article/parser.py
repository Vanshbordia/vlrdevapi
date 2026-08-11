"""Parse full news article pages (``/{article_id}/<slug>``).

Articles on vlr.gg use semantic HTML (headings, paragraphs, lists, links,
emphasis, and Twitch clip embeds). The body is exposed both as plain text
and as a Markdown conversion that preserves that structure.
"""

import html as html_module
import re
from datetime import tzinfo
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from selectolax.parser import HTMLParser, Node

from vlrdevapi._news.article.models import NewsArticle
from vlrdevapi.commons.datetime import parse_vlr_iso_datetime
from vlrdevapi.fetcher import BASE_URL

_BLOCK_TAGS = frozenset(
    {
        "p",
        "div",
        "section",
        "article",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "blockquote",
        "pre",
        "iframe",
        "hr",
        "table",
    }
)

_MD_ESCAPES = {"\\": "\\\\", "*": "\\*", "_": "\\_", "[": "\\[", "]": "\\]", "`": "\\`"}


def parse_news_article(
    html: HTMLParser,
    source_tz: ZoneInfo | tzinfo | None = None,
) -> NewsArticle:
    """Parse a full news article page (``/{article_id}/<slug>``).

    Args:
        html: Parsed HTML document of an article page.
        source_tz: Timezone VLR.gg renders local times in. Used only when
            the article's ``datetime`` attribute is naive (no offset);
            offset-aware values are converted to UTC as-is.

    Returns:
        NewsArticle: The article with ``id``, ``title``, ``author``,
        ``date``, ``event_name``, ``event_link``, ``content`` (plain
        text), and ``content_md`` (Markdown). Fields are empty when the
        page does not contain a recognisable article card.

    Examples:
        >>> article = parse_news_article(vlrdevapi_article_html)
        >>> article.author
        'jenopelle'
        >>> article.content_md.startswith('The [Pacific Stage 2]')
        True

    """
    article = NewsArticle()

    card = html.css_first("div.wf-card.mod-article")
    if card is None:
        return article

    canonical = html.css_first("link[rel=canonical]")
    canonical_href = canonical.attributes.get("href") or "" if canonical else ""
    canonical_path = urlsplit(canonical_href).path.lstrip("/")
    try:
        article.id = int(canonical_path.split("/")[0])
    except (ValueError, IndexError):
        article.id = 0

    title_el = card.css_first("h1.wf-title.mod-article-title")
    if title_el:
        article.title = title_el.text(strip=True)

    author_el = card.css_first("a.article-meta-author")
    if author_el:
        article.author = author_el.text(strip=True)

    time_el = card.css_first("time.js-date-toggle")
    if time_el:
        article.date = parse_vlr_iso_datetime(
            (time_el.attributes.get("datetime") or "").strip(),
            source_tz=source_tz,
        )

    event_el = card.css_first("a.article-header-event")
    if event_el:
        article.event_name = event_el.text(strip=True)
        article.event_link = _resolve_link_url(event_el.attributes.get("href") or "")

    body_el = card.css_first("div.article-body")
    if body_el is not None:
        for el in body_el.css("span.article-ref-card"):
            el.decompose()
        for el in body_el.css("style"):
            el.decompose()
        text = body_el.text(strip=True, separator=" ")
        article.content = " ".join(text.split())
        article.content_md = html_to_markdown(body_el)

    return article


def html_to_markdown(body: Node) -> str:
    """Convert an article body subtree to Markdown.

    Handles the semantic elements used by vlr.gg articles: paragraphs,
    ``h1``-``h6`` headings, ``ul``/``ol`` lists (including nested lists),
    ``table`` (as a pipe table), links, ``strong``/``em`` emphasis,
    verbatim inline ``code`` spans, ``img``, and ``iframe`` Twitch clip
    embeds (rendered as a link). Decorative flags (``i.flag``), hover
    cards (``span.article-ref-card``), and ``style``/``script`` elements
    are dropped.

    Args:
        body: The ``div.article-body`` node (or any container of block
            elements) to convert.

    Returns:
        str: The body converted to Markdown, with blocks separated by
            blank lines. Returns an empty string for an empty body.

    Examples:
        >>> md = html_to_markdown(article_body)
        >>> md.startswith('[Americas Stage 2](https://www.vlr.gg/')
        True

    """
    blocks: list[str] = []
    for child in _direct_children(body):
        if child.tag == "-text":
            continue
        rendered = _render_block(child)
        if rendered:
            blocks.append(rendered.strip())
    return "\n\n".join(blocks)


def _direct_children(node: Node) -> list[Node]:
    """Return the immediate child nodes (elements and text) of ``node``."""
    return [child for child in node.iter(include_text=True) if child.parent == node]


def _render_block(node: Node) -> str:
    """Render a single block-level element (or inline element at block level)."""
    tag = node.tag.lower()

    if tag in {"p", "div", "section", "article", "span", "figure"}:
        return _render_flow(node)
    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        inner = _render_inline(node).strip()
        return f"{'#' * int(tag[1])} {inner}" if inner else ""
    if tag == "ul":
        return _render_list(node, ordered=False)
    if tag == "ol":
        return _render_list(node, ordered=True)
    if tag == "table":
        return _render_table(node)
    if tag == "blockquote":
        quoted = _render_flow(node)
        return "\n".join(f"> {line}" if line else ">" for line in quoted.splitlines())
    if tag == "pre":
        return f"```\n{node.text().strip()}\n```"
    if tag == "iframe":
        src = _attr(node, "src")
        return f"[Watch clip]({_clean_clip_url(src)})" if src else ""
    if tag == "img":
        return _render_image(node)
    if tag == "em":
        return f"*{_render_inline(node).strip()}*"
    if tag == "strong":
        return f"**{_render_inline(node).strip()}**"
    if tag == "hr":
        return "---"
    return _render_inline(node).strip()


def _render_flow(node: Node) -> str:
    """Render a container node, recursing when it holds block-level content."""
    if any(
        child.tag in _BLOCK_TAGS
        for child in _direct_children(node)
        if child.tag != "-text"
    ):
        return html_to_markdown(node)
    return _render_inline(node).strip()


def _render_list(node: Node, ordered: bool) -> str:
    """Render a ``ul`` or ``ol`` list, including nested lists."""
    marker = "1." if ordered else "-"
    lines: list[str] = []
    for child in _direct_children(node):
        if child.tag != "li":
            continue
        item = _render_list_item(child, marker)
        if item:
            lines.append(item)
    return "\n".join(lines)


def _render_list_item(node: Node, marker: str) -> str:
    """Render a single ``li``, flattening inline content onto the marker line.

    Nested ``ul``/``ol`` children are rendered underneath, with each of
    their lines indented by two spaces.
    """
    inline: list[str] = []
    sublists: list[str] = []
    for child in _direct_children(node):
        if child.tag == "-text":
            text = re.sub(r"\s+", " ", child.text())
            if text:
                inline.append(_escape_markdown(text))
            continue
        tag = child.tag.lower()
        if tag == "ul":
            sublists.append(_render_list(child, ordered=False))
        elif tag == "ol":
            sublists.append(_render_list(child, ordered=True))
        else:
            rendered = _render_inline_child(child)
            if rendered:
                inline.append(rendered)
    text = _collapse_inline(inline).strip()
    if not text and not sublists:
        return ""
    lines = [f"{marker} {text}".rstrip()] if text else []
    for sublist in sublists:
        lines.extend(f"  {line}" for line in sublist.splitlines())
    return "\n".join(lines)


def _collapse_inline(parts: list[str]) -> str:
    """Join rendered inline parts, collapsing runs of spaces to a single space.

    Backtick-delimited code spans are protected so their internal
    whitespace is preserved verbatim; ``br`` hard breaks (``"  \\n"``)
    are kept intact.
    """
    joined = "".join(parts)
    spans: list[str] = []

    def _protect(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return f"\x00{len(spans) - 1}\x00"

    protected = re.sub(r"(`+).*?\1", _protect, joined, flags=re.DOTALL)
    protected = re.sub(r" {2,}(?!\n)", " ", protected)
    for index, span in enumerate(spans):
        protected = protected.replace(f"\x00{index}\x00", span)
    return protected


def _render_table(node: Node) -> str:
    """Render a ``table`` as a pipe table with a header separator row."""
    rows: list[list[str]] = []
    for tr in node.css("tr"):
        cells = [
            _render_inline(cell).replace("|", "\\|").strip()
            for cell in tr.css("th, td")
        ]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    lines = [f"| {' | '.join(rows[0])} |"]
    lines.append(f"| {' | '.join('---' for _ in rows[0])} |")
    lines.extend(f"| {' | '.join(cell) or ' '} |" for cell in rows[1:])
    return "\n".join(lines)


def _render_inline(node: Node) -> str:
    """Render the inline children of ``node``."""
    parts: list[str] = []
    for child in _direct_children(node):
        if child.tag == "-text":
            text = re.sub(r"\s+", " ", child.text())
            if text:
                parts.append(_escape_markdown(text))
            continue
        rendered = _render_inline_child(child)
        if rendered:
            parts.append(rendered)
    return _collapse_inline(parts)


def _render_inline_child(node: Node) -> str:
    """Render a single inline child element, or ``""`` when it is dropped."""
    tag = node.tag.lower()
    classes = _classes(node)

    if tag in {"style", "script"} or "article-ref-card" in classes:
        return ""
    if tag == "i" and "flag" in classes:
        return ""
    if tag == "a":
        return _render_link(node)
    if tag in {"strong", "b"}:
        return f"**{_render_inline(node).strip()}**"
    if tag in {"em", "i"}:
        return f"*{_render_inline(node).strip()}*"
    if tag == "code":
        return _render_code(node)
    if tag == "br":
        return "  \n"
    if tag == "img":
        return _render_image(node)
    if tag == "iframe":
        src = _attr(node, "src")
        if src:
            return f"[Watch clip]({_clean_clip_url(src)})"
        return ""
    if tag == "ul":
        return _render_list(node, ordered=False)
    if tag == "ol":
        return _render_list(node, ordered=True)
    return _render_inline(node).strip()


def _render_code(node: Node) -> str:
    """Render an inline ``code`` element verbatim, preserving whitespace."""
    text = node.text(strip=True)
    if not text:
        return ""
    if "`" in text:
        return f"``{text}``"
    return f"`{text}`"


def _resolve_link_url(href: str) -> str:
    """Resolve a link href to a usable absolute URL.

    Absolute URLs (``http(s)://``, ``mailto:``, etc.), protocol-relative
    URLs (``//...``), and fragment-only anchors (``#...``) are returned
    unchanged. ``www.``-prefixed links are upgraded to ``https://``.
    Anything else (relative paths like ``/player/5132/mada`` or
    ``player/5132/mada``) is prefixed with the VLR base URL.
    """
    href = href.strip()
    if not href:
        return href
    if urlsplit(href).scheme:
        return href
    if href.startswith(("//", "#")):
        return href
    if href.startswith("www."):
        return f"https://{href}"
    return f"{BASE_URL}/{href.lstrip('/')}"


def _render_link(node: Node) -> str:
    """Render an ``a`` element as ``[text](href)`` with the href resolved."""
    href = _attr(node, "href")
    text = _render_inline(node).strip()
    if not href:
        return text
    return f"[{text or href}]({_resolve_link_url(href)})"


def _render_image(node: Node) -> str:
    """Render an ``img`` element as ``![alt](src)``."""
    src = _attr(node, "src")
    if not src:
        return ""
    alt = _attr(node, "alt")
    return f"![{alt}]({src})"


def _classes(node: Node) -> set[str]:
    """Return the whitespace-split class list of ``node``."""
    return set(((node.attributes or {}).get("class") or "").split())


def _clean_clip_url(src: str) -> str:
    """Convert a media embed URL into a directly openable watch URL.

    Recognises Twitch clip embeds, Twitch player/VOD embeds, YouTube
    (and youtube-nocookie) embeds, and Soop live/VOD embeds. Unrecognised
    URLs are returned unchanged, except that the ``parent`` query
    parameter is stripped from Twitch hosts.
    """
    src = html_module.unescape(src).strip()
    if not src:
        return src
    parts = urlsplit(src)
    netloc = (parts.hostname or "").lower()
    query = dict(parse_qsl(parts.query))

    if "twitch.tv" in netloc:
        if "clips.twitch.tv" in netloc:
            slug = query.get("clip")
            if slug:
                return f"https://clips.twitch.tv/{slug}"
        else:
            video = query.get("video")
            if video and parts.path in ("", "/"):
                return f"https://www.twitch.tv/videos/{video}"
        query.pop("parent", None)
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )

    if netloc in {
        "www.youtube.com",
        "youtube.com",
        "www.youtube-nocookie.com",
        "youtube-nocookie.com",
    }:
        segments = parts.path.split("/")
        if len(segments) >= 3 and segments[1] == "embed" and segments[2]:
            return f"https://www.youtube.com/watch?v={segments[2]}"
        if len(segments) >= 3 and segments[1] == "shorts" and segments[2]:
            return f"https://www.youtube.com/shorts/{segments[2]}"
        return src

    if netloc in {"play.sooplive.co.kr", "play.sooplive.com"} and parts.path.endswith(
        "/embed"
    ):
        watch_path = parts.path[: -len("/embed")] or "/"
        return urlunsplit((parts.scheme, parts.netloc, watch_path, "", ""))

    if netloc in {"vod.sooplive.com", "vod.sooplive.co.kr"}:
        match = re.fullmatch(r"/player/(\d+)(?:/embed)?/?", parts.path)
        if match:
            return f"https://www.sooplive.com/vod/{match.group(1)}"
        return src

    return src


def _attr(node: Node, name: str) -> str:
    """Return an unescaped, stripped attribute value."""
    return html_module.unescape((node.attributes or {}).get(name) or "").strip()


def _escape_markdown(text: str) -> str:
    """Escape Markdown-significant characters in inline text."""
    for char, escaped in _MD_ESCAPES.items():
        text = text.replace(char, escaped)
    return text
