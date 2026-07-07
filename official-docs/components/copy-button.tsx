'use client'

import { useState } from 'react'

export function CopyButton({ code, className = '' }: { code: string; className?: string }) {
  const [copied, setCopied] = useState(false)

  return (
    <button
      type="button"
      onClick={() => {
        navigator.clipboard.writeText(code)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
      }}
      className={`absolute top-3 right-3 z-10 inline-flex size-7 items-center justify-center backdrop-blur-lg rounded-lg text-fd-muted-foreground hover:text-fd-accent-foreground transition-colors data-checked:text-fd-accent-foreground ${className}`}
      data-checked={copied || undefined}
      aria-label={copied ? 'Copied' : 'Copy code'}
    >
      {copied ? (
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
      )}
    </button>
  )
}
