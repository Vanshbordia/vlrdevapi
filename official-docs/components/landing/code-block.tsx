import type { ReactNode } from 'react';

const TOKEN_RE =
  /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(#.*$)|(\b(?:import|from|with|as|for|in|if|else|return|None|True|False|class|def|async|await|and|or|not)\b)|(\b\d+(?:\.\d+)?\b)|(\b[A-Za-z_]\w*(?=\())/g;

function highlight(line: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let cursor = 0;
  let index = 0;

  for (const match of line.matchAll(TOKEN_RE)) {
    const start = match.index ?? 0;
    if (start > cursor) {
      nodes.push(line.slice(cursor, start));
    }

    const [text, str, comment, keyword, number, fn] = match;
    const className = str
      ? 'text-[#a7d8a9]'
      : comment
        ? 'text-white/25'
        : keyword
          ? 'text-[#ff8fab]'
          : number
            ? 'text-[#f0c674]'
            : fn
              ? 'text-[#8ab4f8]'
              : undefined;

    nodes.push(
      <span key={`${index}-${start}`} className={className}>
        {text}
      </span>,
    );
    cursor = start + text.length;
    index += 1;
  }

  if (cursor < line.length) {
    nodes.push(line.slice(cursor));
  }

  return nodes;
}

export function CodeBlock({
  code,
  className = '',
  lineNumbers = true,
  animate = false,
}: {
  code: string;
  className?: string;
  lineNumbers?: boolean;
  animate?: boolean;
}) {
  const lines = code.replace(/\n$/, '').split('\n');

  return (
    <pre
      className={`overflow-x-auto p-4 font-mono text-[12.5px] leading-[1.8] text-white/75 ${className}`}
    >
      <code className="table w-full min-w-max border-collapse">
        {lines.map((line, i) => (
          <span
            key={i}
            className={`table-row ${animate ? 'landing-line' : ''}`}
            style={animate ? { animationDelay: `${i * 24}ms` } : undefined}
          >
            {lineNumbers ? (
              <span className="table-cell select-none pr-5 text-right text-white/20">
                {i + 1}
              </span>
            ) : null}
            <span className="table-cell whitespace-pre">
              {line.length > 0 ? highlight(line) : ' '}
            </span>
          </span>
        ))}
      </code>
    </pre>
  );
}
