import { createHighlighter } from 'shiki'

let highlighter: Awaited<ReturnType<typeof createHighlighter>> | null = null

async function getHighlighter() {
  if (!highlighter) {
    highlighter = await createHighlighter({
      langs: ['py', 'bash', 'ts', 'tsx', 'js', 'jsx', 'json', 'csv', 'xml', 'yaml', 'md'],
      themes: ['github-light', 'github-dark'],
    })
  }
  return highlighter
}

export async function highlightCode(code: string, lang: string): Promise<{ light: string; dark: string }> {
  const h = await getHighlighter()
  const light = h.codeToHtml(code, { lang, theme: 'github-light' })
  const dark = h.codeToHtml(code, { lang, theme: 'github-dark' })
  return { light, dark }
}
