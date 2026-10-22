import { isValidElement, type ReactNode } from 'react';
import type { TOCItemType } from 'fumadocs-core/toc';

export interface TocItem {
  id: string;
  text: string;
  level: number;
}

/**
 * Flatten a heading title into plain text.
 *
 * fumadocs' `rehypeToc` exports every heading as a React node rather than a
 * string (`{ props: { children: 'Installation' } }`), because a heading may mix
 * inline markdown such as code or emphasis. Reading `title` as a string
 * therefore silently emptied the whole TOC.
 */
function toPlainText(node: ReactNode): string {
  if (node === null || node === undefined || typeof node === 'boolean') return '';
  if (typeof node === 'string') return node;
  if (typeof node === 'number') return String(node);
  if (Array.isArray(node)) return node.map(toPlainText).join('');
  if (isValidElement<{ children?: ReactNode }>(node)) return toPlainText(node.props.children);

  return '';
}

/**
 * Convert the TOC fumadocs produces (via the `rehypeToc` plugin that
 * fumadocs-mdx applies to every collection) into the flat shape the
 * marketing TOC nav renders.
 *
 * Only `h2`/`h3` are surfaced, matching the depth the nav indents for.
 */
export function toTocItems(toc: TOCItemType[] | undefined): TocItem[] {
  if (!toc) return [];

  return toc
    .filter((item) => item.depth >= 2 && item.depth <= 3)
    .map((item) => ({
      id: item.url.replace(/^#/, ''),
      text: toPlainText(item.title).trim(),
      level: item.depth,
    }))
    .filter((item) => item.text.length > 0);
}
