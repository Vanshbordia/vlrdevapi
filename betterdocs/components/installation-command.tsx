"use client";

import { useState } from "react";

export function InstallationCommand({ command, label: _label }: { command: string; label: string }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(command);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="flex items-center justify-between gap-2 border border-input bg-zinc-100 dark:bg-neutral-900 px-4 py-2.5 font-mono text-sm text-zinc-900 dark:text-white w-full max-w-md hover:border-primary/50 transition-colors">
            <div className="flex items-center gap-2 overflow-hidden">
                <span className="select-none text-primary shrink-0">$</span>
                <span className="truncate">{command}</span>
            </div>
            <button
                onClick={handleCopy}
                className="ml-2 inline-flex h-7 w-7 shrink-0 items-center justify-center border border-input bg-zinc-100 dark:bg-neutral-900 hover:bg-zinc-200 dark:hover:bg-neutral-800 hover:text-accent-foreground focus:outline-none focus:ring-1 focus:ring-ring transition-colors"
                aria-label="Copy command"
            >
                {copied ? (
                    <CheckIcon className="h-3.5 w-3.5 text-green-500" />
                ) : (
                    <CopyIcon className="h-3.5 w-3.5" />
                )}
            </button>
        </div>
    );
}

function CopyIcon({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
        </svg>
    );
}

function CheckIcon({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <polyline points="20 6 9 17 4 12" />
        </svg>
    );
}
