import type { Metadata } from 'next'
import Link from 'next/link'
import { getBlogPosts } from '@/lib/content'

export const metadata: Metadata = {
  title: 'Blog',
  description: 'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Blog',
  name: 'VLRdevAPI Blog',
  description: 'News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.',
  url: 'https://vlrdevapi.pages.dev/blog/',
  publisher: {
    '@type': 'Organization',
    name: 'RiftWatch',
    url: 'https://riftwatch.org',
  },
}

export default function BlogPage() {
  const posts = getBlogPosts()

  return (
    <main className="flex-1">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c'),
        }}
      />
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 pt-28 pb-16 md:pt-36 md:pb-20">
          <h1 className="font-heading text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl md:text-[3rem]">
            Blog
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
            News, tutorials, and deep dives on building with the VLRdevAPI Python SDK for Valorant esports.
          </p>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-7xl px-6 py-16 md:py-20">
          {posts.length === 0 ? (
            <p className="text-sm text-muted-foreground">No posts yet.</p>
          ) : (
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {posts.map((post) => (
                <Link
                  key={post.slug}
                  href={`/blog/${post.slug}`}
                  className="group flex flex-col border border-border bg-background p-6 transition-all hover:border-fd-primary/50"
                >
                  <time className="text-xs text-muted-foreground">{post.date}</time>
                  <h2 className="mt-2 text-base font-bold tracking-tight text-foreground group-hover:text-fd-primary transition-colors">
                    {post.title}
                  </h2>
                  <p className="mt-2 text-sm leading-snug text-muted-foreground line-clamp-3">
                    {post.description}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  )
}
