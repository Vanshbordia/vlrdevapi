import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/**
 * @type {import('next').NextConfig}
 */
const config = {
  serverExternalPackages: ['typescript'],
  output: 'export',
  reactStrictMode: true,
  // Canonical URLs keep the trailing slash: `/about/`, not `/about`.
  //
  // This is the form Google has indexed for this site (Search Console shows
  // ~12,150 trailing-slash impressions vs ~446 for the slash-free form, and
  // 116 vs 2 clicks in AI Overviews). Switching the form would 308 every
  // indexed URL and require a full re-index.
  //
  // With `output: 'export'` this also means the build writes
  // `out/about/index.html`, which is what Cloudflare Pages serves at
  // `/about/`. The slash-free spelling still works: Cloudflare answers
  // `/about` with a 308 to `/about/`.
  trailingSlash: true,
};

export default withMDX(config);
