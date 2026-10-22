'use client';

import { useEffect, useState } from 'react';
import { useInView } from '@/components/use-in-view';

export function RateLimitDemo() {
  const [sent, setSent] = useState(0);
  const [queued, setQueued] = useState(false);
  // The demo loops forever, so it only runs while the card is on screen.
  const { ref, visible } = useInView<HTMLDivElement>();

  useEffect(() => {
    if (!visible) return;

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
  }, [sent, queued, visible]);

  return (
    <div ref={ref} className="mt-6 border border-white/10 bg-fd-canvas p-3.5">
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-[12px] uppercase tracking-[0.1em] text-fd-muted">
          1 second window
        </span>
        <span className="font-mono text-[12px] text-fd-muted">
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
                fired ? 'border-fd-primary/35 bg-fd-primary/[0.08]' : 'border-white/10 bg-white/[0.02]'
              }`}
            >
              <span
                aria-hidden="true"
                className={`absolute inset-x-0 bottom-0 bg-gradient-to-t from-fd-primary/35 to-fd-primary/5 transition-[height] duration-300 ${
                  fired ? 'h-full' : 'h-0'
                }`}
              />
              <span className="absolute inset-x-0 top-1.5 text-center font-mono text-[12px] text-fd-muted">
                {time}
              </span>
              <span
                className={`absolute inset-x-0 bottom-1.5 text-center font-mono text-[12px] uppercase tracking-[0.08em] transition-colors duration-300 ${
                  fired ? 'text-fd-primary' : 'text-fd-muted'
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
              ? 'border-fd-primary/40 bg-fd-primary/[0.06]'
              : 'border-white/10 bg-transparent'
          }`}
        >
          <span
            aria-hidden="true"
            className={`absolute inset-x-0 bottom-0 bg-fd-primary/10 transition-[height] duration-300 ${
              queued ? 'h-5' : 'h-0'
            }`}
          />
          <span className="absolute inset-x-0 top-1.5 text-center font-mono text-[12px] text-fd-muted">
            1.0
          </span>
          <span
            className={`absolute inset-x-0 bottom-1.5 text-center font-mono text-[12px] uppercase tracking-[0.08em] transition-colors duration-300 ${
              queued ? 'text-fd-primary' : 'text-fd-muted'
            }`}
          >
            {queued ? 'queued' : 'next'}
          </span>
        </div>
      </div>

      <div className="mt-2 flex justify-between font-mono text-[12px] text-fd-muted">
        <span>{queued ? 'window full' : 'window open'}</span>
        <span>{queued ? 'next slot · 1.0s' : '3 req / sec'}</span>
      </div>
    </div>
  );
}
