import Link from 'next/link';
import { ArrowUpRight } from 'lucide-react';
import { Reveal } from '@/components/landing/reveal';
import { getBlogEntries } from '@/lib/source';

/**
 * The three most recent blog posts.
 *
 * Keeps the landing page fresh and adds internal links into the blog, which
 * the landing page previously had none of.
 */
export function LatestPosts() {
  const posts = getBlogEntries().slice(0, 3);

  if (posts.length === 0) return null;

  return (
    <section className="border-b border-white/10">
      <div className="mx-auto w-full max-w-7xl px-5 py-20 sm:px-8 sm:py-24">
        <Reveal className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="font-mono text-[12px] uppercase tracking-[0.2em] text-fd-muted">
              From the blog
            </p>
            <h2 className="mt-4 text-3xl font-medium leading-[1.05] tracking-[-0.035em] text-white sm:text-4xl">
              Notes on building
              <br />
              <span className="text-fd-muted">with esports data.</span>
            </h2>
          </div>
          <Link
            href="/blog/"
            className="group inline-flex items-center gap-1.5 pb-1 text-[12.5px] font-medium text-white/60 transition-colors hover:text-white"
          >
            Read the blog
            <ArrowUpRight
              className="size-3.5 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </Link>
        </Reveal>

        <Reveal className="mt-9 grid gap-3 md:grid-cols-3">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={post.url}
              className="group relative flex h-full flex-col overflow-hidden border border-white/10 bg-fd-panel p-5 transition-colors hover:border-white/20"
            >
              <span
                aria-hidden="true"
                className="absolute inset-x-0 top-0 h-px origin-left scale-x-0 bg-fd-primary transition-transform duration-300 group-hover:scale-x-100"
              />
              <span className="font-mono text-[12px] uppercase tracking-[0.14em] text-fd-muted">
                {post.date}
              </span>
              <h3 className="mt-5 text-lg font-medium leading-snug tracking-tight text-white/85 transition-colors group-hover:text-white">
                {post.title}
              </h3>
              <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-fd-subtle">
                {post.description}
              </p>
              <span className="mt-auto inline-flex items-center gap-1.5 pt-6 text-[12px] font-medium text-fd-muted transition-colors group-hover:text-fd-primary">
                Read post
                <ArrowUpRight
                  className="size-3 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </span>
            </Link>
          ))}
        </Reveal>
      </div>
    </section>
  );
}
