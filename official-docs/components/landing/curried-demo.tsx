'use client';

import { useEffect, useState } from 'react';
import snapshot from './landing-snapshot.json';

const methods = [
  { call: '.info()', result: snapshot.player.name },
  { call: '.teams()', result: snapshot.player.team },
  { call: '.agents()', result: `${snapshot.player.agents[0].name} · ${snapshot.player.agents[0].share}` },
  { call: '.matches()', result: 'PlayerMatches' },
  { call: '.profile()', result: 'PlayerProfile' },
];

export function CurriedDemo() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused) return;

    const timer = window.setTimeout(
      () => setActive((current) => (current >= methods.length ? 0 : current + 1)),
      active >= methods.length ? 2600 : 850,
    );

    return () => window.clearTimeout(timer);
  }, [active, paused]);

  return (
    <div
      className="mt-6 overflow-hidden border border-white/10 bg-black"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="flex items-center justify-between border-b border-white/10 px-3.5 py-2">
        <span className="font-mono text-[12px] text-white/35">player.py</span>
        <span className="font-mono text-[12px] uppercase tracking-[0.12em] text-white/25">
          id bound once
        </span>
      </div>

      <div className="p-4 font-mono text-[12px]">
        <p className="whitespace-nowrap text-white/45">
          player = <span className="text-white/75">client.player({snapshot.player.id})</span>
        </p>

        <div className="mt-3 border-l border-white/10 pl-3">
          {methods.map((method, index) => {
            const done = active > index;
            const current = active === index;
            const revealed = done || current;

            return (
              <div
                key={method.call}
                className={`relative -mx-1 flex items-center justify-between gap-3 px-1 py-1.5 transition-colors duration-200 ${
                  current ? 'bg-white/[0.035]' : ''
                }`}
              >
                <span
                  aria-hidden="true"
                  className={`absolute -left-[17px] top-1/2 size-1 -translate-y-1/2 transition-colors duration-200 ${
                    done
                      ? 'bg-[#ff4655]'
                      : current
                        ? 'bg-[#ff4655]'
                        : 'bg-white/15'
                  }`}
                />
                <span
                  className={`transition-colors duration-200 ${
                    current ? 'text-[#ff8d97]' : done ? 'text-white/60' : 'text-white/25'
                  }`}
                >
                  player{method.call}
                </span>
                <span
                  className={`truncate text-right transition-all duration-200 ${
                    revealed ? 'translate-x-0 opacity-100' : 'translate-x-1 opacity-0'
                  } ${current ? 'text-white/80' : 'text-white/35'}`}
                >
                  {method.result}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-white/10 bg-white/[0.02] px-3.5 py-2 font-mono text-[12px] uppercase tracking-[0.1em] text-white/25">
        <span>{active >= methods.length ? 'all resolved' : 'resolving'}</span>
        <span>{Math.min(active, methods.length)} / {methods.length} methods</span>
      </div>
    </div>
  );
}
