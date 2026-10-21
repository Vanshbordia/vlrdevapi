'use client';

import { useEffect, useState } from 'react';

/**
 * Track which element is currently being read. The active section is the last
 * one whose top edge has passed the sticky-header offset (or the final section
 * when the page is scrolled to the bottom).
 */
export function useActiveId(ids: string[], offset = 128) {
  const [activeId, setActiveId] = useState(ids[0] ?? '');
  const key = ids.join('|');

  useEffect(() => {
    const currentIds = key ? key.split('|') : [];
    const elements = currentIds
      .map((id) => document.getElementById(id))
      .filter((element): element is HTMLElement => element !== null);

    if (elements.length === 0) return;

    let frame = 0;

    const update = () => {
      frame = 0;

      let next = currentIds[0];
      for (const element of elements) {
        if (element.getBoundingClientRect().top <= offset) {
          next = element.id;
        } else {
          break;
        }
      }

      const atBottom =
        window.scrollY + window.innerHeight >=
        document.documentElement.scrollHeight - 4;
      if (atBottom) {
        next = currentIds[currentIds.length - 1];
      }

      setActiveId((current) => (current === next ? current : next));
    };

    const onScroll = () => {
      if (frame) return;
      frame = window.requestAnimationFrame(update);
    };

    frame = window.requestAnimationFrame(update);
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    window.addEventListener('hashchange', onScroll);

    return () => {
      if (frame) window.cancelAnimationFrame(frame);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      window.removeEventListener('hashchange', onScroll);
    };
  }, [key, offset]);

  return ids.includes(activeId) ? activeId : (ids[0] ?? '');
}
