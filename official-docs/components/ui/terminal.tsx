'use client';

import { useEffect, useRef, useState } from 'react';

interface TerminalProps {
  commands: string[];
  outputs?: Record<number, string[]>;
  typingSpeed?: number;
  delayBetweenCommands?: number;
}

interface DisplayLine {
  type: 'command' | 'output' | 'blank';
  text: string;
}

export function Terminal({
  commands,
  outputs = {},
  typingSpeed = 45,
  delayBetweenCommands = 1000,
}: TerminalProps) {
  const [lines, setLines] = useState<DisplayLine[]>([]);
  const [typing, setTyping] = useState('');
  const [showCursor, setShowCursor] = useState(true);
  const doneRef = useRef(false);

  useEffect(() => {
    if (doneRef.current) return;

    let cmdIdx = 0;
    let charIdx = 0;
    let timer: ReturnType<typeof setTimeout>;

    const typeNext = () => {
      if (cmdIdx >= commands.length) {
        doneRef.current = true;
        return;
      }

      const cmd = commands[cmdIdx];

      if (charIdx < cmd.length) {
        charIdx++;
        setTyping(cmd.slice(0, charIdx));
        timer = setTimeout(typeNext, typingSpeed);
        return;
      }

      // Done typing this command
      const outLines = (outputs[cmdIdx] || []).map((t) => ({ type: 'output' as const, text: t }));
      setLines((prev) => [...prev, { type: 'command', text: cmd }, ...outLines]);
      setTyping('');
      charIdx = 0;
      cmdIdx++;

      timer = setTimeout(typeNext, delayBetweenCommands);
    };

    timer = setTimeout(typeNext, delayBetweenCommands);

    return () => clearTimeout(timer);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cursor blink
  useEffect(() => {
    const id = setInterval(() => setShowCursor((v) => !v), 530);
    return () => clearInterval(id);
  }, []);

  // Auto-scroll
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [lines, typing]);

  return (
    <div ref={containerRef} className="w-full overflow-hidden rounded-xl border border-border/60 bg-[#0a0a0a] font-mono text-[13px] leading-[1.7] shadow-2xl shadow-black/20">
      <div className="flex items-center gap-2 border-b border-border/40 px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-[#ff5f57]" />
        <span className="h-3 w-3 rounded-full bg-[#febc2e]" />
        <span className="h-3 w-3 rounded-full bg-[#28c840]" />
        <span className="ml-3 text-[11px] font-medium text-white/30 tracking-wide">vlrdevapi</span>
      </div>

      <div className="p-5 pt-4">
        {lines.map((line, i) => {
          if (line.type === 'blank') {
            return <div key={i} className="h-[1.7em]" />;
          }
          if (line.type === 'command') {
            return (
              <div key={i} className="flex">
                <span className="mr-2 text-fd-primary/80 select-none">$</span>
                <span className="text-white/90">{line.text}</span>
              </div>
            );
          }
          return (
            <div key={i} className="flex">
              <span className="text-white/40">{line.text}</span>
            </div>
          );
        })}

        {typing && (
          <div className="flex items-center">
            <span className="mr-2 text-fd-primary/80 select-none">$</span>
            <span className="text-white/90">{typing}</span>
            <span
              className={`ml-[1px] inline-block w-[7px] h-[16px] bg-fd-primary/80 transition-opacity duration-100 ${
                showCursor ? 'opacity-100' : 'opacity-0'
              }`}
            />
          </div>
        )}

        {!typing && !doneRef.current && (
          <div className="flex items-center">
            <span className="mr-2 text-fd-primary/80 select-none">$</span>
            <span
              className={`inline-block w-[7px] h-[16px] bg-fd-primary/80 transition-opacity duration-100 ${
                showCursor ? 'opacity-100' : 'opacity-0'
              }`}
            />
          </div>
        )}
      </div>
    </div>
  );
}
