export const appName = 'VLRdevAPI';
export const docsRoute = '/docs';
export const docsContentRoute = '/llms.mdx/docs';

// Canonical site origin. Override at build time with NEXT_PUBLIC_SITE_URL;
// falls back to the production Pages domain instead of localhost.
export const siteUrl = (
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://vlrdevapi.pages.dev'
).replace(/\/+$/, '');

/**
 * Absolute canonical URL for a path, normalised to the trailing-slash form
 * (`next.config` uses `trailingSlash: true`).
 *
 * The trailing slash is the form this site is indexed under, so it is also
 * the canonical form. The site root keeps its single slash.
 */
export function canonicalUrl(path: string) {
  const withLeadingSlash = path.startsWith('/') ? path : `/${path}`;
  const trimmed = withLeadingSlash.replace(/\/+$/, '');

  return `${siteUrl}${trimmed}/`;
}

/**
 * Strip a trailing slash from an internal path. The root path is preserved
 * as-is so it is never reduced to an empty string.
 */
export function stripTrailingSlash(path: string) {
  if (path === '/' || path === '') return path;
  return path.replace(/\/+$/, '');
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
