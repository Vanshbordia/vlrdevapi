import type { Metadata, ResolvingMetadata } from 'next';
import { canonicalUrl } from './shared';
import { project } from './project';

type TwitterMetadata = NonNullable<Metadata['twitter']>;

/**
 * The Open Graph fields a page may override.
 *
 * Next's own `Metadata['openGraph']` is a discriminated union, so a caller
 * that only wants to add `publishedTime` would also have to repeat
 * `type: 'article'`. This is the flat subset we actually use; the object is
 * cast back to Next's type when the metadata is built.
 */
export interface OpenGraphOverrides {
  title?: string;
  description?: string;
  url?: string;
  siteName?: string;
  locale?: string;
  determiner?: string;
  // Article fields
  publishedTime?: string;
  modifiedTime?: string;
  authors?: string | URL | (string | URL)[] | null;
  section?: string | null;
  tags?: string | null;
}

interface PageMetadataOptions {
  title: string;
  description: string;
  path: string;
  type?: 'website' | 'article';
  keywords?: string[];
  openGraph?: OpenGraphOverrides;
  twitter?: TwitterMetadata;
}

/**
 * Turn a `YYYY-MM-DD` date string into a full ISO 8601 timestamp.
 *
 * `article:published_time` and schema.org `datePublished` want a datetime,
 * not a bare date. The date is anchored to midnight UTC so the value is
 * stable regardless of the machine that builds the site.
 */
export function toIsoDateTime(date: string): string {
  const parsed = new Date(`${date}T00:00:00Z`);

  if (Number.isNaN(parsed.getTime())) return date;

  return parsed.toISOString();
}

/**
 * Build page metadata with a consistent canonical URL, Open Graph payload, and
 * Twitter card.
 *
 * Next.js replaces the `openGraph` and `twitter` objects wholesale when a page
 * defines them, so every field has to be restated here - otherwise a page
 * would silently lose `og:site_name` and `og:type`. Individual pages can
 * still override any field.
 *
 * The Open Graph image is **not** set here: it comes from the
 * `opengraph-image` file convention, which Next injects automatically with the
 * right dimensions, type and alt text.
 */
export function createPageMetadata({
  title,
  description,
  path,
  type = 'website',
  keywords,
  openGraph,
  twitter,
}: PageMetadataOptions): Metadata {
  const url = canonicalUrl(path);
  const socialTitle = `${title} | ${project.name}`;

  return {
    title,
    description,
    ...(keywords?.length ? { keywords } : {}),
    alternates: { canonical: url },
    openGraph: {
      type,
      siteName: project.name,
      locale: 'en_US',
      url,
      title: socialTitle,
      description,
      ...openGraph,
    } as Metadata['openGraph'],
    twitter: {
      card: 'summary_large_image',
      title: socialTitle,
      description,
      ...twitter,
    },
  };
}

/**
 * The Open Graph image of a route.
 *
 * Next resolves the `opengraph-image` file convention into the route's
 * metadata and generates the URL for it, so the only place that gets to see
 * that URL is `generateMetadata`. The page body needs the same URL for its
 * JSON-LD, so it is handed over through a per-route promise.
 */
interface OgImageSlot {
  promise: Promise<string | undefined>;
  resolve: (url: string | undefined) => void;
}

const ogImageSlots = new Map<string, OgImageSlot>();

function ogImageSlot(key: string): OgImageSlot {
  const existing = ogImageSlots.get(key);
  if (existing) return existing;

  let resolve!: (url: string | undefined) => void;
  const promise = new Promise<string | undefined>((r) => {
    resolve = r;
  });
  const created: OgImageSlot = { promise, resolve };
  ogImageSlots.set(key, created);

  return created;
}

/**
 * Read the Open Graph image URL of a route.
 *
 * `generateMetadata` publishes the URL through {@link resolveOgImage}; this is
 * the matching read for the page body. The promise resolves as soon as the
 * metadata has been resolved, so the page never has to wait on the network.
 */
export function getOgImage(key: string): Promise<string | undefined> {
  return ogImageSlot(key).promise;
}

/**
 * Publish the Open Graph image URL of a route.
 *
 * `parent` is the metadata Next has already resolved for the route and it
 * contains the `og:image` URL produced by the `opengraph-image` file
 * convention.
 */
export async function resolveOgImage(
  key: string,
  parent: ResolvingMetadata,
): Promise<string | undefined> {
  const images = (await parent).openGraph?.images;
  const first = Array.isArray(images) ? images[0] : images;
  const url = imageUrl(first);

  ogImageSlot(key).resolve(url);

  return url;
}

/**
 * The URL of a resolved Open Graph image.
 *
 * Next resolves the image of the `opengraph-image` file convention into
 * either a plain URL string or an object with a `url` property.
 */
function imageUrl(image: unknown): string | undefined {
  if (typeof image === 'string') return image;
  if (image instanceof URL) return image.toString();
  if (image && typeof image === 'object' && 'url' in image) {
    const { url } = image as { url?: string | URL };
    if (typeof url === 'string') return url;
    if (url instanceof URL) return url.toString();
  }

  return undefined;
}
