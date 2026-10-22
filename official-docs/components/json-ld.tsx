/**
 * Render JSON-LD as native script tags.
 *
 * Each node is emitted as its own `<script>` element: schema.org structured
 * data in a single script must contain exactly one node. An array of nodes is
 * ignored by Google, so the FAQ and breadcrumb rich results on the "why"
 * pages were silently dropped before this was split.
 *
 * Next.js recommends escaping `<` so structured data cannot terminate the
 * script element early.
 */
export function JsonLd({ data }: { data: unknown | unknown[] }) {
  const nodes = Array.isArray(data) ? data : [data];

  return (
    <>
      {nodes.map((node, index) => (
        <script
          key={index}
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(node).replace(/</g, '\\u003c'),
          }}
        />
      ))}
    </>
  );
}
