import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'

export interface ContentMeta {
  slug: string
  title: string
  description: string
  date: string
  author: string
}

export interface ContentPost extends ContentMeta {
  content: string
}

function parseFrontmatter(raw: string): { data: Record<string, unknown>; content: string } {
  const match = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/.exec(raw)
  if (!match) return { data: {}, content: raw }

  const data = (yaml.load(match[1]) ?? {}) as Record<string, unknown>
  return { data, content: match[2] }
}

function readDir(dir: string): ContentPost[] {
  const fullPath = path.join(process.cwd(), 'content', dir)
  if (!fs.existsSync(fullPath)) return []

  const files = fs.readdirSync(fullPath).filter((f) => f.endsWith('.mdx'))

  return files
    .map((file) => {
      const raw = fs.readFileSync(path.join(fullPath, file), 'utf-8')
      const { data, content } = parseFrontmatter(raw)
      const slug = file.replace(/\.mdx$/, '')

      const rawDate = data.date
      const dateStr = rawDate instanceof Date
        ? rawDate.toISOString().split('T')[0]
        : String(rawDate ?? '')

      return {
        slug,
        title: typeof data.title === 'string' ? data.title : slug,
        description: typeof data.description === 'string' ? data.description : '',
        date: dateStr,
        author: typeof data.author === 'string' ? data.author : 'RiftWatch',
        content,
      }
    })
    .sort((a, b) => b.date.localeCompare(a.date))
}

export function getBlogPosts(): ContentPost[] {
  return readDir('blog')
}

export function getBlogPost(slug: string): ContentPost | undefined {
  return getBlogPosts().find((p) => p.slug === slug)
}

export function getGuides(): ContentPost[] {
  return readDir('guides')
}

export function getGuide(slug: string): ContentPost | undefined {
  return getGuides().find((p) => p.slug === slug)
}
