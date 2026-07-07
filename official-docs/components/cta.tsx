'use client'

import Link from 'next/link'
import { useState } from 'react'

function CopyBtn({ text, label, icon }: { text: string; label: string; icon: React.ReactNode }) {
  const [copied, setCopied] = useState(false)

  return (
    <button
      type="button"
      onClick={() => {
        navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
      }}
      className="inline-flex h-10 items-center gap-2 border border-border bg-background px-5 text-sm font-medium tracking-tight text-foreground transition-all hover:bg-muted"
    >
      {icon}
      {copied ? 'Copied!' : label}
    </button>
  )
}

interface CtaProps {
  title?: string
  description?: string
  docsLabel?: string
  docsHref?: string
}

export function CtaSection({
  title = 'Ready to build with VLRdevAPI?',
  description = 'Install the Python SDK and start fetching Valorant esports data in minutes. No API key required.',
  docsLabel = 'Read the Docs',
  docsHref = '/docs',
}: CtaProps) {
  return (
    <section className="mt-16 md:mt-20">
      <div className="relative overflow-hidden border border-border bg-gradient-to-br from-fd-primary/5 via-transparent to-fd-primary/[0.02] px-6 py-10 md:px-10 md:py-12">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 size-40 rounded-full bg-fd-primary/10 blur-3xl" />
        <div className="relative z-10">
          <div className="flex items-start gap-4">
            <div className="hidden shrink-0 sm:block">
              <div className="flex size-10 items-center justify-center border border-fd-primary/20 bg-fd-primary/10">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-fd-primary"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              </div>
            </div>
            <div>
              <h2 className="text-xl font-bold tracking-tight text-foreground md:text-2xl">
                {title}
              </h2>
              <p className="mt-2 max-w-lg text-sm leading-relaxed text-muted-foreground">
                {description}
              </p>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <CopyBtn
              text="pip install vlrdevapi"
              label="pip install vlrdevapi"
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>}
            />
            <CopyBtn
              text="uv add vlrdevapi"
              label="uv add vlrdevapi"
              icon={<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>}
            />
            <Link
              href={docsHref}
              className="inline-flex h-10 items-center gap-2 bg-foreground px-5 text-sm font-medium tracking-tight text-background transition-all hover:brightness-125"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
              {docsLabel}
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}
