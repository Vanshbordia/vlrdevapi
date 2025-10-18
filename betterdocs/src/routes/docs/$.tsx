import { createFileRoute, notFound } from '@tanstack/react-router';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { createServerFn } from '@tanstack/react-start';
import { source } from '@/lib/source';
import type { PageTree } from 'fumadocs-core/server';
import { useMemo } from 'react';
import { docs } from '../../../source.generated';
import {
  DocsBody,
  DocsDescription,
  DocsPage,
  DocsTitle,
} from 'fumadocs-ui/page';
import defaultMdxComponents from 'fumadocs-ui/mdx';
import { createClientLoader } from 'fumadocs-mdx/runtime/vite';
import { baseOptions } from '@/lib/layout.shared';
import { LLMCopyButton, ViewOptions } from '@/components/page-actions';
import { SidebarFooterGithub } from '@/components/sidebar-footer-github';

export const Route = createFileRoute('/docs/$')({
  component: Page,
  loader: async ({ params }) => {
    const data = await loader({ data: params._splat?.split('/') ?? [] });
    await clientLoader.preload(data.path);
    return data;
  },
});

const loader = createServerFn({
  method: 'GET',
})
  .inputValidator((slugs: string[]) => slugs)
  .handler(async ({ data: slugs }) => {
    const page = source.getPage(slugs);
    if (!page) throw notFound();

    return {
      tree: source.pageTree as object,
      path: page.path,
    };
  });

const clientLoader = createClientLoader(docs.doc, {
  id: 'docs',
  component({ toc, frontmatter, default: MDX }) {
    return (
      <DocsPage toc={toc}>
        <DocsTitle>{frontmatter.title}</DocsTitle>
        <DocsDescription className='mb-1'>{frontmatter.description}</DocsDescription>
        <div className="flex flex-row gap-2 items-center border-b pt-2 pb-6">
          {/* Build Markdown URL for LLM endpoints */}
          {(() => {
            const mdxUrl = typeof window !== 'undefined'
              ? `/llms.mdx${window.location.pathname.replace(/^\/docs/, '')}.mdx`
              : '';
            return (
              <>
                <LLMCopyButton markdownUrl={mdxUrl} />
                <ViewOptions markdownUrl={mdxUrl} githubUrl="#" />
              </>
            );
          })()}
        </div>
        <DocsBody>
          <MDX
            components={{
              ...defaultMdxComponents,
            }}
          />
        </DocsBody>
      </DocsPage>
    );
  },
});

function Page() {
  const data = Route.useLoaderData();
  const Content = clientLoader.getComponent(data.path);
  const tree = useMemo(
    () => transformPageTree(data.tree as PageTree.Folder),
    [data.tree],
  );

  return (
    <DocsLayout 
      {...baseOptions()} 
      tree={tree}
    >
      {/* Inject GitHub icon inline with the Theme Toggle in the sidebar footer */}
      <SidebarFooterGithub />
      <Content />
    </DocsLayout>
  );
}

function transformPageTree(tree: PageTree.Folder): PageTree.Folder {
  function transform<T extends PageTree.Item | PageTree.Separator>(item: T) {
    if (typeof item.icon !== 'string') return item;

    return {
      ...item,
      icon: (
        <span
          dangerouslySetInnerHTML={{
            __html: item.icon,
          }}
        />
      ),
    };
  }

  return {
    ...tree,
    index: tree.index ? transform(tree.index) : undefined,
    children: tree.children.map((item) => {
      if (item.type === 'folder') return transformPageTree(item);
      return transform(item);
    }),
  };
}
