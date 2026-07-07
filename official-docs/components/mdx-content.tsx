import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'
import { highlightCode } from '@/lib/shiki'
import { CopyButton } from './copy-button'

function headingId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}

function extractText(node: React.ReactNode): string {
  if (typeof node === 'string') return node
  if (typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(extractText).join('')
  if (node && typeof node === 'object' && 'props' in node) {
    return extractText((node as { props: { children: React.ReactNode } }).props.children)
  }
  return ''
}

interface CodeBlockInfo {
  lang: string
  code: string
}

function extractCodeBlocks(content: string): CodeBlockInfo[] {
  const blocks: CodeBlockInfo[] = []
  const regex = /```(\w*)\n([\s\S]*?)```/g
  let match: RegExpExecArray | null
  while ((match = regex.exec(content)) !== null) {
    blocks.push({ lang: match[1] || 'text', code: match[2].replace(/\n$/, '') })
  }
  return blocks
}

interface MdxContentProps {
  content: string
}

export async function MdxContent({ content }: MdxContentProps) {
  const codeBlocks = extractCodeBlocks(content)
  const highlighted = await Promise.all(
    codeBlocks.map((b) =>
      highlightCode(b.code, b.lang).catch(() => ({ light: '', dark: '' }))
    )
  )

  let blockIndex = 0

  const components: Partial<Components> = {
    h2: ({ children, ...props }) => {
      const text = extractText(children)
      return <h2 id={headingId(text)} className="scroll-mt-28" {...props}>{children}</h2>
    },
    h3: ({ children, ...props }) => {
      const text = extractText(children)
      return <h3 id={headingId(text)} className="scroll-mt-28" {...props}>{children}</h3>
    },
    a: ({ href, children, ...props }) => {
      const isExternal = href?.startsWith('http')
      return (
        <a
          href={href}
          target={isExternal ? '_blank' : undefined}
          rel={isExternal ? 'noopener noreferrer' : undefined}
          className="text-fd-primary underline underline-offset-2 decoration-1 decoration-fd-primary/30 hover:decoration-fd-primary transition-[text-decoration-color]"
          {...props}
        >
          {children}
        </a>
      )
    },
    code: ({ className, children, ...props }) => {
      if (!className) {
        return (
          <code className="bg-muted px-1 py-0.5 text-sm font-normal text-foreground rounded-none" {...props}>
            {children}
          </code>
        )
      }
      return <>{children}</>
    },
    pre: ({ children, ...props }) => {
      const idx = blockIndex++
      const { light, dark } = highlighted[idx] ?? {}

      if (light) {
        return (
          <figure className="not-prose relative my-4 bg-fd-card rounded-xl border shadow-sm overflow-hidden text-sm" dir="ltr">
            <div className="text-[0.8125rem] py-3.5 overflow-auto max-h-[600px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-fd-ring">
              <pre className="min-w-full w-max *:flex *:flex-col">
                <div className="dark:hidden" dangerouslySetInnerHTML={{ __html: light }} />
                <div className="hidden dark:block" dangerouslySetInnerHTML={{ __html: dark }} />
              </pre>
            </div>
            <CopyButton code={codeBlocks[idx]?.code ?? ''} />
          </figure>
        )
      }

      return (
        <pre
          className="not-prose my-4 bg-fd-card rounded-xl border shadow-sm overflow-hidden text-sm text-[0.8125rem] p-3.5 overflow-x-auto"
          {...props}
        >
          {children}
        </pre>
      )
    },
  }

  return (
    <div className="prose prose-sm prose-neutral dark:prose-invert max-w-none prose-code:before:content-none prose-code:after:content-none prose-pre:!p-0 prose-pre:!bg-transparent prose-pre:!border-none prose-a:!font-normal prose-a:!no-underline [&_pre]:!bg-transparent [&_pre]:!p-0">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
