# VLRdevAPI Official Docs

Next.js static site for the [VLRdevAPI](https://vlrdevapi.pages.dev) Python SDK documentation — built with [Fumadocs](https://fumadocs.dev) and [Next.js](https://nextjs.org) (static export).

## Getting Started

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Build

```bash
npm run build
```

Outputs a static site to `out/` via `next export`.

## Project Structure

| Route | Description |
|---|---|
| `app/(home)/page.tsx` | Landing page |
| `app/(home)/blog/` | Blog listing + `[slug]` detail (TOC, CTA) |
| `app/(home)/guides/` | Guides listing + `[slug]` detail (TOC, CTA) |
| `app/(home)/faq/` | FAQ with accordion + JSON-LD |
| `app/(home)/changelog/` | Changelog with sticky timeline |
| `app/docs/[[...slug]]` | Fumadocs documentation pages |
| `app/opengraph-image.tsx` + per-route OG images | Route-level OG images via `next/og` |

### Content

- `content/docs/` — Fumadocs MDX source (sidebar-based)
- `content/blog/` — Blog posts (`.mdx` with frontmatter)
- `content/guides/` — Guide walkthroughs (`.mdx` with frontmatter)
- `lib/content.ts` — Build-time gray-matter parser for blog/guides

### Features

- **Blog / Guides**: MDX rendered with `react-markdown` + Shiki syntax highlighting + Fumadocs-style code blocks
- **FAQ**: 6 sections with 43 accordion items, IntersectionObserver text highlighting, FAQPage JSON-LD
- **Changelog**: Versioned entries with sticky sidebar timeline
- **JSON-LD**: Organization, WebSite, SoftwareApplication, TechArticle, BreadcrumbList, FAQPage, BlogPosting schemas
- **Fonts**: Geist (body via `next/font/google`), Articulat CF (headings via CSS `@font-face` from `public/fonts/`)
- **OG Images**: Route-specific generated images with embedded logo SVG
- **Sitemap**: Dynamic `sitemap.ts` covering docs, blog, guides, FAQ, changelog
- **Robots**: `robots.ts` allowing all crawlers

### Key Scripts

```bash
npm run dev       # Development server
npm run build     # Static export build + type check
npm run types:check  # TypeScript check only
```
