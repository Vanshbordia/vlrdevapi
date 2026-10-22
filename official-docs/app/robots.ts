import type { MetadataRoute } from 'next';
import { siteUrl } from '@/lib/shared';

/**
 * `robots.txt` is generated rather than a static file so the sitemap URL
 * always matches the configured origin (`NEXT_PUBLIC_SITE_URL`).
 */
export const dynamic = 'force-static';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
      },
      // AI crawlers and assistants are explicitly allowed. The policy is the
      // same as the `*` rule, but listing them keeps the intent unambiguous
      // for agents that read their own section.
      ...[
        'GPTBot',
        'OAI-SearchBot',
        'ChatGPT-User',
        'PerplexityBot',
        'Perplexity-User',
        'ClaudeBot',
        'Claude-User',
        'Claude-SearchBot',
        'anthropic-ai',
        'Googlebot',
        'Google-Extended',
        'Google-CloudVertexBot',
        'Applebot',
        'Applebot-Extended',
        'CCBot',
        'Bytespider',
        'Amazonbot',
        'meta-externalagent',
        'MistralAI-User',
        'cohere-ai',
        'DuckAssistBot',
        'YouBot',
      ].map((userAgent) => ({ userAgent, allow: '/' })),
    ],
    sitemap: `${siteUrl}/sitemap.xml`,
    host: siteUrl,
  };
}
