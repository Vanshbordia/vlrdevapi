import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

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

function readDir(dir: string): ContentPost[] {
  const fullPath = path.join(process.cwd(), 'content', dir)
  if (!fs.existsSync(fullPath)) return []

  const files = fs.readdirSync(fullPath).filter((f) => f.endsWith('.mdx'))

  return files
    .map((file) => {
      const raw = fs.readFileSync(path.join(fullPath, file), 'utf-8')
      const { data, content } = matter(raw)
      const slug = file.replace(/\.mdx$/, '')

      const rawDate = data.date
      const dateStr = rawDate instanceof Date
        ? rawDate.toISOString().split('T')[0]
        : String(rawDate ?? '')

      return {
        slug,
        title: data.title ?? slug,
        description: data.description ?? '',
        date: dateStr,
        author: data.author ?? 'RiftWatch',
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
