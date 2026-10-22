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
        ? 'text-fd-muted'
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
      className={`overflow-x-auto p-4 font-mono text-[12.5px] leading-[1.8] text-white/75 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden ${className}`}
    >
      {/*
        A real table rather than `display: table` spans inside `<code>`.
        `<code>` may only contain phrasing content, and the layout hack breaks
        in forced-colours / high-contrast mode.
      */}
      <table className="w-full min-w-max border-collapse">
        <tbody>
          {lines.map((line, i) => (
            <tr
              key={i}
              className={animate ? 'landing-line' : undefined}
              style={animate ? { animationDelay: `${i * 24}ms` } : undefined}
            >
              {lineNumbers ? (
                <td className="select-none pr-5 text-right align-top text-fd-muted">
                  <span aria-hidden="true">{i + 1}</span>
                </td>
              ) : null}
              <td className="whitespace-pre align-top">
                <code>{line.length > 0 ? highlight(line) : ' '}</code>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </pre>
  );
}
