'use client';

import { useState } from 'react';
import { CopyButton } from './copy-button';

export function CopyCommand({
  command,
  className = '',
}: {
  command?: string;
  className?: string;
}) {
  const [manager, setManager] = useState<'uv' | 'pip'>('uv');

  const activeCommand = command
    ? command
    : manager === 'uv'
      ? 'uv add vlrdevapi'
      : 'pip install vlrdevapi';

  return (
    <div
      className={`inline-flex h-11 max-w-full items-center gap-2 border border-white/15 bg-white/[0.03] pl-2.5 pr-1.5 transition-colors hover:border-white/25 hover:bg-white/[0.06] ${className}`}
    >
      {!command && (
        <div className="flex items-center gap-1 border-r border-white/10 pr-2 font-mono text-[11px]">
          <button
            type="button"
            onClick={() => setManager('uv')}
            className={`px-1.5 py-0.5 transition-colors ${
              manager === 'uv'
                ? 'bg-fd-primary/20 font-semibold text-fd-primary'
                : 'text-white/40 hover:text-white/80'
            }`}
            aria-label="Use uv package manager"
          >
            uv
          </button>
          <button
            type="button"
            onClick={() => setManager('pip')}
            className={`px-1.5 py-0.5 transition-colors ${
              manager === 'pip'
                ? 'bg-fd-primary/20 font-semibold text-fd-primary'
                : 'text-white/40 hover:text-white/80'
            }`}
            aria-label="Use pip package manager"
          >
            pip
          </button>
        </div>
      )}

      <span aria-hidden="true" className="font-mono text-xs text-fd-primary">
        $
      </span>
      <code className="truncate font-mono text-[13px] text-white/80">{activeCommand}</code>
      <CopyButton
        value={activeCommand}
        label={`Copy command: ${activeCommand}`}
        className="ml-auto border-0 bg-transparent"
      />
    </div>
  );
}
