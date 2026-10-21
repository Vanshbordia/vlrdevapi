'use client';

import { useEffect, useState } from 'react';

export function RateLimitDemo() {
  const [sent, setSent] = useState(0);
  const [queued, setQueued] = useState(false);

  useEffect(() => {
    if (sent < 3) {
      const timer = window.setTimeout(
        () => setSent((current) => current + 1),
        sent === 0 ? 550 : 340,
      );
      return () => window.clearTimeout(timer);
    }

    if (!queued) {
      const timer = window.setTimeout(() => setQueued(true), 340);
      return () => window.clearTimeout(timer);
    }

    const timer = window.setTimeout(() => {
      setSent(0);
      setQueued(false);
    }, 1900);

    return () => window.clearTimeout(timer);
  }, [sent, queued]);

  return (
    <div className="mt-6 border border-white/10 bg-black p-3.5">
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-[12px] uppercase tracking-[0.1em] text-white/30">
          1 second window
        </span>
        <span className="font-mono text-[12px] text-white/35">
          {sent} / 3 sent
        </span>
      </div>

      <div className="mt-3 grid grid-cols-4 gap-1.5">
        {['0.00', '0.33', '0.67'].map((time, index) => {
          const fired = sent > index;

          return (
            <div
              key={time}
              className={`relative h-14 overflow-hidden border transition-colors duration-300 ${
                fired ? 'border-[#ff4655]/35 bg-[#ff4655]/[0.08]' : 'border-white/10 bg-white/[0.02]'
              }`}
            >
              <span
                aria-hidden="true"
                className={`absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#ff4655]/35 to-[#ff4655]/5 transition-[height] duration-300 ${
                  fired ? 'h-full' : 'h-0'
                }`}
              />
              <span className="absolute inset-x-0 top-1.5 text-center font-mono text-[12px] text-white/30">
                {time}
              </span>
              <span
                className={`absolute inset-x-0 bottom-1.5 text-center font-mono text-[12px] uppercase tracking-[0.08em] transition-colors duration-300 ${
                  fired ? 'text-[#ff9aa2]' : 'text-white/15'
                }`}
              >
                {fired ? 'sent' : 'idle'}
              </span>
            </div>
          );
        })}

        <div
          className={`relative h-14 overflow-hidden border border-dashed transition-colors duration-300 ${
            queued
              ? 'border-[#ff4655]/40 bg-[#ff4655]/[0.06]'
              : 'border-white/10 bg-transparent'
          }`}
        >
          <span
            aria-hidden="true"
            className={`absolute inset-x-0 bottom-0 bg-[#ff4655]/10 transition-[height] duration-300 ${
              queued ? 'h-5' : 'h-0'
            }`}
          />
          <span className="absolute inset-x-0 top-1.5 text-center font-mono text-[12px] text-white/30">
            1.0
          </span>
          <span
            className={`absolute inset-x-0 bottom-1.5 text-center font-mono text-[12px] uppercase tracking-[0.08em] transition-colors duration-300 ${
              queued ? 'text-[#ff9aa2]' : 'text-white/15'
            }`}
          >
            {queued ? 'queued' : 'next'}
          </span>
        </div>
      </div>

      <div className="mt-2 flex justify-between font-mono text-[12px] text-white/20">
        <span>{queued ? 'window full' : 'window open'}</span>
        <span>{queued ? 'next slot · 1.0s' : '3 req / sec'}</span>
      </div>
    </div>
  );
}
