import type { ReactNode } from 'react';

/**
 * Prose styling shared by the blog and guide articles.
 *
 * The class list used to be duplicated verbatim in both article routes.
 */
export function ArticleBody({ children }: { children: ReactNode }) {
  return (
    <div className="article-prose prose prose-invert max-w-none prose-headings:scroll-mt-24 prose-headings:font-medium prose-headings:tracking-tight prose-h2:mt-12 prose-h2:text-2xl prose-h2:text-white prose-h3:text-lg prose-h3:text-white/90 prose-p:text-white/65 prose-p:leading-relaxed prose-li:text-white/65 prose-li:leading-relaxed prose-strong:text-white/85 prose-a:text-fd-primary prose-a:font-normal [&_h2_a]:!text-inherit [&_h3_a]:!text-inherit [&_h4_a]:!text-inherit prose-a:no-underline hover:prose-a:underline prose-code:text-fd-primary prose-code:before:content-none prose-code:after:content-none prose-pre:!border prose-pre:!border-white/10 prose-pre:!bg-fd-panel prose-pre:!p-0 prose-blockquote:border-fd-primary/50 prose-blockquote:text-white/55 prose-hr:border-white/10 prose-table:text-white/65 prose-th:text-white/80 prose-td:border-white/10 [&_pre]:!bg-fd-panel [&_figure.shiki]:!my-6 [&_figure.shiki]:!rounded-none [&_figure.shiki]:!border-white/10 [&_figure.shiki]:!bg-fd-panel [&_figure.shiki]:!shadow-none">
      {children}
    </div>
  );
}
