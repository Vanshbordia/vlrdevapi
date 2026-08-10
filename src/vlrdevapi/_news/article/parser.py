"""Parse full news article pages (``/{article_id}/<slug>``).

Articles on vlr.gg use semantic HTML (headings, paragraphs, lists, links,
emphasis, and Twitch clip embeds). The body is exposed both as plain text
and as a Markdown conversion that preserves that structure.
"""

import html as html_module
import logging
import re
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from selectolax.parser import HTMLParser, Node

from vlrdevapi._news.article.models import NewsArticle

logger = logging.getLogger(__name__)

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


def parse_news_article(html: HTMLParser) -> NewsArticle:
    """Parse a full news article page (``/{article_id}/<slug>``).

    Args:
        html: Parsed HTML document of an article page.

    Returns:
        NewsArticle: The article with ``id``, ``title``, ``author``,
        ``date``, ``event_name``, ``event_link``, ``content`` (plain
        text), and ``content_md`` (Markdown). Fields are empty when the
        page does not contain a recognisable article card.

    Examples:
        >>> article = parse_news_article(vlrdevapi_article_html)
        >>> article.author
        'jenopelle'
        >>> article.content_md.startswith('## 1. Gen.G (5-0)')
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
        dt_attr = (time_el.attributes.get("datetime") or "").strip()
        if dt_attr:
            try:
                article.date = datetime.fromisoformat(dt_attr).astimezone(UTC)
            except ValueError:
                logger.debug("Failed to parse news article date: %r", dt_attr)

    event_el = card.css_first("a.article-header-event")
    if event_el:
        article.event_name = event_el.text(strip=True)
        article.event_link = event_el.attributes.get("href") or ""

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
    ``h1``-``h6`` headings, ``ul``/``ol`` lists, links, ``strong``/``em``
    emphasis, ``img``, and ``iframe`` Twitch clip embeds (rendered as a
    link). Decorative flags (``i.flag``), hover cards
    (``span.article-ref-card``), and ``style``/``script`` elements are
    dropped.

    Args:
        body: The ``div.article-body`` node (or any container of block
            elements) to convert.

    Returns:
        str: The body converted to Markdown, with blocks separated by
            blank lines. Returns an empty string for an empty body.

    Examples:
        >>> md = html_to_markdown(article_body)
        >>> "## 1. Gen.G (5-0)" in md
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
    if any(child.tag in _BLOCK_TAGS for child in _direct_children(node) if child.tag != "-text"):
        return html_to_markdown(node)
    return _render_inline(node).strip()


def _render_list(node: Node, ordered: bool) -> str:
    """Render a ``ul`` or ``ol`` list."""
    marker = "1." if ordered else "-"
    lines: list[str] = []
    for child in _direct_children(node):
        if child.tag != "li":
            continue
        text = _render_inline(child).strip()
        if text:
            lines.append(f"{marker} {text}")
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

        tag = child.tag.lower()
        classes = _classes(child)

        if tag in {"style", "script"} or "article-ref-card" in classes:
            continue
        if tag == "i" and "flag" in classes:
            continue
        if tag == "a":
            parts.append(_render_link(child))
        elif tag in {"strong", "b"}:
            parts.append(f"**{_render_inline(child)}**")
        elif tag in {"em", "i"}:
            parts.append(f"*{_render_inline(child)}*")
        elif tag == "code":
            parts.append(f"`{_render_inline(child)}`")
        elif tag == "br":
            parts.append("  \n")
        elif tag == "img":
            rendered = _render_image(child)
            if rendered:
                parts.append(rendered)
        elif tag == "iframe":
            src = _attr(child, "src")
            if src:
                parts.append(f"[Watch clip]({_clean_clip_url(src)})")
        else:
            parts.append(_render_inline(child))
    return "".join(parts)


def _render_link(node: Node) -> str:
    """Render an ``a`` element as ``[text](href)``."""
    href = _attr(node, "href")
    text = _render_inline(node).strip()
    if not href:
        return text
    return f"[{text or href}]({href})"


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
    """Strip the ``parent`` query parameter from Twitch clip embed URLs."""
    parts = urlsplit(src)
    if "twitch.tv" not in parts.netloc:
        return src
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if k != "parent"])
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _attr(node: Node, name: str) -> str:
    """Return an unescaped, stripped attribute value."""
    return html_module.unescape((node.attributes or {}).get(name) or "").strip()


def _escape_markdown(text: str) -> str:
    """Escape Markdown-significant characters in inline text."""
    for char, escaped in _MD_ESCAPES.items():
        text = text.replace(char, escaped)
    return text
