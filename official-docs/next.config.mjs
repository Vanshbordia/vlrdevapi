import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  serverExternalPackages: ['typescript'],
  output: 'export',
  reactStrictMode: true,
  trailingSlash: true,
  async rewrites() {
    return [
      {
        source: '/docs/:path*.mdx',
        destination: '/llms.mdx/docs/:path*',
      },
      {
        source: '/blog/:slug.mdx',
        destination: '/llms.mdx/blog/:slug/content.md',
      },
      {
        source: '/guides/:slug.mdx',
        destination: '/llms.mdx/guides/:slug/content.md',
      },
    ];
  },
};

export default withMDX(config);
