export const appName = 'VLRdevAPI';
export const docsRoute = '/docs';
export const docsImageRoute = '/og/docs';
export const docsContentRoute = '/llms.mdx/docs';

// Canonical site origin. Override at build time with NEXT_PUBLIC_SITE_URL;
// falls back to the production Pages domain instead of localhost.
export const siteUrl = (
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://vlrdevapi.pages.dev'
).replace(/\/+$/, '');

/**
 * Absolute canonical URL for a path, normalized to the enforced
 * trailing-slash form (next.config uses `trailingSlash: true`).
 */
export function canonicalUrl(path: string) {
  const withLeadingSlash = path.startsWith('/') ? path : `/${path}`;
  return `${siteUrl}${withLeadingSlash.endsWith('/') ? withLeadingSlash : `${withLeadingSlash}/`}`;
}

/**
 * Absolute URL for a static asset (image, file). Unlike {@link canonicalUrl}
 * this never appends a trailing slash.
 */
export function assetUrl(path: string) {
  return `${siteUrl}${path.startsWith('/') ? path : `/${path}`}`;
}

// fill this with your actual GitHub info, for example:
export const gitConfig = {
  user: 'vanshbordia',
  repo: 'vlrdevapi',
  branch: 'main',
};
