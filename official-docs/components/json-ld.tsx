/**
 * Render JSON-LD as a native script tag. Next.js recommends escaping `<` so
 * structured data cannot terminate the script element early.
 */
export function JsonLd({ data }: { data: unknown }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, '\\u003c'),
      }}
    />
  );
}
